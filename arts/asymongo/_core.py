from copy import deepcopy
from motor.motor_asyncio import AsyncIOMotorClient as MongoClient  # 代码提示

from arts.vtype import uniset, empset, SysEmpty, ToolPool, OrmIndexError


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

    def _deepcopy(self, obj):
        if obj in (uniset, empset):
            return obj
        return deepcopy(obj)

    def __and__(self, obj):  # 交集
        a = self._deepcopy(self.where)
        b = self._deepcopy(obj.where)
        if a is uniset: return Factory(b)
        if b is uniset: return Factory(a)
        if a and b:  # a和b有可能是empset
            if set(a) & set(b):
                return Factory({'$and': [a, b]})
            return Factory({**a, **b})
        return Factory(empset)
    
    def __or__(self, obj):  # 并集
        a = self._deepcopy(self.where)
        b = self._deepcopy(obj.where)
        if a is empset: return Factory(b)
        if b is empset: return Factory(a)
        if a is uniset or b is uniset:
            return Factory(uniset)
        return Factory({'$or': [a, b]})
    
    def __sub__(self, obj): return self & (~ obj)  # 差集

    def __invert__(self):  # 补集
        w = self.where
        if w is uniset: return Factory(empset)
        if w is empset: return Factory(uniset)
        return Factory({'$nor': [w]})
    
    def ParseWhere(self):
        where  = self._deepcopy(self.where)
        if where is uniset: return {}
        if where is empset: return {'$and': [{'a':1}, {'a':2}]}
        return where

class moBase():
    def __init__(self, *lis, **dic):
        self.lis = lis
        self.dic = dic

class containAll(moBase): ...
class containAny(moBase): ...
class containNo(moBase): ...
class isin(moBase): ...
class notin(moBase): ...
def re(s, i=False):
    if i:
        return {'$regex': s, '$options': 'i'}
    return {'$regex': s}


class Filter():
    _variable = True

    def __init__(self, field):
        self.field = field
        self._variable = False
    
    def __setattr__(self, name, value):
        assert self._variable
        object.__setattr__(self, name, value)
    
    def __getattr__(self, name): return Filter(f"{self.field}.{name}")
    def __lt__(self, obj): return Factory({self.field: {'$lt': obj}})  # <
    def __le__(self, obj): return Factory({self.field: {'$lte': obj}})  # <=
    def __gt__(self, obj): return Factory({self.field: {'$gt': obj}})  # >
    def __ge__(self, obj): return Factory({self.field: {'$gte': obj}})  # >=
    def __ne__(self, obj): return Factory({self.field: {'$ne': obj}})  # !=

    def __eq__(self, obj):
        if isinstance(obj, containAll):
            lis = obj.lis
            if len(lis) == 1: return Factory({self.field: {'$elemMatch':{'$eq':lis[0]}}})
            if len(lis) > 1: return Factory({'$and': [{self.field: {'$elemMatch':{'$eq':x}}} for x in set(lis)]})
            return Factory(uniset)
        
        elif isinstance(obj, containAny):
            lis = obj.lis
            if len(lis) == 1: return Factory({self.field: {'$elemMatch':{'$eq':lis[0]}}})
            if len(lis) > 1: return Factory({'$or': [{self.field: {'$elemMatch':{'$eq':x}}} for x in set(lis)]})
            return Factory(empset)
        
        elif isinstance(obj, containNo):
            lis = obj.lis
            if lis: return Factory({'$nor': [{self.field: {'$elemMatch':{'$eq':x}}} for x in set(lis)]})
            return Factory(uniset)
        
        elif isinstance(obj, isin):
            lis = obj.lis
            if not lis: return Factory(empset)
            if len(lis) == 1: return Factory({self.field: lis[0]})
            return Factory({self.field: {'$in': lis}})
        
        elif isinstance(obj, notin):
            lis = obj.lis
            if not lis: return Factory(uniset)
            if len(lis) == 1: return Factory({self.field: {'$ne': lis[0]}})
            return Factory({self.field: {'$nin': lis}})
        
        return Factory({self.field: obj})

