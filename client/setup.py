
import py2exe
import os
from distutils.core import setup

files = []
base_dir = "C:\\Users\\austin.jackson\\Desktop\\HotC\\client\\heroes\\"
for f in os.listdir(base_dir):
    f1 = base_dir + f
    f2 = 'heroes', [f1]
    files.append(f2)

setup(
    options = {'py2exe': {'bundle_files': 1, 'compressed': True}},
    zipfile = None,
    console = ['HotC_client.py'],
    data_files = files
)
