from distutils.core import setup
import py2exe
setup(name="hometape",
      version='0.3.8',
      windows = [
        {
            "script": "hometape.py",
            "icon_resources": [(1, "win_icon.ico")]
        }
    ],
    options = {'py2exe': {'optimize': 2, 'bundle_files': 1, 'compressed': True, \
                                  'excludes': [], 'packages': ['encodings'], \
                                  'dll_excludes': ['MSVCP90.dll']} },
    zipfile = None
)
