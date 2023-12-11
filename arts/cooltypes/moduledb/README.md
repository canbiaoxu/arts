# 项目描述

为 Python 模块提供数据持久化支持。

# 安装

```
pip install arts
```

# 导入

```python
from arts.cooltypes import moduledb
```

# 为当前模块持久化数据

```python
db = moduledb.DB(__file__, depth=3)

city = db['泉州市']  # 第 1 层
school = city['希望小学']  # 第 2 层
wang = school['小王']  # 第 depth 层

wang['age'] = 18
wang['name'] = '小王'
wang.setdefault('性别', '男')

print(wang['name'])  # >>> '小王'
```

# 为其它模块持久化数据

```python
import requests

db = moduledb.DB(requests, depth=2)

city = db['上海市']  # 第 1 层
hong = city['小红']  # 第 depth 层

hong['age'] = 20
hong['name'] = '小红'
hong.setdefault('性别', '女')
hong.update({'爱好':'旅游', '身高':'170CM'})

print(hong['name'])  # '小红'
```
