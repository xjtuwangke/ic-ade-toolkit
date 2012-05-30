# -*- mode: python -*-
a = Analysis([os.path.join(HOMEPATH,'support\\_mountzlib.py'), os.path.join(HOMEPATH,'support\\useUnicode.py'), 'F:\\release\\assign.py'],
             pathex=['F:\\release'])
pyz = PYZ(a.pure)
exe = EXE( pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name=os.path.join('dist', 'assign.exe'),
          debug=False,
          strip=False,
          upx=True,
          console=True , icon='icon.ico')