class upList(): ...
class mup:
    class push(upList):  # 添加
        name = '$push'
        def __init__(self, *vs):
            self.value = {"$each":list(vs)}
    
    class add(upList):  # 不存在时才添加
        name = '$addToSet'
        def __init__(self, *vs):
            self.value = {"$each":list(vs)}

    class inc(upList):  # 自增:inc(1), 自减:inc(-1)
        name = '$inc'
        def __init__(self, value):
            self.value = value

    class pull(upList):  # 从数组field内删除一个等于value值
        name = '$pull'
        def __init__(self, value):
            self.value = value

    class rename(upList):  # 修改字段名称
        name = '$rename'
        def __init__(self, value):
            self.value = value

    class _(upList):  # 删除键
        name = '$unset'
        value = 1
    unset = delete = _()

    class _(upList):
        name = '$pop'
        def __init__(self, value):
            self.value = value
    popfirst = _(-1)  # 删除数组第1个元素, 和Python相反, -1代表最前面
    poplast = _(1)  # 删除数组最后1个元素


repairUpsert = False
# pymongo官方bug
# cannot infer query fields to set, path 'a' is matched twice, full error: {'index': 0, 'code': 54, 'errmsg': "cannot infer query fields to set, path 'a' is matched twice"}


class allColumns: ...


class makeSlice():
    def __init__(self, func, *vs, **kvs):
        self.func = func
        self.vs = vs
        self.kvs = kvs
    def __getitem__(self, key):
        return self.func(key, *self.vs, **self.kvs)
    

