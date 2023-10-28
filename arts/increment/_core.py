import time, os
from collections import deque
from random import choices


Characters = ''.join(sorted('0123456789abcdefghijklmnopqrstuvwxyz'))
LenChars = len(Characters)

def EncodeNum(num:int):
    if num > 0:
        rn = deque()
        while num:
            num, i = divmod(num, LenChars)
            rn.appendleft(Characters[i])
        return ''.join(rn)
    return Characters[0]

getTid = lambda : EncodeNum(int(time.time() * 1000))  # 一般毫秒后面的数值没有分辨率
pid = EncodeNum(os.getpid())  # 进程ID

class incrementer():
    def __init__(self, macid=None, macidSize=4):
        self._threads = [1]  # 线程安全
        self._ContPool = deque()  # 线程安全
        self.macid = macid or ''.join(choices(Characters, k=macidSize or 1))
        self._TMP = f"{getTid()}_{self.macid}_{pid}"

    def _getid(self):
        try:
            cont = self._ContPool.popleft()
        except:
            class ele: ...
            self._threads.append(ele)
            x = EncodeNum(self._threads.index(ele))
            cont = ['', 0] if x == '1' else [f"{x}-", 0]
        cont[1] += 1
        x, y = cont
        self._ContPool.append(cont)
        return f"{x}{y}"

    # 使用创建进程时的时间
    def pk1(self): return f"{self._TMP}_{self._getid()}"

    # 使用当前时间 
    def pk2(self): return f"{getTid()}_{self.macid}_{pid}_{self._getid()}"

    def pk3(self): return self._getid()