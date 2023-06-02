from typing import List, Any, Dict
import enum

from atopile.model.model import Model
from atopile.project.config import BuildConfig, BaseConfig
from atopile.project.project import Project


class TargetNotFoundError(Exception):
    """
    The target you are looking for does not exist.
    """

def find_target(target_name: str) -> "Target":
    """Find a target by name."""
    #TODO: fix this entire function and premise
    if target_name == "netlist-kicad6":
        import atopile.targets.netlist.kicad6
        return atopile.targets.netlist.kicad6.Kicad6NetlistTarget
    if target_name == "designators":
        import atopile.targets.designators
        return atopile.targets.designators.Designators
    if target_name == "bom-jlcpcb":
        import atopile.targets.bom_jlcpcb
        return atopile.targets.bom_jlcpcb.BomJlcpcbTarget
    raise TargetNotFoundError(target_name)

class TargetCheckResult(enum.IntEnum):
    # data is fully specified so anything
    # untouched between revs will be the same
    COMPLETE = 0

    # there's additional, extraneous data, but what we need is there
    UNTIDY = 1

    # there's enough data to solve deterministically,
    # but if there are any changes in the source,
    # significant changes in the output may occur
    SOLVABLE = 2

    # there's not enough data to solve deterministically
    UNSOLVABLE = 3

class Target:
    def __init__(self, project: Project, model: Model, build_config: BuildConfig) -> None:
        self.project = project
        self.model = model
        self.build_config = build_config

    @property
    def name(self) -> str:
        raise NotImplementedError

    @property
    def config(self) -> BaseConfig:
        return self.project.config.targets.get(self.name, BaseConfig({}, self.project, self.name))

    def build(self) -> None:
        """
        Build this targets output and save it to the build directory.
        What gets called when you run `ato build <target>`
        """
        raise NotImplementedError

    def resolve(self, *args, **kwargs) -> None:
        """
        Interactively solve for missing data, potentially:
        - prompting the user for more info
        - outputting template files for a user to fill out
        This function is expected to be called manually, and is
        therefore allowed to write to version controlled files.
        This is what's run with the `ato resolve <target>` command.
        """
        raise NotImplementedError

    def check(self) -> TargetCheckResult:
        """
        Check whether all the data required to build this target is available and valid.
        This is what's run with the `ato check <target>` command.
        """
        raise NotImplementedError

    def generate(self) -> Any:
        """
        Generate and return the underlying data behind the target.
        This isn't available from the command-line and is instead only used internally.
        It provides other targets with access to the data generated by this target.
        """
        raise NotImplementedError
