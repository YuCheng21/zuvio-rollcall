import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
    'include_files': [
        './app.ui',
        './about.txt',
        './static/',
    ],
    "excludes": [],
}

# base="Win32GUI" should be used only for Windows GUI app
base = None
if sys.platform == "win32":
    base = "Win32GUI"

target = Executable(
    script='./app.py',
    base=base,
    icon='./static/icon.ico'
)

setup(
    name='ZuvioBot',
    version='1.0',
    description='Zuvio 自動點名程式',
    author='Thomas Feng',
    options={'build_exe': build_exe_options},
    executables=[target]
)
