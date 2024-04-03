import re
from random import uniform
from datetime import datetime as DT2
from datetime import timedelta


def parse_add(seconds=0, minutes=0, hours=0, days=0, weeks=0):
    return timedelta(seconds=seconds, minutes=minutes, hours=hours, days=days, weeks=weeks)

def parse_time(datetime: 'int|float|str|Cooltime|None'=None) -> DT2:
    typ = type(datetime)
    if typ in (int, float):  # 从时间戳生成
        return DT2.fromtimestamp(datetime)
    elif not datetime:  # 生成当前时区的当前时间
        return DT2.now()
    elif isinstance(datetime, Cooltime):  # 从自身类型生成
        return datetime._datetime
    else:  # 从字符串生成
        datetime = re.split(r'[^\d]+', re.sub(r'^[^\d]+', '', str(datetime)), 5)
        if len(datetime) == 6:
            if second := re.findall(r'(\d+)\.?(\d{0,6})', datetime.pop()):  # microsecond must be in 0..999999
                datetime += second[0]
        return DT2(*[int(x) for x in datetime if x])

class Cooltime():

    def __init__(self, _datetime: 'int|float|str|Cooltime|None'=None):
        self._datetime = parse_time(_datetime)

    @property
    def year(self): return self._datetime.year
    
    @property
    def month(self): return self._datetime.month
    
    @property
    def day(self): return self._datetime.day
    
    @property
    def hour(self): return self._datetime.hour
    
    @property
    def minute(self): return self._datetime.minute
    
    @property
    def second(self): return float(re.findall(r'[\d.]+$', str(self._datetime))[0])

    @staticmethod
    def random(start=None, end=None):
        if type(start) not in (int, float) and not start: start = 63043200  # 北京时间1972-01-01
        if type(end) not in (int, float) and not end: end = 2114352000  # 北京时间2037-01-01
        return Cooltime(uniform(float(Cooltime(start)), float(Cooltime(end))))

    def __eq__(self, _datetime): return self._datetime == parse_time(_datetime)
    def __ne__(self, _datetime): return self._datetime != parse_time(_datetime)
    def __lt__(self, _datetime): return self._datetime < parse_time(_datetime)
    def __le__(self, _datetime): return self._datetime <= parse_time(_datetime)
    def __ge__(self, _datetime): return self._datetime >= parse_time(_datetime)
    def __gt__(self, _datetime): return self._datetime >= parse_time(_datetime)

    def __float__(self): return self._datetime.timestamp()  # 1687271066.000028
    def __int__(self): return int(float(self))  # 1687271066
    def __str__(self): return self.datetime
    def __repr__(self): return f"arts.Cooltime<{self._datetime}>"  # arts.Cooltime<2023-06-20 22:24:26.000028>

    @property
    def datetime(self): return str(self._datetime)  # 2023-06-20 22:24:26.000028

    @property
    def floor_datetime(self): return self.datetime[:19]  # 2023-06-20 22:24:26

    @property
    def date(self): return str(self._datetime.date())  # 2023-06-20

    @property
    def time(self): return str(self._datetime.time())  # 22:24:26.000028

    @property
    def floor_time(self): return self.time[:8]  # 22:24:26
    
    def shift(self, seconds=0, minutes=0, hours=0, days=0, weeks=0):
        self._datetime += parse_add(seconds=seconds, minutes=minutes, hours=hours, days=days, weeks=weeks)
    
    def shift_copy(self, seconds=0, minutes=0, hours=0, days=0, weeks=0):
        return Cooltime(self._datetime + parse_add(seconds=seconds, minutes=minutes, hours=hours, days=days, weeks=weeks))
    
    def strftime(self, fmt=r"%Y-%m-%d %H:%M:%S"):
        return self._datetime.strftime(fmt)