class sheetORM():
    _variable = True

    def __init__(self, connPool:ToolPool, dbName:str, sheetName:str, where=None, columns=allColumns, _sort=None):
        assert columns
        self.connPool = connPool
        self.dbName = dbName
        self.sheetName = sheetName
        self.where = where or Factory(uniset)
        self.columns = columns  # str型 或 tuple型 或 allColumns, 都是不可变的
        self._sort = deepcopy(_sort or {})
            # {A:True, B:False, C:1, D:0}
            # bool(value) == True 表示升序
            # bool(value) == False 表示降序
        self._variable = False

    def __setattr__(self, name, value):
        assert self._variable
        object.__setattr__(self, name, value)

    def __getattr__(self, name):
        conn:MongoClient = self.connPool.get()
        return conn[self.dbName][self.sheetName].__getattribute__(name)

    def __repr__(self):
        return f'coolmongo.sheetORM("{self.dbName}.{self.sheetName}")'
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

    def _ParseColumns(self):
        cols = self.columns
        if cols is allColumns: return None
        if isinstance(cols, tuple):
            cols = dict.fromkeys(cols, 1)
        else:
            cols = {cols:1}
        cols.setdefault('_id', 0)
        return cols

    def order(self, **rule): return self._copy(_sort={**rule})

    def _ParseOrder(self):
        if self._sort:
            return [(k, 1 if v else -1) for k,v in self._sort.items()]
        return []
    
    def insert(self, data):
        conn:MongoClient = self.connPool.get()
        sheet = conn[self.dbName][self.sheetName]
        if type(data) is dict:
            future = sheet.insert_one(data)
            # r = await sheet.insert(data)
            # r.inserted_id
        else:
            future = sheet.insert_many(data)
            # r = await sheet.insert([line1, line2])
            # r.inserted_ids
        self.connPool.put(conn)
        return future

    def delete(self):
        return makeSlice(self._deleteBase)

    async def _deleteBase(self, key):
        conn:MongoClient = self.connPool.get()
        sheet = conn[self.dbName][self.sheetName]
        # [::]
        if isinstance(key, slice):
            L, R, S = key.start, key.stop, key.step or 1
            if S in [None,1]:
                if (L in [None,1] and R in [None,-1]) or (L == -1 and R == 1):
                    r = await sheet.delete_many(ParseWhere(self))
                    self.connPool.put(conn)
                    return r
                    # r.acknowledged, r.deleted_count
        # [1]且无排序
        if key == 1 and not self._ParseOrder():
            r = await sheet.delete_one(ParseWhere(self))
            self.connPool.put(conn)
            return r
            # r.acknowledged, r.deleted_count
        # 其它情况
        try:
            ids = await self['_id'][key]
        except OrmIndexError:
            condition = Factory(empset).ParseWhere()
            r = await sheet.delete_one(condition)
            self.connPool.put(conn)
            return r
        else:
            if isinstance(ids, list):
                condition = (mc._id == isin(*ids)).ParseWhere()
                r = await sheet.delete_many(condition)
                self.connPool.put(conn)
                return r
            else:
                condition = (mc._id == ids['_id']).ParseWhere()
                r = await sheet.delete_one(condition)
                self.connPool.put(conn)
                return r

    def update(self, data:dict=None):
        return makeSlice(self._updateBase, data=data, default=None)
    
    async def _updateBase(self, key, data=None, default=None):
        data_ = {'$set':{}}
        for k,v in (data or {}).items():
            if isinstance(v, upList):
                data_.setdefault(v.name, {})[k] = v.value
            else:
                data_['$set'][k] = v
        conn:MongoClient = self.connPool.get()
        sheet = conn[self.dbName][self.sheetName]
        empsetCondi = Factory(empset).ParseWhere()
        # [::]
        if isinstance(key, slice):
            L, R, S = key.start, key.stop, key.step or 1
            if S in [None,1]:
                if (L in [None,1] and R in [None,-1]) or (L == -1 and R == 1):
                    r = await sheet.update_many(ParseWhere(self), data_)
                    if repairUpsert and not r.matched_count and default:
                        r = await sheet.update_many(empsetCondi, {'$setOnInsert':default}, upsert=True)
                    self.connPool.put(conn)
                    return r
                    # r.acknowledged, r.matched_count
                    # matched_count 与 modified_count 的区别:
                    ## matched_count 表示匹配到的数目, 如果是update_one, 则 matched_count in [0, 1]
                    ## modified_count 表示数据有变化的数目
                    ## 如果一条数据修改前和修改后一致(例如:把3修改成3), 则不会统计到modified_count中
        # [1]且无排序
        if key == 1 and not self._ParseOrder():
            r = await sheet.update_one(ParseWhere(self), data_)
            if repairUpsert and not r.matched_count and default:
                r = await sheet.update_one(empsetCondi, {'$setOnInsert':default}, upsert=True)
            self.connPool.put(conn)
            return r
            # r.acknowledged, r.matched_count
        # 其它情况
        try:
            ids = await self['_id'][key]
        except OrmIndexError:
            if repairUpsert and default:
                r = await sheet.update_one(empsetCondi, {'$setOnInsert':default}, upsert=True)
            else:
                r = await sheet.update_one(empsetCondi, {'$set':{}})
            self.connPool.put(conn)
            return r
        else:
            if isinstance(ids, list):
                if ids:
                    ids = [x['_id'] for x in ids]
                    condition = (mc._id == isin(*ids)).ParseWhere()
                    r = await sheet.update_many(condition, data_)
                    self.connPool.put(conn)
                    return r
                else:
                    if repairUpsert and default:
                        r = await sheet.update_many(empsetCondi, {'$setOnInsert':default}, upsert=True)
                    else:
                        r = await sheet.update_many(empsetCondi, {'$set':{}})
                    self.connPool.put(conn)
                    return r
            else:
                condition = (mc._id == ids['_id']).ParseWhere()
                r = await sheet.update_one(condition, data_)
                self.connPool.put(conn)
                return r
    
    async def len(self):
        conn:MongoClient = self.connPool.get()
        sheet = conn[self.dbName][self.sheetName]
        tatal = await sheet.count_documents(ParseWhere(self))
        self.connPool.put(conn)
        return tatal
    
    def get(self, index, default=None):
        try:
            return self[index]
        except IndexError:
            return default

    async def _find_one(self, key):
        index = key
        if index < 0: index = await self.len() + index + 1
        if index < 1: raise OrmIndexError(f"index({key}) out of range")
        skip = index - 1
        conn:MongoClient = self.connPool.get()
        sheet = conn[self.dbName][self.sheetName]
        sh = sheet.find(ParseWhere(self), self._ParseColumns())
        if sort:= self._ParseOrder():
            sh = sh.sort(sort)
        if skip: sh = sh.skip(skip)
        r = await sh.limit(1).to_list(1)
        self.connPool.put(conn)
        if r:
            return r[0]
        else:
            raise OrmIndexError(f"index({key}) out of range")
            # 没有的话引发OrmIndexError错误. 已被self.update和self.delete调用

    async def _find_many(self, key):
        # 没有的话返回空列表, 但不要报错. 已被self.update和self.delete调用
        L, R, S = key.start, key.stop, key.step or 1
        tL, tR, tS = type(L), type(R), type(S)
        assert {tL, tR, tS} <= {int, type(None)}
        assert 0 not in (L, R)
        assert S > 0
        lenSheet = float('inf')
        if '-' in f"{L}{R}":  # -是负号
            lenSheet = await self.len()
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
            conn:MongoClient = self.connPool.get()
            sheet = conn[self.dbName][self.sheetName]
            sh = sheet.find(ParseWhere(self), self._ParseColumns())
            if sort:= self._ParseOrder():
                sh = sh.sort(sort)
            if skip: sh = sh.skip(skip)
            if isinstance(size, int): sh = sh.limit(size)
            r = [x async for x in sh]
            self.connPool.put(conn)
            if sliceSort:
                if S == 1:
                    return r
                else:
                    return r[::S]
            else:
                return r[::-S]
        else:
            return []
    
    def __getitem__(self, key):
        # 索引取值
        if isinstance(key, int):
            return self._find_one(key)
        # 切片取值
        if isinstance(key, slice):
            return self._find_many(key)
        # 限定columns
        # 输入多个字符串, 用逗号隔开, Python会自动打包成tuple
        if isinstance(key, (str, tuple)) or key is allColumns:
            return self._copy(columns=key)
        # Factory
        if isinstance(key, Factory):
            return self._copy(where=self.where & key)
        raise TypeError(key)

