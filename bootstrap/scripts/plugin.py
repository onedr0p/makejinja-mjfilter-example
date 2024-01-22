from collections.abc import Callable
from pathlib import Path
from jinja2.utils import import_string
from typing import Any
import makejinja

class Plugin(makejinja.plugin.Plugin):
    def __init__(self, data: dict[str, Any], config: makejinja.config.Config):
        self.user_data = data
        self.user_config = config

        self._excluded_dirs: set[Path] = set()

        for input_path in config.inputs:
            for filter_file in input_path.rglob("_mjfilter.py"):
                filter_file = filter_file.relative_to(Path.cwd())
                filter_file = filter_file.with_suffix("")
                filter_module = str(filter_file).replace("/", ".")
                filter_func: Callable[[dict[str, Any]], bool] = import_string(
                    f"{filter_module}:main"
                )
                if filter_func(data) is False:
                    self._excluded_dirs.add(filter_file.parent)

    def path_filters(self):
        return [self._mjfilter_func]

    def _mjfilter_func(self, path: Path) -> bool:
        # Render the file if there is no parent directory that is excluded
        return not any(
            path.is_relative_to(excluded_dir) for excluded_dir in self._excluded_dirs
        )
