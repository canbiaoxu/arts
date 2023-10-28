from copy import deepcopy
from collections import deque
from pymysql import connect  # 代码提示
from pymysql.cursors import DictCursor
from json import dumps as jsonDumps


class TRUE:
    def __bool__(self): return True

class FALSE:
    def __bool__(self): return False

uniset = TRUE()
empset = FALSE()
SysEmpty = FALSE()

class OrmIndexError(IndexError):
    def __repr__(self):
        return 'OrmIndexError'

def jsonChinese(data): return jsonDumps(data, ensure_ascii=False)

class ToolPool():
    def __init__(self, mktool, minlen:int=0, maxlen=None):
        self.mktool = mktool
        self.pool = deque([mktool() for i in range(minlen or 0)], maxlen=maxlen)
    
    def put(self, obj):
        obj['cursor'].close()
        self.pool.append(obj)
    
    def get(self, dbName=''):
        try:
            obj = self.pool.popleft()
            conn = obj['conn']
            conn.ping(reconnect=True)
            conn.commit()  # pymysql只有在commit时才会获取数据库的最新状态
            obj['cursor'] = conn.cursor(cursor=DictCursor)
        except:
            obj = self.mktool()
        if dbName and obj['dbName'] != dbName:
            obj['cursor'].execute(f'use {dbName}')
            obj['dbName'] = dbName
        return obj

class ORM():
    def __init__(self, mkconn):
        def _():
            conn:connect = mkconn()
            return dict(
                conn = conn,
                cursor = conn.cursor(cursor=DictCursor),
                dbName = ''
            )
        self.connPool = ToolPool(mktool=_, minlen=1, maxlen=1)
        # 当增删改查报错时, conn不再放回连接池, 以避免含有残留数据
    
    def getDbList(self):
        obj = self.connPool.get()
        obj['cursor'].execute("show databases")  # 非本地操作, 需要连接到数据库
        r = list(obj['cursor'].fetchall())
        self.connPool.put(obj)
        return r
    
    def getDbNames(self): return [x['Database'] for x in self.getDbList()]
    def __len__(self): return len(self.getDbList())
    def __contains__(self, dbName): return dbName in self.getDbNames()
    
    def __getitem__(self, key):
        if isinstance(key, str):
            return dbORM(connPool=self.connPool, dbName=key)
        elif isinstance(key, tuple):
            return [dbORM(connPool=self.connPool, dbName=x) for x in key]
        elif isinstance(key, slice):
            assert key.start is key.stop is key.step is None
            return [dbORM(connPool=self.connPool, dbName=x) for x in self.getDbNames()]
        else:
            raise TypeError(key)
    
    def close(self):
        obj = self.connPool.get()
        r = obj['conn'].close()  # 关闭后就不必再放回self.connPool了
        return r or True

class dbORM():
    def __init__(self, connPool:ToolPool, dbName):
        self.connPool = connPool
        self.dbName = dbName

    def __repr__(self):
        return f'coolmysql.dbORM("{self.dbName}")'
    __str__ = __repr__

    def getSheetNames(self):
        obj = self.connPool.get(self.dbName)
        sql = f'select table_name from information_schema.tables where table_schema = "{self.dbName}"'
        obj['cursor'].execute(sql)
        r = [x['TABLE_NAME'] for x in list(obj['cursor'].fetchall())]
        self.connPool.put(obj)
        return r

    def __len__(self): return len(self.getSheetNames())
    def __contains__(self, sheetName): return sheetName in self.getSheetNames()

    def __getitem__(self, key):
        if isinstance(key, str):
            return sheetORM(connPool=self.connPool, dbName=self.dbName, sheetName=key)
        elif isinstance(key, tuple):
            return [sheetORM(connPool=self.connPool, dbName=self.dbName, sheetName=x) for x in key]
        elif isinstance(key, slice):
            assert key.start is key.stop is key.step is None
            sheets = self.getSheetNames()
            return [sheetORM(connPool=self.connPool, dbName=self.dbName, sheetName=x) for x in sheets]
        else:
            raise TypeError(key)
        
    def close(self):
        obj = self.connPool.get()
        r = obj['conn'].close()
        return r or True

