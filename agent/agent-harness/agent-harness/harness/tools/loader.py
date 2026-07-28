"""Discover and import builtin tool modules and user modules in `tools/`."""
from __future__ import annotations

import importlib
import importlib.util
import logging
import pkgutil
import sys

from harness.config import PROJECT_ROOT

logger = logging.getLogger(__name__)


def load_all_tools() -> list[str]:
    """Import every builtin tool module and every user `tools/*.py` module.

    Returns a list of human-readable error strings (empty when everything
    imported cleanly). A broken user tool never prevents startup.
    """
    errors: list[str] = []

    import harness.tools.builtin as builtin_pkg

    for module_info in pkgutil.iter_modules(builtin_pkg.__path__):
        module_name = f"{builtin_pkg.__name__}.{module_info.name}"
        try:
            importlib.import_module(module_name)
        except Exception as exc:
            message = f"{module_name}: {type(exc).__name__}: {exc}"
            logger.warning("failed to import builtin tool module: %s", message)
            errors.append(message)

    tools_dir = PROJECT_ROOT / "tools"
    if tools_dir.is_dir():
        for path in sorted(tools_dir.glob("*.py")):
            if path.name.startswith("_"):
                continue
            module_name = f"user_tools.{path.stem}"
            try:
                spec = importlib.util.spec_from_file_location(module_name, path)
                if spec is None or spec.loader is None:
                    raise ImportError(f"could not create an import spec for {path.name}")
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)
            except Exception as exc:
                message = f"{path.name}: {type(exc).__name__}: {exc}"
                logger.warning("failed to import user tool: %s", message)
                errors.append(message)

    return errors