def ParseWhere(obj:sheetORM):
    return obj.where.ParseWhere()

class dbORM():
    def __init__(self, connPool:ToolPool, dbName):
        self.connPool = connPool
        self.dbName = dbName

    def __getattr__(self, name):
        conn:MongoClient = self.connPool.get()
        return conn[self.dbName].__getattribute__(name)

    def __repr__(self):
        return f'coolmongo.dbORM("{self.dbName}")'
    __str__ = __repr__

    async def getSheetNames(self):
        conn:MongoClient = self.connPool.get()
        sheets = await conn[self.dbName].list_collection_names()
        self.connPool.put(conn)
        return sheets
    
    async def len(self): return len(await self.getSheetNames())

    async def delete_all_sheets(self):
        conn:MongoClient = self.connPool.get()
        db = conn[self.dbName]
        r = [await db.drop_collection(name) for name in db.list_collection_names()]
        self.connPool.put(conn)
        return r

    async def delete_sheets(self, *names):
        conn:MongoClient = self.connPool.get()
        db = conn[self.dbName]
        r = [await db.drop_collection(name) for name in names]
        self.connPool.put(conn)
        return r

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

class ORM():
    def __init__(self, mkconn):
        self.connPool = ToolPool(mktool=mkconn, minlen=1, maxlen=1)
        # 当增删改查报错时, conn不再放回连接池, 以避免含有残留数据

    def __getattr__(self, name):
        conn:MongoClient = self.connPool.get()
        return conn.__getattribute__(name)
    
    async def getDbNames(self):
        conn:MongoClient = self.connPool.get()
        dbs = await conn.list_database_names()
        self.connPool.put(conn)
        return dbs
    
    async def len(self): return len(await self.getDbNames())

    async def delete_all_dbs(self):
        conn:MongoClient = self.connPool.get()
        dbs:list = conn.list_database_names()
        try:
            dbs.remove('admin')
        except:
            pass
        r = [await conn.drop_database(dbName) for dbName in dbs]
        self.connPool.put(conn)
        return r

    async def delete_dbs(self, *names):
        conn:MongoClient = self.connPool.get()
        r = [await conn.drop_database(dbName) for dbName in names]
        self.connPool.put(conn)
        return r

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


class MongoColumn():
    _id = None  # 字段提示
    def __getattribute__(self, field):
        return Filter(field=field)
    __getitem__ = __getattribute__

mc = MongoColumn()  # 已被sheetORM.update和sheetORM.delete调用