class Factory:
    _variable = True

    def __init__(self, where):
        if where is not empset:
            where = where or uniset
        self.where = where
        self._variable = False

    def __setattr__(self, name, value):
        assert self._variable
        object.__setattr__(self, name, value)
    
    def __bool__(self): return True  # 下面有一个 where or Factory(uniset)

    def __and__(self, obj):
        a = self.where
        b = obj.where
        if a is uniset: return Factory(b)
        if b is uniset: return Factory(a)
        if a and b: return Factory(f"({a}) and ({b})")
        return Factory(empset)

    def __or__(self, obj):
        a = self.where
        b = obj.where
        if a is empset: return Factory(b)
        if b is empset: return Factory(a)
        if a is uniset or b is uniset: return Factory(uniset)
        return Factory(f"({a}) or ({b})")

    def __invert__(self):
        w = self.where
        if w is uniset: return Factory(empset)
        if w is empset: return Factory(uniset)
        return Factory(f"not ({w})")

    def __sub__(self, obj): return self & (~ obj)
    
    def __str__(self):
        w = self.where
        if w is uniset: return ''
        if w is empset: return ' where 1 = 2'
        return f" where {w}"


class Filter():
    _variable = True

    def __init__(self, field):
        self.field = field
        self._variable = False
    
    def __setattr__(self, name, value):
        assert self._variable
        object.__setattr__(self, name, value)

    def __eq__(self, obj):
        if obj is None:
            return Factory(f"{self.field} is null")
        return Factory(f"{self.field} = {jsonChinese(obj)}")

    def __ne__(self, obj):
        if obj is None:
            return Factory(f"{self.field} is not null")
        return Factory(f"{self.field} != {jsonChinese(obj)}")

    def __lt__(self, obj): return Factory(f"{self.field} < {jsonChinese(obj)}")
    def __le__(self, obj): return Factory(f"{self.field} <= {jsonChinese(obj)}")
    def __gt__(self, obj): return Factory(f"{self.field} > {jsonChinese(obj)}")
    def __ge__(self, obj): return Factory(f"{self.field} >= {jsonChinese(obj)}")
    def re(self, string): return Factory(f"{self.field} regexp {jsonChinese(string or '')}")

    def isin(self, *lis):
        if not lis: return Factory(empset)
        if len(lis) == 1: return self == lis[0]
        null = False
        type_item = {str:set(), int:set(), float:set()}
        for i, x in enumerate(lis):
            if x is None:
                null = True
            else:
                type_item[type(x)].add(x)
        sumlis = []
        for lis in type_item.values():
            if len(lis) == 1:
                sumlis.append(f"{self.field} = {jsonChinese(list(lis)[0])}")
            elif len(lis) > 1:
                sumlis.append(f"{self.field} in ({', '.join(jsonChinese(x) for x in lis)})")
        if null:
            sumlis.append(f"{self.field} is null")
        if len(sumlis) == 1:
            return Factory(sumlis[0])
        else:
            return Factory(' or '.join(f"({x})" for x in sumlis))

    def notin(self, *lis):
        if not lis: return Factory(uniset)
        if len(lis) == 1: return self != lis[0]
        null = False
        type_item = {str:set(), int:set(), float:set()}
        for i, x in enumerate(lis):
            if x is None:
                null = True
            else:
                type_item[type(x)].add(x)
        sumlis = []
        for lis in type_item.values():
            if len(lis) == 1:
                sumlis.append(f"{self.field} != {jsonChinese(list(lis)[0])}")
            elif len(lis) > 1:
                sumlis.append(f"{self.field} not in ({', '.join(jsonChinese(x) for x in lis)})")
        if null:
            sumlis.append(f"{self.field} is not null")
            sumlis = sumlis[0] if len(sumlis) == 1 else ' and '.join(f"({x})" for x in sumlis)
        else:
            sumlis = sumlis[0] if len(sumlis) == 1 else ' and '.join(f"({x})" for x in sumlis)
            sumlis = f"({sumlis}) or ({self.field} is null)"
        return Factory(sumlis)

class makeSlice():
    def __init__(self, func, *vs, **kvs):
        self.func = func
        self.vs = vs
        self.kvs = kvs
    
    def __getitem__(self, key):
        return self.func(key, *self.vs, **self.kvs)

