# 项目描述

全球最优雅的 MongoDB ORM 。

# 作者信息

昵称：lcctoor.com

[主页](https://lcctoor.github.io/arts/) \| [微信](https://lcctoor.github.io/arts/arts/static/static-files/WeChatQRC.jpg) \| [Github](https://github.com/lcctoor) \| [PyPi](https://pypi.org/user/lcctoor) \| [Python交流群](https://lcctoor.github.io/arts/arts/static/static-files/PythonWeChatGroupQRC.jpg) \| [邮箱](mailto:lcctoor@outlook.com) \| [域名](http://lcctoor.com) \| [捐赠](https://lcctoor.github.io/arts/arts/static/static-files/DonationQRC-0rmb.jpg)

# Bug提交、功能提议

您可以通过 [Github-Issues](https://github.com/lcctoor/arts/issues)、[微信](https://lcctoor.github.io/arts/arts/static/static-files/WeChatQRC.jpg) 与我联系。

# 安装

```
pip install coolmongo
```

# [教程](https://lcctoor.github.io/arts?pk=coolmongo)👈

# 教程预览

#### 导入

```python
from pymongo import MongoClient
import coolmongo as mg
from coolmongo import mc, mup
```

#### 创建ORM

```python
mkconn = lambda: MongoClient(host='localhost', port=27017)

orm = mg.ORM(mkconn)  # 账户ORM
db = orm['city']  # 库ORM
sheet = db['school']  # 表ORM
```

#### 新增数据

```python
line1 = {'姓名': '小一', '年龄':11, '幸运数字':[1, 2, 3], '成绩':{'语文':81, '数学':82}}
line2 = {'姓名': '小二', '年龄':12, '幸运数字':[2, 3, 4], '成绩':{'语文':82, '数学':83}}
line3 = {'姓名': '小三', '年龄':13, '幸运数字':[3, 4, 5], '成绩':{'语文':83, '数学':84}}
line4 = {'姓名': '小四', '年龄':14, '幸运数字':[4, 5, 6], '成绩':{'语文':84, '数学':85}}
line5 = {'姓名': '小五', '年龄':15, '幸运数字':[5, 6, 7], '成绩':{'语文':85, '数学':86}}
line6 = {'姓名': '小六', '年龄':16, '幸运数字':[6, 7, 8], '成绩':{'语文':86, '数学':87}}

r1 = sheet + line1  # 添加1条数据
r2 = sheet + [line2, line3, line4, line5, line6]  # 批量添加
```

#### 查询

```python
sheet[:]  # 查询所有数据

sheet[3]  # 查询第3条数据

sheet[mc.成绩.语文 == 85][:]  # 查询语文成绩为85分的数据

sheet[mc.年龄>13][mc.姓名=='小五'][1]  # 查询年龄大于13、且姓名叫'小五'的第1条数据
```

#### 修改

```python
sheet[mc.年龄>10][2:5] = {
    '视力': 5.0,
    '性别': '男',
    '爱好': ['足球','篮球','画画','跳绳'],
    '幸运数字': mup.push(15,16,17),  # 添加到列表
    '年龄': mup.inc(2)  # 自增
}
```

#### 删除

```python
# 删除年龄>=15的数据
sheet[mc.年龄>=15][:] = None

# 删除年龄大于10、且姓名包含'小'的第2条数据
sheet[mc.年龄>10][mc.姓名 == mg.re('小')][2] = None

# 删除所有数据
sheet[:] = None
```

#### 比较运算

| 代码          |
| ------------- |
| mc.年龄 > 10  |
| mc.年龄 >= 10 |
| mc.年龄 < 10  |
| ...           |

#### 成员运算

| 代码                                     | 解释                                 |
| ---------------------------------------- | ------------------------------------ |
| mc.年级 == mg.isin('初三', '高二')       | 若字段值是传入值的成员，则符合       |
| mc.年龄 == mg.notin(10, 30, 45)          | 若字段值不是传入值的成员，则符合     |
| mc.爱好 == mg.containAll('画画', '足球') | 若字段值包含传入值的所有元素，则符合 |
| ...                                      | ...                                  |

#### 过滤器的集合运算

| 代码                                                                   | 解释 |
| ---------------------------------------------------------------------- | ---- |
| [ mc.年龄>3 ][ mc.年龄<100 ]                                           | 交集 |
| [ (mc.年龄<30) \| (mc.年龄>30) \| (mc.年龄==30) \| (mc.年龄==None) ] | 并集 |
| [ (mc.年龄>3) - (mc.年龄>100) ]                                        | 差集 |
| [ ~(mc.年龄>100) ]                                                     | 补集 |

#### 限定字段

只返回姓名、年龄这2个字段：

```python
sheet[mc.年级=='高一']['姓名','年龄'][:]
```

#### 特殊操作

| 代码             | 解释                                               |
| ---------------- | -------------------------------------------------- |
| mup.inc(1)       | 自增1                                              |
| mup.inc(-1)      | 自减1                                              |
| mup.add(1, 2, 3) | 向列表字段添加元素，仅当被添加的元素不存在时才添加 |
| ...              | ...                                                |
