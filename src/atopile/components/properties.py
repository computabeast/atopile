import logging
from functools import cache
from pathlib import Path

import atopile.config
import atopile.errors
import atopile.front_end
from atopile import address, instance_methods
from atopile.address import AddrStr

log = logging.getLogger(__name__)


def get_mpn(addr: AddrStr) -> str:
    """
    Return the MPN for a component
    """
    return instance_methods.get_data(addr, "mpn")


def get_user_facing_value(addr: AddrStr) -> str:
    """
    Return a "value" of a component we can slap in things like
    the BoM and netlist. Doesn't need to be perfect, just
    something to look at.
    """
    return str(instance_methods.get_data(addr, "value", "?"))


# Footprints come from the users' code, so we reference that directly
@cache
def get_footprint(addr: AddrStr) -> str:
    """
    Return the footprint for a component
    """
    try:
        return instance_methods.get_data(addr, "footprint")
    except KeyError as ex:
        raise MissingData(
            "$addr has no footprint", title="No footprint", addr=addr
        ) from ex


class DesignatorManager:
    """
    Ensure unique designators for all components.
    """

    def __init__(self) -> None:
        self._designators: dict[AddrStr, str] = {}

    def _make_designators(self, root: str) -> dict[str, str]:
        designators: dict[str, str] = {}
        unnamed_components = []
        used_designators = set()

        # FIXME: add lock-file data
        # first pass: grab all the designators from the lock data
        for err_handler, component in atopile.errors.iter_through_errors(
            filter(
                instance_methods.match_components,
                instance_methods.all_descendants(root),
            )
        ):
            with err_handler():
                try:
                    designator = instance_methods.get_data(component, "designator")
                except KeyError:
                    designator = None

                if designator:
                    if designator in used_designators:
                        raise atopile.errors.AtoError(
                            f"Designator {designator} already in use", addr=component
                        )
                    used_designators.add(designator)
                    designators[component] = designator
                else:
                    unnamed_components.append(component)

        # second pass: assign designators to the unnamed components
        for component in unnamed_components:
            try:
                prefix = instance_methods.get_data(component, "designator_prefix")
            except KeyError:
                prefix = "U"

            i = 1
            while f"{prefix}{i}" in used_designators:
                i += 1

            designators[component] = f"{prefix}{i}"
            used_designators.add(designators[component])

        return designators

    def get_designator(self, addr: str) -> str:
        """Return a mapping of instance address to designator."""
        if addr not in self._designators:
            self._designators = self._make_designators(address.get_entry(addr))
        return self._designators[addr]


designator_manager = DesignatorManager()


def get_designator(addr: str) -> str:
    """
    Return the designator for a component
    """
    return designator_manager.get_designator(addr)


# why is this not defined in errors?
class MissingData(atopile.errors.AtoError):
    """
    Raised when a component is missing data in the Basic_Parts.csv file.
    """


def get_specd_value(addr: AddrStr) -> str:
    """
    Return the MPN for a component given its address
    """
    try:
        return str(instance_methods.get_data(addr, "value"))
    except KeyError as ex:
        raise MissingData("$addr has no value", title="No value", addr=addr) from ex


# FIXME: this function's requirements might cause a circular dependency
def download_footprint(addr: AddrStr, footprint_dir: Path):
    """
    Take the footprint from the database and make a .kicad_mod file for it
    TODO: clean this mess up
    """
    return
    if not _is_generic(addr):
        return
    db_data = _get_generic_from_db(addr)

    # convert the footprint to a .kicad_mod file
    try:
        footprint = db_data.get("footprint_data", {})["kicad"]
    except KeyError as ex:
        raise MissingData(
            "db component for $addr has no footprint", title="No Footprint", addr=addr
        ) from ex

    if footprint == "standard_library":
        log.debug("Footprint is standard library, skipping")
        return

    try:
        file_name = db_data.get("footprint", {}).get("kicad")
        file_path = Path(footprint_dir) / str(file_name)

        # Create the directory if it doesn't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w") as footprint_file:
            footprint_file.write(footprint)
    except Exception as ex:
        raise errors.AtoInfraError("Failed to write footprint file", addr=addr) from ex
