'''
运行此脚本，将自动为指定的本地文件生成哈希值，并将生成的哈希值保存到 `许灿标本地文件哈希值.yaml` 中。
'''

import hashlib, datetime, platform
from pathlib import Path
from os.path import abspath
from os import stat as os_stat

import yaml

this_dir = Path(__file__).parent
local_files_dir = Path(rf'C:\bpath\repo_arts\skybox_local_files')
save_file = this_dir / '许灿标本地文件哈希值.yaml'

assert local_files_dir.exists()

def loop(obj: Path):
    if obj.is_dir():
        return obj.name, dict(map(loop, list(obj.iterdir())))
    else:
        assert obj.is_file()
        print(f"\r{obj.name}", end='                                                                ')
        info = {
            'size': os_stat(abspath(obj), follow_symlinks=False).st_size,
            'sha-512': hashlib.sha512(obj.read_bytes()).hexdigest(),
            'sha3-512': hashlib.sha3_512(obj.read_bytes()).hexdigest(),
        }
        return obj.name, info

hashes = loop(local_files_dir)[1]

environment_info = dict(
    操作系统 = platform.system(),
    系统版本 = platform.release(),
    Python版本 = platform.python_version(),
    生成日期_UTC = datetime.datetime.now(datetime.timezone.utc).isoformat()[:10],
)

result = {'environment_info': environment_info, 'hashes': hashes}
result = yaml.dump(result, Dumper=yaml.SafeDumper, indent=4, allow_unicode=True, sort_keys=True)
save_file.write_text(result, encoding='utf-8')
print('\n已更新哈希值')