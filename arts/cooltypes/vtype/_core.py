import re, os
from math import ceil
from collections import deque
import hashlib
from hashlib import shake_256
from typing import Any, List, Union, Literal
import numpy as np
from pathlib import Path
from sys import platform
from json import dumps as jsonDumps
from json import loads as jsonLoads

class missing_arguments_error(Exception): ...


########################################## vbool ##########################################

class vbool():
    name: str
    _bool: bool

    def __new__(cls, obj, name='', _system=False):
        if _system:
            self = object.__new__(cls)
            self.name = name
            self._bool = bool(obj)
            return self
        else:
            return vtrue if obj else vfalse
    
    def __bool__(self): return self._bool
    def __str__(self): return f"arts//vbool<{self.name}>"

vtrue = vbool(True, 'vtrue', _system=True)  # 解决 1 == True 的历史遗留问题
vfalse = vbool(False, 'vfalse', _system=True)  # 解决 0 == False 的历史遗留问题

def creat_vtrue_instance(name=''): return vbool(True, name, _system=True)
def creat_vfalse_instance(name=''): return vbool(False, name, _system=True)

undefined = creat_vfalse_instance('undefined')  # 逻辑空值，用于与业务空值None相互区分

##################################################################################

class bidict:
    ''' 双向字典 '''
    def __init__(self):
        self.core = {}
    
    def __setitem__(self, key, value):
        self.pop(key, None)
        self.pop(value, None)
        self.core[key] = value
        self.core[value] = key
    
    def __getitem__(self, key):
        return self.core[key]

    def get(self, key, default=undefined):
        value = self.core.get(key, default)
        if value is undefined:
            raise missing_arguments_error('default')
        else:
            return value
    
    def pop(self, key, default=undefined):
        if key in self.core:
            value = self.core.pop(key)
            self.core.pop(value, 0)
            return value
        elif default is undefined:
            raise missing_arguments_error('default')
        else:
            return default

##################################################################################


class ztype():
    core: Any

    def __getattr__(self, name):
        return self.core.__getattr__(name)
    
    @classmethod
    def _GetZtypeCore(cls, obj):
        if isinstance(obj, ztype):
            return obj.core
        return obj
    
    def __str__(self): return str(self.core)
    def __int__(self): return int(self.core)
    def __float__(self): return float(self.core)
    def __bool__(self): return bool(self.core)
    def __bytes__(self): return bytes(self.core)

    def str(self): return str(self)
    def int(self): return int(self)
    def float(self): return float(self)
    def bool(self): return bool(self)
    def bytes(self): return bytes(self.core)

    def __len__(self): return len(self.core)

    # 默认用内核比较大小
    def __eq__(self, obj): return self.core == self._GetZtypeCore(obj)
    def __ne__(self, obj): return self.core != self._GetZtypeCore(obj)
    def __lt__(self, obj): return self.core < self._GetZtypeCore(obj)
    def __le__(self, obj): return self.core <= self._GetZtypeCore(obj)
    def __gt__(self, obj): return self.core > self._GetZtypeCore(obj)
    def __ge__(self, obj): return self.core >= self._GetZtypeCore(obj)

    # 加减乘除默认用内核操作
    def __add__(self, n): return self.__class__(self.core + self._GetZtypeCore(n))
    def __radd__(self, n): return self.__class__(self._GetZtypeCore(n) + self.core)
    def __iadd__(self, n):
        self.core += self._GetZtypeCore(n)
        return self
    
    def __sub__(self, n): return self.__class__(self.core - self._GetZtypeCore(n))
    def __rsub__(self, n): return self.__class__(self._GetZtypeCore(n) - self.core)
    def __isub__(self, n):
        self.core -= self._GetZtypeCore(n)
        return self.core

    def __mul__(self, n): return self.__class__(self.core * self._GetZtypeCore(n))
    def __rmul__(self, n): return self.__class__(self._GetZtypeCore(n) * self.core)
    def __imul__(self, n):
        self.core *= self._GetZtypeCore(n)
        return self

    def __truediv__(self, n): return self.__class__(self.core / self._GetZtypeCore(n))
    def __rtruediv__(self, n): return self.__class__(self._GetZtypeCore(n) / self.core)
    def __itruediv__(self, n):
        self.core /= self._GetZtypeCore(n)
        return self


##################################################################################

class vbytes(ztype):
    ''' 可变字节串 '''

    core: bytes

    def __bytes__(self): return self.core
    def __init__(self, *s, **kvs):
        self.core = bytes(*s, **kvs)

    def md5(self, rtype: Literal['str','bytes','vbytes']='str'):
        value = hashlib.md5(self.core)
        if rtype in (str, 'str'): return value.hexdigest()
        if rtype in (bytes, 'bytes'): return value.digest()
        if rtype in (vbytes, 'vbytes'): return vbytes(value.digest())
        raise ValueError(rtype)

    def shake256(self, rtype: Literal['str','bytes','vbytes']='str', rsize=32):
        value = shake_256(self.core)
        if rtype in (str, 'str'): return value.hexdigest(ceil(rsize/2))[:rsize]
        if rtype in (bytes, 'bytes'): return value.digest(rsize)
        if rtype in (vbytes, 'vbytes'): return vbytes(value.digest(rsize))
        raise ValueError(rtype)

##################################################################################

