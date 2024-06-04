import asyncio
import asyncio.tasks
from typing import Optional, TypeVar

import httpx

import atopile.config
import atopile.errors
import atopile.front_end
import atopile.instance_methods
from atopile.address import AddrStr
from atopile.components import server_api
from atopile.front_end import RangedValue
from atopile.components.properties import MissingData

T = TypeVar("T")
_known_types = {}

def _know_type(func: T) -> T:
    _known_types[func.__name__] = func
    return func


def find_components_from_abstract(build_ctx: atopile.config.BuildContext):
    asyncio.run(_find_components(build_ctx))


async def _find_components(build_ctx: atopile.config.BuildContext):
    async with httpx.AsyncClient() as client, asyncio.TaskGroup() as g:
        components = filter(
            atopile.instance_methods.match_components,
            atopile.instance_methods.all_descendants(build_ctx.entry)
        )
        for component in components:
            # This isn't an abstract component anymore
            if atopile.instance_methods.get_data(component, "mpn", None) is not None:
                continue

            abstract_type = atopile.instance_methods.get_data(component, "__type__")

            if abstract_type not in _known_types:
                raise atopile.errors.AtoError(f"Unknown component type: {abstract_type}")

            component_func = _known_types[abstract_type]
            g.create_task(component_func(component, client))


class NoMatchingComponent(atopile.errors.AtoError):
    """
    Raised when there's no component matching the given parameters in jlc_parts.csv
    """

    title = "No component matches parameters"


def _package(component: AddrStr) -> Optional[list[str]]:
    # Make sure we don't have conflicting package and footprint assigned
    footprint = atopile.instance_methods.get_data(component, "footprint", None)
    if footprint is None:
        package_from_footprint = None

    # This is a hack to convert existing C0603 to 0603 etc...
    elif footprint[0] == "R" or footprint[0] == "C":
        package_from_footprint = footprint[1:]

    # Get a package spec'd in the source code
    package = atopile.instance_methods.get_data(component, "package", None)

    if package is not None and package_from_footprint is not None:
        if package != package_from_footprint:
            raise atopile.errors.AtoError(
                f"Conflicting package and footprint: {package} and {footprint}",
                addr=component
            )
    elif package is None:
        package = package_from_footprint

    return [package] if package is not None else None


def _to(value: Optional[RangedValue], to: str) -> Optional[RangedValue]:
    if value is None:
        return None

    if not isinstance(value, RangedValue):
        raise atopile.errors.AtoTypeError(f"Expected a physical value, got {value}")

    return value.to(to)


def _get_value(component: AddrStr, key: str, to: Optional[str] = None) -> Optional[RangedValue | str]:
    assignments = atopile.instance_methods.get_assignments(component, key)
    if assignments[0].value is None:
        raise MissingData(f"No '{key}' assigned for $addr", addr=component)

    if assignments[0].value is atopile.front_end.AtoAny:
        return None  # No constraints on this value

    try:
        return _to(assignments[0].value, to)
    except atopile.errors.AtoTypeError as ex:
        ex.set_src_from_ctx(assignments[0].src_ctx)
        raise


async def _do_post(extension: str, request, client: httpx.AsyncClient) -> httpx.Response:
    url = atopile.config.get_project_context().config.services.components + "/v2/find" + extension

    try:
        response = await client.post(url, json=request.model_dump(), timeout=10)
        response.raise_for_status()

    # FIXME: this error handling should be way better
    except httpx.HTTPStatusError as ex:
        if response.status_code == 404:
            raise atopile.errors.AtoInfraError(
                "Could not connect to server. Check internet, or please try again later!"
            ) from ex
        if response.status_code == 500:
            if response.json()["error"] == "no_matching_component":
                raise NoMatchingComponent(
                    # FIXME: add useful information here
                    "No component matches parameters",
                ) from ex

        raise atopile.errors.AtoInfraError(repr(ex)) from ex

    return response


@_know_type
async def resistor(component: AddrStr, client: httpx.AsyncClient):
    value_ohms = _get_value(component, "value", "ohms")
    rated_power = _get_value(component, "rated_power", "watts")
    rated_temp = _get_value(component, "rated_temp", "celsius")

    # Make the request
    request = server_api.ResistorInput(
        mpn=None,
        package=_package(component),
        resistance_ohms_min=value_ohms.min_val if value_ohms is not None else None,
        resistance_ohms_max=value_ohms.max_val if value_ohms is not None else None,
        rated_power_watts=rated_power.max_val if rated_power is not None else None,
        rated_temp_celsius_min=rated_temp.min_val if rated_temp is not None else None,
        rated_temp_celsius_max=rated_temp.max_val if rated_temp is not None else None,
    )

    response = server_api.ResistorOutput(**(await _do_post("/resistor", request, client)).json())

    def _set(key, value):
        atopile.instance_methods.set_data(component, key=key, value=value)

    # Update the component
    _set("mpn", response.mpn)
    _set("package", response.package)
    _set("rated_power", RangedValue(response.rated_power_watts, unit="watts"))
    _set("rated_temp", RangedValue(response.rated_temp_celsius_min, response.rated_temp_celsius_max, "celsius"))
