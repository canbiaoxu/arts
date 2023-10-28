import sys
from pathlib import Path

from ._envname import envname


def _parsecmd():
    kws = sys.argv[1:]
    if kws:
        kw = kws[0].lower()
        if kw == 'set' and len(kws) > 1:
            py = Path(__file__).parent / '_envname.py'
            py.write_text(f"envname = '{kws[1]}'", 'utf8')
            print('创建成功!')
        elif kw == 'read':
            print(envname)
    else:
        print('''指令集:
envname set <名称> | 创建环境名称
envname read       | 查看环境名称
''')