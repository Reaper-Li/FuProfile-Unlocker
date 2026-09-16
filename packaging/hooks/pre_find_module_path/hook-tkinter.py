"""Keep Tcl/Tk 9's DLL-embedded library available to PyInstaller.

Python's install-manager distribution of Tcl/Tk 9 stores its script library
inside ``tcl90.dll``.  PyInstaller 6.22 can package and run that layout, but
its discovery subprocess may still classify the installation as broken and
exclude ``tkinter`` before dependency analysis.  Point discovery back at the
standard-library package; the normal ``_tkinter`` hook then collects the
extension and its Tcl/Tk DLL dependencies.
"""

from pathlib import Path


def pre_find_module_path(hook_api) -> None:
    import tkinter

    hook_api.search_dirs = [str(Path(tkinter.__file__).resolve().parent.parent)]
