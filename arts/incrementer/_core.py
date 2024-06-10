import time, os
from collections import deque


Characters = ''.join(sorted('0123456789abcdefghijklmnopqrstuvwxyz'))
LenChars = len(Characters)


class Incrementer():
    # 可直接调用的属性:
    encoded_pid: str
    
    def __init__(self):
        self._inc_groups = deque()
        self._inc_group_ids = [0]  # 先填充一个任意元素，用于占位，使 _inc_group_ids.index(temp) 的值从 1 开始
        self._simple_incid = 0
    
    def encode_num(self, num: int):
        if num > 0:
            rn = deque()
            while num:
                num, i = divmod(num, LenChars)
                rn.appendleft(Characters[i])
            return ''.join(rn)
        return Characters[0]
    
    def get_encoded_time(self):
        return self.encode_num(int(time.time() * 1000))  # 在 Python 中，一般毫秒后面的数值没有分辨率
    
    def __getattr__(self, name):
        match name:
            case 'encoded_pid':
                self.encoded_pid = self.encode_num(os.getpid())
                return self.encoded_pid
        raise AttributeError(name)
    
    def get_incpk(self):
        try:
            inc_group = self._inc_groups.popleft()
        except IndexError:
            class temp: ...
            self._inc_group_ids.append(temp)
            gid = self.encode_num(self._inc_group_ids.index(temp))
            inc_group = [gid, 0]
        inc_group[1] += 1
        gid, value = inc_group
        self._inc_groups.append(inc_group)
        return f"{gid}_{value}"
    
    def get_simple_incpk(self):
        self._simple_incid += 1
        return self.encode_num(self._simple_incid)