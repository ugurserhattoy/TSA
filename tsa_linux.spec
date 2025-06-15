# -*- mode: python ; coding: utf-8 -*-
# import sys
import os
# import glob

# usr_libs = []

icon_file = os.path.join('data', 'tsa_icon.png')
# base_path = '/usr/lib/**/'
#    tmp_so = '/tmp/libpython3.12.so'
# so_list = [
#     'libpython3.12.so.1.0',
#        'libc.so.6',
#        'libdl.so.2',
#        'libm.so.6',
#        'libutil.so.1',
#        'libpthread.so.0'
# ]
# for s in so_list:
#     usr_libs += [
#         (f, '_internal') for f in glob.glob(base_path + s, recursive=True)
#         if not os.path.islink(f)
#     ]
#    os.system('cp %s %s' % (usr_libs[0][0], tmp_so))
#    usr_libs.append((tmp_so, '_internal'))


a = Analysis(
    ['ui/app_main.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    hooksconfig={},
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    exclude_binaries=True,
    name='TSA',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file,
    # Enable onefile build
    singlefile=True
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='TSA'
)
