# -*- mode: python ; coding: utf-8 -*-
import platform
import kivy.tools.packaging.pyinstaller_hooks as pyinstaller_hooks


os = platform.system()
block_cipher = None


# Carry out platform specific imports
if os == "Windows":
    from kivy_deps import sdl2, glew

# Set platform specific constants
if os == "Linux":
    icon = "../Icons/app-icon.svg"
elif os == "Windows":
    icon = "../Icons/app-icon.ico"
else:
    icon = None


a_kwargs = {
    "pathex": [],
    "binaries": [],
    "datas": [
    	("../Templates/melter_desktop.kv", "Templates"),
        ("../Templates/input_output_chooser.kv", "Templates"),
        ("../Templates/file_chooser_popup.kv", "Templates"),
        (icon, "Icons"),
        ("../Fonts/DroidSansMono.ttf", "Fonts"),
    ],
    "hiddenimports": [
    	"Templates",
    	"Templates.input_output_chooser",
    	"Templates.dropdown_button",
    	"Templates.console_output",
    ],
    "hookspath": [],
    "hooksconfig": {},
    "runtime_hooks": [],
    "excludes": [
        ".git"
    ],
    "win_no_prefer_redirects": False,
    "win_private_assemblies": False,
    "cipher": block_cipher,
    "noarchive": False
}


# Add platform specific kwargs to a_kwargs
if os == "Windows":
    a_kwargs["hiddenimports"].append("win32timezone")
# Add kivy deps and hooks to existing kwargs
for k, v in pyinstaller_hooks.get_deps_all().items():
    if k in a_kwargs:
        a_kwargs[k] += v
    else:
        a_kwargs[k] = v


a = Analysis(["../Melter.py"], **a_kwargs)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name="Melter",
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None , icon=icon)

# Prepare platform dependant args for COLLECT
c_args = [exe, a.binaries, a.zipfiles, a.datas]
if os == "Windows":
    c_args += [Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)]

coll = COLLECT(*c_args,
               strip=False,
               upx=True,
               upx_exclude=[],
               name="Melter")
