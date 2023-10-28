import numpy as np
from pathlib import Path
from sys import platform
from math import ceil

from arts.vtype import SysEmpty

# 以下模块允许被其它模块导入
from json import dumps as jsonDumps
from json import loads as jsonLoads
from pickle import dumps as pickleDumps
from pickle import loads as pickleLoads
from os.path import abspath


system_type = platform.lower()
if 'win' in system_type: system_type = 'win'
elif 'linux' in system_type: system_type = 'linux'
elif 'mac' in system_type: system_type = 'mac'

def cut_data(data, groupSize):
    return [data[groupSize*(i-1): groupSize*i] for i in range(1, ceil(len(data)/groupSize)+1)]

def getGroupNumber(i, groupSize):
    '''
    组号和索引都是从1开始
    getGroupNumber(1, 3) >>> 1
    getGroupNumber(2, 3) >>> 1
    getGroupNumber(3, 3) >>> 1
    getGroupNumber(4, 3) >>> 2
    '''
    return ceil(i / groupSize)

def jsonChinese(data): return jsonDumps(data, ensure_ascii=False)

# 三元表达式
def ternary(tv, obj, fv): return tv if obj else fv

def check_dir(path):
    return Path(path).mkdir(parents=True, exist_ok=True)
def check_parent_dir(path):
    return Path(path).parent.mkdir(parents=True, exist_ok=True)

def readJson(fpath, default=SysEmpty, mode=3):
    '''
    mode:
        等于1时: 文件不存在时返回default
        等于2时: 文件内容解析错误时返回default
        等于3时: 无论哪种错误, 都返回default
    '''
    try:
        return jsonLoads(Path(fpath).read_text('utf8'))
    except BaseException as e:
        if default is not SysEmpty:
            if mode == 3: return default
            if mode == 1 and type(e) is FileNotFoundError: return default
        raise

def writeJson(fpath, data, ensure_ascii=False):
    fpath = Path(fpath)
    data = jsonDumps(data, ensure_ascii=ensure_ascii)
    try:
        return fpath.write_text(data, 'utf8')
    except FileNotFoundError:
        fpath.parent.mkdir(parents=True, exist_ok=True)
        return fpath.write_text(data, 'utf8')

def repairPathClash(path):
    ''' 解决命名冲突 '''
    while Path(path).exists():
        path += '_'
    return path

def uniform_put(total, siteCount):
    ''' 均匀放球 '''
    baseCount, r = divmod(total, siteCount)
    sites = [baseCount] * siteCount
    if r:
        for x in np.linspace(0, siteCount-1, r):
            sites[round(x)] += 1
    return sites

def cool_iter(obj):
    for i, x in enumerate(obj): yield i, x, type(x)

def limit_input(prompt='', limit:list=[]):
    while True:
        user = input(prompt)
        if user in limit: return user