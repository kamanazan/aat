from cx_Freeze import setup, Executable
import time

if __name__ == "__main__":
    options = {
        'build':{
            'build_exe': 'build/build_%s' % time.strftime(" %d%m%Y_%H%M%S", time.localtime())
        }
    }
    executables = [
        Executable('aat.py', targetName='aat.exe')
    ]

    setup(name='aat',
          version=time.strftime("%Y.%m.%H%M", time.localtime()),
          description='AAT',
          options=options,
          executables=executables
    )