class vstr(ztype):
    ''' 可变字符串 '''

    core: str

    s_az = 'abcdefghijklmnopqrstuvwxyz'
    s_AZ = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    s_09 = '0123456789'
    s_09az = '0123456789abcdefghijklmnopqrstuvwxyz'
    s_09AZ = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    s_azAZ = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    s_09azAZ = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

    def __str__(self): return self.core
    def __init__(self, *s, **kvs):
        self.core = str(*s, **kvs)

    def wash_paragraph(self):  # 单段清洗
        text = re.sub(r'\s+', ' ', self.core)
        text = re.sub(r'^ +', '', text)
        text = re.sub(r' +$', '', text)
        return vstr(text)

    def sub(self, pattern, repl, count=0, flags=0):
        return vstr(re.sub(pattern, repl, self.core, count, flags))

    def visible(self):  # 是否含可视字符
        return bool(re.search(r'[^\s]', self.core))

    def has_sound(self):   # 是否含有有声字符(支持中文和英文)
        return bool(re.search(r'[\u4e00-\u9fa5\da-zA-Z]', self.core))

    def has_chinese(self):
        return bool(re.search(r'[\u4e00-\u9fa5]', self.core))

    def __contains__(self, obj):
        if isinstance(obj, self.__class__):
            return obj.core in self.core
        return obj in self.core

#################################################################################
# def into_Fraction(*s, **kvs):
#     if s and isinstance(s[0], vnum): return s[0].core
#     return Fraction(*s, **kvs)

# class vnum(ztype):
#     ''' 可变数字
#         1、 float 和 int 没必要拆成两种, 太麻烦了
#         2、 解决浮点数精度问题
#     '''
#     core: Fraction
    
#     def __init__(self, numerator, denominator=undefined):
#         if denominator is undefined:
#             self.core = into_Fraction(numerator)
#         else:
#             self.core = Fraction(into_Fraction(numerator), into_Fraction(denominator))

##################################################################################

def XpathGet(dic, i, keySize, keys):
    if i < keySize and type(dic) is dict:
        ikey = keys[i]
        for k, v in dic.items():
            if k == ikey:
                if i == keySize - 1:
                    return v
                value = XpathGet(v, i + 1, keySize, keys)
                if value is not undefined:
                    return value
            else:
                value = XpathGet(v, i, keySize, keys)
                if value is not undefined:
                    return value
    return undefined

def into_dict(*s, **kvs):
    if s and isinstance(s[0], vdict): return s[0].core.copy()
    return dict(*s, **kvs)

class vdict(ztype):
    core: dict

    def __init__(self, *s, **kvs):
        self.core = into_dict(*s, **kvs)

    def xpath(self, *keys):
        '''
            一个查找字典的子孙键的工具.
            使用场景: 当字典的结构具有不确定性, 或者要获取的键位于较深层的子孙层时, 可使用该函数进行取值.
        '''
        if not isinstance(keys, tuple):
            keys = (keys, )
        value = XpathGet(self.core, 0, len(keys), keys)
        if value is undefined:
            raise KeyError(keys)
        return value
    
    def deepGet(self, *keys, default=undefined):
        res = self.core
        try:
            for k in keys:
                res = res[k]
            return res
        except:
            if default is undefined:
                raise missing_arguments_error('default')
            else:
                return default

########################################## ToolPool ##########################################

class ToolPool():
    def __init__(self, mktool, minlen:int=0, maxlen=None):
        self.mktool = mktool
        self.pool = deque([mktool() for i in range(minlen or 0)], maxlen=maxlen)
    
    def put(self, obj):  # 右进
        self.pool.append(self.beforePut(obj))
    
    def get(self):  # 左出
        try:
            return self.beforeGet(self.pool.popleft())
        except:
            return self.mktool()
    
    def beforeGet(self, obj): return obj
    def beforePut(self, obj): return obj


class _CoolQueue:
    ''' 一个先进先出, 可设置最大容量, 可固定元素的队列 '''

    def __init__(self, maxlen: int=None):
        self._core: List[dict] = []
        self.maxlen = maxlen or float('inf')

    def _trim(self):
        _core = self._core
        if len(_core) > self.maxlen:
            dc = len(_core) - self.maxlen
            indexes = []
            for i,x in enumerate(_core):
                if not x['pin']:
                    indexes.append(i)
                if len(indexes) == dc:
                    break
            for i in indexes[::-1]:
                _core.pop(i)

    def add_many(self, *objs):
        for x in objs:
            self._core.append({'obj':x, 'pin':False})
        self._trim()

    def __iter__(self):
        for x in self._core:
            yield x['obj']

    def pin(self, *indexes):
        for i in indexes:
            self._core[i]['pin'] = True

    def unpin(self, *indexes):
        for i in indexes:
            self._core[i]['pin'] = False

    def copy(self):
        que = self.__class__(maxlen=self.maxlen)
        que._core = self._core.copy()
        return que
    
    def deepcopy(self): ...  # 创建这个方法是为了提醒用户: copy 方法是浅拷贝

    def __add__(self, obj: Union[list, '_CoolQueue']):
        que = self.copy()
        if isinstance(obj, self.__class__):
            que._core += obj._core
            que._trim()
        else:
            que.add_many(*obj)
        return que
    

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

def readJson(fpath, default=undefined, mode=3):
    '''
    mode:
        等于1时: 文件不存在时返回default
        等于2时: 文件内容解析错误时返回default
        等于3时: 无论哪种错误, 都返回default
    '''
    try:
        return jsonLoads(Path(fpath).read_text('utf8'))
    except BaseException as e:
        if default is not undefined:
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

def get_chrome_path():
    for chrome in (
        r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
        rf'C:\Users\{os.getlogin()}\AppData\Local\Google\Chrome\Application\chrome.exe',
        rf'C:\Users\{os.getlogin()}\AppData\Local\360ChromeX\Chrome\Application\360ChromeX.exe'
        '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        '/usr/bin/chromium-browser',
        '/usr/bin/google-chrome',
    ):
        if Path(chrome).exists():
            return chrome
    return None