class sheetORM():
    _variable = True
    _pk = ''

    def __init__(self, connPool:ToolPool, dbName:str, sheetName:str, where=None, columns='*', _sort=None):
        assert columns  # 不能为空
        self.columns = columns  # str型 或 tuple型
        self.connPool = connPool
        self.dbName = dbName
        self.sheetName = sheetName
        self.where = where or Factory(uniset)
        self._sort = deepcopy(_sort or {})
            # {A:True, B:False, C:1, D:0}
            # bool(value) == True --> 升序
            # bool(value) == False --> 降序
        self._variable = False

    def __setattr__(self, name, value):
        assert self._variable
        object.__setattr__(self, name, value)

    def __repr__(self):
        return f'coolmysql.sheetORM("{self.dbName}.{self.sheetName}")'
    __str__ = __repr__

    def _copy(self, where=SysEmpty, columns=SysEmpty, _sort=SysEmpty):
        return sheetORM(
            connPool = self.connPool,
            dbName = self.dbName,
            sheetName = self.sheetName,
            where = self.where if where is SysEmpty else where,
            columns = self.columns if columns is SysEmpty else columns,
            _sort = self._sort if _sort is SysEmpty else _sort
        )

    def _ParseOrder(self):
        if self._sort:
            return ' order by ' + ', '.join([k if v else f"{k} desc" for k,v in self._sort.items()])
        return ''

    def _ParseColumns(self):
        if type(self.columns) is str:
            return self.columns
        return ', '.join(self.columns)
    
    def update_by_pk(self, data:dict):
        pk = self.getPK()
        records = {}
        for key, line in data.items():
            for field, value in line.items():
                records.setdefault(field, {})[key] = value
        blocks = []
        for field, kvs in records.items():
            s = [f"{field} = ", '    case']
            for k, v in kvs.items():
                s.append(f"        when {pk} = {jsonChinese(k)} then {jsonChinese(v)}")
            s.append(f"else {field}")
            s.append('end')
            blocks.append('\n'.join(s))
        blocks = ' ,\n'.join(blocks)
        sql = f"update {self.sheetName} set \n{blocks}"
        r, cursor = self.execute(sql=sql)
        return cursor

    def apply(self, handler):
        return makeSlice(self._applyBase, handler=handler)
    
    def _applyBase(self, key, handler):
        pk = self.getPK()
        # 添加主键字段
        cols = raw_columns = self.columns
        if isinstance(cols, str): cols = [cols]
        for x in cols:
            if x.strip() in ('*', pk):
                break
        else:
            self.columns = tuple(list(cols) + [pk])
        # 从数据库提取数据
        lines = self[key]
        object.__setattr__(self, 'columns', raw_columns)  # 恢复用户设定的columns
        if type(lines) is dict:
            lines = [lines]
            r_type = 'dict'
        else:
            r_type = 'list'
        # 处理数据
        records = {}
        for line in lines:
            key = line[pk]
            line2 = line.copy()
            handler(line)
            for k, v in line.items():
                if v != line2.get(k, SysEmpty):
                    records.setdefault(k, {})[key] = v
        if r_type == 'dict':
            lines = lines[0]
        # 更新到数据库
        if records:
            blocks = []
            for field, kvs in records.items():
                s = [f"{field} = ", '    case']
                for k, v in kvs.items():
                    s.append(f"        when {pk} = {jsonChinese(k)} then {jsonChinese(v)}")
                s.append(f"else {field}")
                s.append('end')
                blocks.append('\n'.join(s))
            blocks = ' ,\n'.join(blocks)
            sql = f"update {self.sheetName} set \n{blocks}"
            self.execute(sql=sql)
            return dict(data=lines)
        else:
            return dict(data=lines)

    def order(self, **rule): return self._copy(_sort={**rule})

    def __add__(self, data):
        if type(data) is dict:
            cols = data.keys()
            sql = f"insert into {self.sheetName}({', '.join(cols)}) values ({', '.join(('%s',)*len(cols))})"
            rdata, cursor = self.execute(sql, tuple(data.values()))
            return cursor  # cursor.rowcount, cursor.lastrowid
        else:
            cols = set()
            for x in data: cols |= set(x)
            cols = list(cols)
            sql = f"insert into {self.sheetName}({', '.join(cols)}) values ({', '.join(('%s',)*len(cols))})"
            data = tuple(tuple(x.get(k) for k in cols) for x in data)
            r, cursor = self.executemany(sql, data)
            return cursor

    def delete(self):
        return makeSlice(self._deleteBase)
        
    def _deleteBase(self, key):
        # [::]
        if isinstance(key, slice):
            L, R, S = key.start, key.stop, key.step or 1
            if S in [None,1]:
                if (L in [None,1] and R in [None,-1]) or (L == -1 and R == 1):
                    rdata, cursor = self.execute(f"delete from {self.sheetName}{self.where}")
                    return cursor
        # [1]且无排序
        if key == 1 and not self._ParseOrder():
            rdata, cursor = self.execute(f"delete from {self.sheetName}{self.where} limit 1")
            return cursor
        # 其它情况
        pk = self.getPK()
        try:
            pks = self[pk][key]
        except OrmIndexError:
            rdata, cursor = self.execute(f"delete from {self.sheetName} where 1 = 2 limit 1")
        else:
            if isinstance(pks, list):
                if pks:
                    pks = [x[pk] for x in pks]
                    rdata, cursor = self.execute(f"delete from {self.sheetName}{mc[pk].isin(*pks)}")
                else:
                    rdata, cursor = self.execute(f"delete from {self.sheetName} where 1 = 2")
            else:
                rdata, cursor = self.execute(f"delete from {self.sheetName}{mc[pk] == pks[pk]} limit 1")
        return cursor

    def update(self, data):
        return makeSlice(self._updateBase, data=data)
    
    def _updateBase(self, key, data:dict):
        data = ', '.join([f"{k}={v.field}" if isinstance(v,Filter) else f"{k}={jsonChinese(v)}" for k,v in data.items()])
        # [::]
        if isinstance(key, slice):
            L, R, S = key.start, key.stop, key.step or 1
            if S in [None,1]:
                if (L in [None,1] and R in [None,-1]) or (L == -1 and R == 1):
                    rdata, cursor = self.execute(f"update {self.sheetName} set {data}{self.where}")
                    return cursor
        # [1]且无排序
        if key == 1 and not self._ParseOrder():
            rdata, cursor = self.execute(f"update {self.sheetName} set {data}{self.where} limit 1")
            return cursor
        # 其它情况
        pk = self.getPK()
        try:
            pks = self[pk][key]
        except OrmIndexError:
            rdata, cursor = self.execute(f"update {self.sheetName} set {data} where 1 = 2 limit 1")
        else:
            if isinstance(pks, list):
                if pks:
                    pks = [x[pk] for x in pks]
                    rdata, cursor = self.execute(f"update {self.sheetName} set {data}{mc[pk].isin(*pks)}")
                else:
                    rdata, cursor = self.execute(f"update {self.sheetName} set {data} where 1 = 2")
            else:
                rdata, cursor = self.execute(f"update {self.sheetName} set {data}{mc[pk] == pks[pk]} limit 1")
        return cursor
    
    def execute(self, sql:str, data=None, commit=True):
        mobj:dict = self.connPool.get(self.dbName)
        conn:connect = mobj['conn']
        cursor:DictCursor = mobj['cursor']
        if commit:
            try:
                cursor.execute(sql, data)
                r = list(cursor.fetchall())
                conn.commit()
                self.connPool.put(mobj)
                return r, cursor
            except:
                conn.rollback()
                raise
        else:
            cursor.execute(sql, data)
            r = list(cursor.fetchall())
            self.connPool.put(mobj)
            return r, cursor
    
    def executemany(self, sql:str, data):
        mobj:dict = self.connPool.get(self.dbName)
        conn:connect = mobj['conn']
        cursor:DictCursor = mobj['cursor']
        try:
            cursor.executemany(sql, data)
            r = list(cursor.fetchall())
            conn.commit()
            self.connPool.put(mobj)
            return r, cursor
        except:
            conn.rollback()
            raise
    
    def getPK(self):
        if not self._pk:
            sql = f"select column_name from information_schema.columns where table_schema = '{self.dbName}' and table_name = '{self.sheetName}' and column_key='PRI' "
            rdata, cursor = self.execute(sql, commit=False)
            data = rdata[0]
            assert len(data) == 1
            _pk = list(data.values())[0]
            object.__setattr__(self, '_pk', rdata[0]['COLUMN_NAME'])
        return self._pk
    
    def getColumns(self, comment=True, type=True):
        need = ['column_name as name']
        if comment: need.append('column_comment as comment')
        if type: need.append('column_type as type')
        need = ', '.join(need)
        sql = f"select {need} from information_schema.columns where table_schema = '{self.dbName}' and table_name = '{self.sheetName}'"
        rdata, cursor = self.execute(sql, commit=False)
        return rdata
    
    def __len__(self):
        rdata, cursor = self.execute(f"select count(1) as tatal from {self.sheetName}{self.where}", commit=False)
        return rdata[0]['tatal']
    len = __len__

    def __setitem__(self, key, value):
        if value is None:
            self._deleteBase(key)
        elif isinstance(value, dict):
            self._updateBase(key, data=value)
        else:
            raise TypeError(key)
    
    def __getitem__(self, key):
        # 索引取值
        if isinstance(key, int):
            index = key
            if index < 0: index = len(self) + index + 1  # R索引
            if index < 1: raise OrmIndexError(f"index({key}) out of range")
            skip = index - 1
            parseLimit = f" limit {skip}, 1"
            sql = f"select {self._ParseColumns()} from {self.sheetName}{self.where}{self._ParseOrder()}{parseLimit}"
            r, cursor = self.execute(sql, commit=False)
            if r:
                return r[0]
            else:
                raise OrmIndexError(f"index({key}) out of range")
                # 没有的话引发OrmIndexError错误. 已被self.update和self.delete调用
        # 切片取值
        if isinstance(key, slice):
            # 没有的话返回空列表, 但不要报错. 已被self.update和self.delete调用
            L, R, S = key.start, key.stop, key.step or 1
            tL, tR, tS = type(L), type(R), type(S)
            assert {tL, tR, tS} <= {int, type(None)}
            assert 0 not in (L, R)
            assert S > 0
            lenSheet = float('inf')
            if '-' in f"{L}{R}":  # -是负号
                lenSheet = len(self)
                if '-' in str(L): L = lenSheet + L + 1  # R索引
                if '-' in str(R): R = lenSheet + R + 1  # R索引
            sliceSort = True  # 正序
            if tL is tR is int and R < L:
                L, R = R, L
                sliceSort = False  # 逆序
            skip = max(1, L or 1) - 1  # 把L转化成skip
            if R is None: R = float('inf')
            size = R - skip
            if skip >= lenSheet: return []
            if size > 0:
                if size == float('inf'):
                    parseLimit = f" limit {skip}, 9999999999999"
                else:
                    parseLimit = f" limit {skip}, {size}"
                sql = f"select {self._ParseColumns()} from {self.sheetName}{self.where}{self._ParseOrder()}{parseLimit}"
                r, cursor = self.execute(sql, commit=False)
                if sliceSort:
                    if S == 1:
                        return r
                    else:
                        return r[::S]
                else:
                    return r[::-S]
            else:
                return []
        # 限定columns
        # 输入多个字符串, 用逗号隔开, Python会自动打包成tuple
        if isinstance(key, (str, tuple)):
            return self._copy(columns=key)
        # Factory
        if isinstance(key, Factory):
            return self._copy(where=self.where & key)
        raise TypeError(key)
    
    def close(self):
        obj = self.connPool.get()
        r = obj['conn'].close()
        return r or True
    
    def _native(self): return f"select {self._ParseColumns()} from {self.sheetName}{self.where}{self._ParseOrder()}"
    def _deleteNative(self): return f"delete from {self.sheetName}{self.where}"
    def _updateNative(self, data:dict={}):
        data = ', '.join([f"{k}={v}" for k,v in data.items()]) or '____'
        return f"update {self.sheetName} set {data}{self.where}"


class MysqlColumn():
    id = None  # 字段提示
    def __getattribute__(self, field):
        return Filter(field=field)
    __getitem__ = __getattribute__

mc = MysqlColumn()


class MysqlFunc():
    # 函数名提示
    year = day = month = week = hour = None
    md5 = None
    round = ceil = floor = abs = least = greatest = sign = pi = None
    curdate = curtime = utcdata = utctime = now = localtime = None
    
    def __getattribute__(self, func):
        def builtFunc(*fields):
            return Filter(field=f"{func}({', '.join(fields)})")
        return builtFunc

mf = MysqlFunc()