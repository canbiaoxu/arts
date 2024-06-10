
class Rslice:
    def __init__(self, core: list|tuple|str): self.core = core
    
    def __len__(self): return len(self.core)

    def __getitem__(self, key):
        core = self.core
        if isinstance(key, int):
            if key > 0: return core[key - 1]
            if key < 0: return core[key]
            raise IndexError(key)
        elif isinstance(key, slice):
            L, R, S = key.start, key.stop, key.step or 1
            tL, tR, tS = type(L), type(R), type(S)
            assert {tL, tR, tS} <= {int, type(None)}
            assert 0 not in (L, R)
            assert S > 0
            if '-' in f"{L}{R}":  # -是负号
                lenSheet = len(self)
                if '-' in str(L): L = lenSheet + L + 1  # R索引
                if '-' in str(R): R = lenSheet + R + 1  # R索引
            if tL is tR is int:
                if max(L, R) < 1: return core[0:0]
                if R >= L: return core[max(0,L-1):R:S]
                if R >= 2: return core[L-1:R-2:-S]
                return core[L-1:None:-S]
            elif tL is int:
                if L > 0: return core[L-1:None:S]
                return core[L:None:S]
            elif tR is int:
                if R >= 1: return core[None:R:S]
                if R == 0: return core[0:0:S]
                if R == -1: return core[None:None:S]
                return core[None:R + 1]
            else:
                return core[None:None:S]
        raise KeyError(key)
    
    def __setitem__(self, key, value):
        self.core[self._setitemBase(key)] = value
    
    def _setitemBase(self, key):
        if isinstance(key, int):
            if key > 0: return key - 1
            if key < 0: return key
            assert key != 0
        elif isinstance(key, slice):
            L, R, S = key.start, key.stop, key.step or 1
            tL, tR, tS = type(L), type(R), type(S)
            assert {tL, tR, tS} <= {int, type(None)}
            assert 0 not in (L, R)
            assert S > 0
            if '-' in f"{L}{R}":  # -是负号
                lenSheet = len(self)
                if '-' in str(L): L = lenSheet + L + 1  # R索引
                if '-' in str(R): R = lenSheet + R + 1  # R索引
            if tL is tR is int:
                if R<L: L,R = R,L
                if R < 1: return slice(None, 0)  # 左侧插入
                if L > 0: return slice(L-1, R, None)
                return slice(None, R, None)
            elif tL is int:
                if L > 0: return slice(L-1, None)
                return slice(None, None)
            elif tR is int:
                return slice(None, R)
            else:
                return slice(None, None)
        raise KeyError(key)