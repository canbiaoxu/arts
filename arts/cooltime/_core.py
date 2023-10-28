import re
from random import uniform
from datetime import datetime as datetime2
from datetime import timedelta
from typing import Union


def parse_add(dt: Union[int, float, dict]):
    if type(dt) is dict:
        return timedelta(**dt)
    return timedelta(seconds=dt)

def parse_time(t: Union[int, float, 'cooltime', str]=None):
    typ = type(t)
    if typ in (int, float): return datetime2.fromtimestamp(t)  # 从时间戳生成
    if not t: return datetime2.now()  # 生成当前时区的当前时间
    if typ is cooltime: return t.t  # 从自身类型生成
    return datetime2(*map(int, re.findall('\d+', str(t))[:7]))

class cooltime():
    t: datetime2
    year: int
    month: int
    day: int
    hour: int
    minute: int
    second: int
    microsecond: int

    def __init__(self, t: Union[int, float, 'cooltime', str]=None):
        self.t = t = parse_time(t)
        self.year = t.year
        self.month = t.month
        self.day = t.day
        self.hour = t.hour
        self.minute = t.minute
        self.second = t.second
        self.microsecond = t.microsecond

    @staticmethod
    def random(start=None, end=None):
        if not start and not isinstance(start, (int, float)): start = 63043200  # 北京时间1972-01-01
        if not end and not isinstance(end, (int, float)): end = 2114352000  # 北京时间2037-01-01
        return cooltime(uniform(float(cooltime(start)), float(cooltime(end))))

    def __eq__(self, t): return self.t == parse_time(t)
    def __ne__(self, t): return self.t != parse_time(t)
    def __lt__(self, t): return self.t < parse_time(t)
    def __le__(self, t): return self.t <= parse_time(t)
    def __ge__(self, t): return self.t >= parse_time(t)
    def __gt__(self, t): return self.t >= parse_time(t)

    def __float__(self): return self.t.timestamp()  # 1687271066.000028
    def __int__(self): return int(self.t.timestamp())  # 1687271066
    def __str__(self): return str(self.t)  # 2023-06-20 22:24:26.000028
    def __repr__(self): return f"cooltime({self.t})"  # cooltime(2023-06-20 22:24:26.000028)

    def date(self): return str(self.t)[:10]  # 2023-06-20
    def floor(self): return str(self.t)[:19]  # 2023-06-20 22:24:26

    def __add__(self, dt): return cooltime(self.t + parse_add(dt))
    def __iadd__(self, dt):
        self.t += parse_add(dt)
        return self
    
    def __sub__(self, dt): return cooltime(self.t - parse_add(dt))
    def __isub__(self, dt):
        self.t -= parse_add(dt)
        return self
    
    def strftime(self, fmt="%Y-%m-%d %H:%M:%S"):
        return self.t.strftime(fmt)