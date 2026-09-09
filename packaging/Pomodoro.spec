# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec: freezes the Pomodoro GUI into a macOS ``.app`` bundle.

Build with::

    pyinstaller --noconfirm --clean packaging/Pomodoro.spec

or just run ``packaging/build.sh``, which also (re)generates the icon.
"""

from pathlib import Path

from PySide6 import __version__ as _pyside_version  # noqa: F401  (ensures PySide6 is importable)

SPEC_DIR = Path(SPECPATH).resolve()
PROJECT_ROOT = SPEC_DIR.parent

# Read the version straight from the package so it stays in one place.
_version_ns: dict = {}
exec((PROJECT_ROOT / "src" / "pomodoro" / "__init__.py").read_text(encoding="utf-8"), _version_ns)
APP_VERSION = _version_ns["__version__"]

icon_path = SPEC_DIR / "Pomodoro.icns"

a = Analysis(
    [str(SPEC_DIR / "pomodoro_app.py")],
    pathex=[str(PROJECT_ROOT / "src")],
    binaries=[],
    datas=[
        # Ship the phase-end sounds inside the bundle. Users can still override
        # them by dropping MP3s into ~/Library/Application Support/Pomodoro/sounds/.
        (str(PROJECT_ROOT / "sounds"), "sounds"),
        # Ship the logo mark used for the in-app header and window icon.
        (str(PROJECT_ROOT / "assets"), "assets"),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tkinter",
        "PySide6.QtWebEngineCore",
        "PySide6.QtWebEngineWidgets",
        "PySide6.QtQuick",
        "PySide6.QtQml",
        "PySide6.Qt3DCore",
        "PySide6.QtCharts",
        "PySide6.QtDataVisualization",
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Pomodoro",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,          # follows the building machine (arm64 on Apple Silicon)
    codesign_identity=None,    # ad-hoc signed after the build (see build.sh)
    entitlements_file=None,
    icon=str(icon_path),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="Pomodoro",
)

app = BUNDLE(
    coll,
    name="Pomodoro.app",
    icon=str(icon_path),
    bundle_identifier="com.l3montree.pomodoro",
    version=APP_VERSION,
    info_plist={
        "CFBundleName": "Pomodoro",
        "CFBundleDisplayName": "Pomodoro",
        "CFBundleShortVersionString": APP_VERSION,
        "CFBundleVersion": APP_VERSION,
        "NSHighResolutionCapable": True,
        "LSMinimumSystemVersion": "11.0",
        "LSApplicationCategoryType": "public.app-category.productivity",
        "NSHumanReadableCopyright": "MIT License",
        # The countdown must keep ticking while the window is in the background.
        "LSUIElement": False,
    },
)
