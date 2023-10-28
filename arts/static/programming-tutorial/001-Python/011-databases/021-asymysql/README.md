# 项目描述

异步的 mysql ORM 。

# 作者信息

昵称：lcctoor.com

[主页](https://lcctoor.github.io/arts/) \| [微信](https://lcctoor.github.io/arts/arts/static/static-files/WeChatQRC.jpg) \| [Github](https://github.com/lcctoor) \| [PyPi](https://pypi.org/user/lcctoor) \| [Python交流群](https://lcctoor.github.io/arts/arts/static/static-files/PythonWeChatGroupQRC.jpg) \| [邮箱](mailto:lcctoor@outlook.com) \| [域名](http://lcctoor.com) \| [捐赠](https://lcctoor.github.io/arts/arts/static/static-files/DonationQRC-0rmb.jpg)

# Bug提交、功能提议

您可以通过 [Github-Issues](https://github.com/lcctoor/arts/issues)、[微信](https://lcctoor.github.io/arts/arts/static/static-files/WeChatQRC.jpg) 与我联系。

# 安装

```
pip install asymysql
```

# 教程 ([查看美化版](https://lcctoor.github.io/arts/?pk=asymysql)👈)

本文将以最简洁的方式向你介绍核心知识，而不会让你被繁琐的术语所淹没。

## 导入

```python
from aiomysql import connect
from asymysql import ORM, mc, mf
```

## 创建ORM

```python
async def mkconn():
    return await connect(
        host = 'localhost',
        port = 3306,
        user = 'root',
        password = '123456789'
    )

orm = await ORM(mkconn)  # 账户ORM
db = orm['泉州市']  # 库ORM
sheet = db['希望小学']  # 表ORM
```

## 新增数据

```python
line1 = {'姓名': '小一', '年龄':11, '签到日期':'2023-01-11'}
line2 = {'姓名': '小二', '年龄':12, '签到日期':'2023-01-12'}
line3 = {'姓名': '小三', '年龄':13, '签到日期':'2023-01-13'}
line4 = {'姓名': '小四', '年龄':14, '签到日期':'2023-01-14'}
line5 = {'姓名': '小五', '年龄':15, '签到日期':'2023-01-15'}
line6 = {'姓名': '小六', '年龄':16, '签到日期':'2023-01-16'}

r1 = await sheet.insert(line1)  # 添加1条数据
r2 = await sheet.insert([ line2, line3, line4, line5, line6 ])  # 批量添加
```

查看分配到的主键：

```python
r1.lastrowid
r2.lastrowid
```

## 查询示例

```python
await sheet[:]  # 查询所有数据

await sheet[3]  # 查询第3条数据

await sheet[mc.年龄>13][mc.姓名=='小五'][1]  # 查询年龄大于13、且姓名叫'小五'的第1条数据
```

注：后文有关于查询的详细教程。

## 修改

### 批量修改

```python
data = {
    '视力': 5.0,
    '性别': '男',
    '爱好': '足球,篮球,画画,跳绳'
}

r = await sheet[mc.年龄>11].update(data)[2:5]  # 修改符合条件的第2~5条数据

r.rowcount  # 查看修改详情
```

### 按主键修改

```python
data = {
    2: {'姓名':'xiao二', '年龄':20},
    3: {'年级':'三年级'},
    4: {'id':400, '视力':4.0}
}

await sheet.update_by_pk(data)
```

### 用自定义函数修改

```python
def handler(row:dict):
    row['年龄'] += 1  # 年龄统一加1岁
    if row['爱好'] == '打篮球':
        row['身高'] = 180
    elif row['爱好'] == '玩手机':
        row['视力'] = 1.8
    row['姓名'] = row['姓名'].replace('小', 'xiao')

await sheet[mc.年龄>11].apply(handler)[:]  # 修改符合条件的所有数据
await sheet[mc.年龄>11].apply(handler)[2:-2]  # 修改符合条件的第2条~倒数第2条
await sheet[mc.年龄>11].apply(handler)[2]  # 修改符合条件的第2条数据
```

注：

1、传递给 apply 方法的函数必须接收且仅接收1个参数，参数名可以不是‘row’。

2、可只提取需要的字段以提升性能。比如在上例中，handler 函数只使用到年龄、爱好、姓名这3个字段，可改为 `await sheet[mc.年龄>11]['年龄', '爱好', '姓名'].apply(handler)[:]` 以提高性能。

3、ORM 会自动对比修改前与修改后的数据差异，只提交差异部分到数据库。

## 删除

```python
# 删除年龄>=15的所有数据
r1 = await sheet[mc.年龄>=15].delete()[:]

# 删除年龄大于10、且喜欢足球的第2条数据
r2 = await sheet[mc.年龄>10][mc.爱好.re('足球')].delete()[2]

# 删除所有数据
r3 = await sheet.delete()[:]

# 查看删除详情
r1.rowcount
r2.rowcount
r3.rowcount
```

## 切片

1、切片格式为  [start: stop: step]  ，start 表示从哪条开始，stop 表示到哪条停止，step 表示步长。

2、start 和 stop

* 当为正值时，表示正序第 x 条，例如：1 表示第 1 条、2 表示第 2 条。
* 当为负值时，表示倒数第 x 条，例如：-1 表示倒数第 1 条、-2 表示倒数第 2 条。
* 不可为 0 。

3、step

* 须为正整数。
* 当 step >= 2  时表示间隔式切片。
* 当 step = 1 时可省略 `: step` ，即：[start: stop] 等价于 [start: stop: 1] 。

4、与 Python 切片风格对比

此 ORM 的切片风格比 Python 切片风格更人性化。具体区别为：

|                                        | **Python**                                            | **asymysql**                                         |
| -------------------------------------- | ----------------------------------------------------------- | ----------------------------------------------------------- |
| **索引**                         | 从 0 开始，例如：<br />[0] 表示第 1 个元素、[1] 表示第 2 个元素 | 从 1 开始，例如：<br />[1] 表示第 1 个元素、[2] 表示第 2 个元素 |
| **切片**                         | 左闭右开区间，例如：<br />[3: 5] 表示第 4~5 这 2 个元素     | 双闭区间，例如：<br />[3: 5] 表示第 3~5 这 3 个元素         |
| **从右往**<br />**左切片** | step 为负值，例如：<br />[9: 1: -1] 表示第 9~3 这 7 个元素 | step 为正值，例如：<br />[9: 1: 1] 表示第 9~1 这 9 个元素   |

### 示例

```python
await sheet[过滤器]...[过滤器][:]  # 查询符合条件的全部数据
await sheet[过滤器]...[过滤器][:] = None  # 删除符合条件的全部数据
await sheet[过滤器]...[过滤器][:] = {'年级':'初一'}  # 修改符合条件的全部数据

await sheet[过滤器]...[过滤器][1]  # 查询符合条件的第1条
await sheet[过滤器]...[过滤器][1] = None  # 删除符合条件的第1条
await sheet[过滤器]...[过滤器][1] = {'年级':'初一'}  # 修改符合条件的第1条

await sheet[过滤器]...[过滤器][3:7]  # 查询符合条件的第3~7条
await sheet[过滤器]...[过滤器][3:7] = None  # 删除符合条件的第3~7条
await sheet[过滤器]...[过滤器][3:7] = {'年级':'初一'}  # 修改符合条件的第3~7条

await sheet[过滤器]...[过滤器][3:7:2]  # 查询符合条件的第3、5、7条
await sheet[过滤器]...[过滤器][3:7:2] = None  # 删除符合条件的第3、5、7条
await sheet[过滤器]...[过滤器][3:7:2] = {'年级':'初一'}  # 修改符合条件的第3、5、7条
```

值得注意的地方：  [3: 8: 2]  操作第  3、5、7  条，而  [8: 3: 2]  操作第  8、6、4  条。

更多示例：

```python
[:]           # 所有数据
[1:-1]        # 所有数据
[-1:1]        # 所有数据（逆序）
[1:]          # 所有数据
[:1000]       # 第1条 ~ 第1000条
[:-1000]      # 第1条 ~ 倒数第1000条
[100:200]     # 第100条 ~ 第200条
[200:100]     # 第200条 ~ 第100条
[-300:-2]     # 倒数第300条 ~ 倒数第2条
[50:-2]       # 第50条 ~ 倒数第2条
[250:]        # 第250条 ~ 最后1条
[-250:]       # 倒数第250条 ~ 最后1条
[1]           # 第1条
[-1]          # 最后1条
[::3]         # 以3为间距, 间隔操作所有数据
[100:200:4]   # 以4为间距, 间隔操作第100条 ~ 第200条
```

## 过滤器

过滤器的结构为 `mc.<字段名称><运算符><值>` ，例如 `mc.年龄 > 18` 。

### 比较运算

| **代码** |
| -------------- |
| mc.年龄 > 10   |
| mc.年龄 >= 10  |
| mc.年龄 < 10   |
| mc.年龄 <= 10  |
| mc.年龄 == 10  |
| mc.年龄 != 10  |

### 成员运算

| **代码**               | **解释**                   |
| ---------------------------- | -------------------------------- |
| mc.年级.isin('初三', '高二') | 若字段值是传入值的成员，则符合   |
| mc.年龄.notin(10, 30, 45)    | 若字段值不是传入值的成员，则符合 |

注：

1、isin、notin 的传入值都不必是同类型的数据，以isin为例：可以这样使用：  mc.tag.isin(3, 3.5, '学生', None)  ，传入值含有int型、float型、str型、None。

2、成员运算符未传入任何值时的处理方式：

| **代码**   | **处理方式** |
| ---------------- | ------------------ |
| mc.年级.isin( )  | 所有数据都 不符合  |
| mc.年级.notin( ) | 所有数据都 符合    |

### 正则运算

| **代码**   |
| ---------------- |
| mc.姓名.re('小') |

### 过滤器的集合运算

| **代码**                                                       | **解释** |
| -------------------------------------------------------------------- | -------------- |
| [ mc.年龄>3 ][ mc.年龄<100 ]                                         | 交集           |
| [ (mc.年龄<30)\| (mc.年龄>30) \| (mc.年龄==30) \| (mc.年龄==None) ] | 并集           |
| [ (mc.年龄>3) - (mc.年龄>100) ]                                      | 差集           |
| [ ~(mc.年龄>100) ]                                                   | 补集           |

注：四种集合运算可以相互嵌套，且可以无限嵌套。

### 特殊字段名的表示方法

MySQL支持各种特殊的字段名，如：数字、符号、emoji表情，这些字符在Python中不是合法变量名，使用  mc.1、mc.+  等格式会报错，可用  mc['1']、mc['+']  这种格式代替。

### 字段提示

变量 mc 无字段提示功能，输入‘mc.’后，编辑器不会提示可选字段。后文有关于如何设置字段提示的内容。

## 查询

### 限定返回字段

只返回姓名、年龄这2个字段：

```python
await sheet[mc.年级=='高一']['姓名','年龄'][:]
```

注：

1、字段限定器可放在sheet与[:]之间的任意位置。以下3行代码的返回结果相同：

```python
await sheet[mc.年龄>11][mc.年龄<30]['姓名', '年龄'][:]
await sheet[mc.年龄>11]['姓名', '年龄'][mc.年龄<30][:]
await sheet['姓名', '年龄'][mc.年龄>11][mc.年龄<30][:]
```

2、可反复限定字段，查询时是根据最后1次指定的字段提取数据。以下代码返回结果中只有‘年龄’字段：

```python
await sheet[mc.年级=='高一']['姓名']['年龄'][:]
```

3、若想恢复提取全部字段，则限定字段为 '\*'  ，'\*'即代表“全部字段”。

```python
await sheet[mc.年级=='高一']['姓名']['*'][:]
```

（为什么有时候要先限定字段，然后再取消限定，而不是一开始就不限定字段？这是因为在某些场景中这样做可以使代码整体上更优雅。参见后文 [ 如何写出优雅的代码 ](#如何写出优雅的代码) ）

### 1个复杂的查询示例

```python
_ = sheet
_ = _[mc.年龄>=12]  # 比较
_ = _[mc.姓名.isin('小三','小四')]  # 被包含
_ = _[mc.姓名.notin('十三','十四')]  # 不被包含
_ = _[(mc.年龄==15) | (mc.年龄>15) | (mc.年龄<15)]  # 并集
_ = _[mc.年龄>=3][mc.年龄<100]  # 交集
_ = _[(mc.年龄>=3) - (mc.年龄>100)]  # 差集
_ = _[~ (mc.年龄>100)]  # 补集
_ = _[mc.姓名.re('小')]  # 正则表达式
await _[:]  # 切片
```

注：无论过滤器多复杂，ORM都不会访问数据库，只有在最后切片时，ORM才会访问数据库。

## 排序

对所有年级为“高一”的数据，优先按年龄降序，其次按姓名升序，排序后返回第2\~4条数据：

```python
await sheet[mc.年级=='高一'].order(年龄=False, 姓名=True)[2:4]
```

有趣的，以下两行代码的返回结果相同：

```python
await sheet[mc.年级=='高一'].order(年龄=True)[1:-1]

await sheet[mc.年级=='高一'].order(年龄=False)[-1:1]
```

解释：order(年龄=False)表示按年龄降序，[-1:1]表示逆序切片，产生了类似‘负负得正’的效果。

注：

1、排序器可放在sheet与[:]之间的任意位置。以下3行代码的返回结果相同：

```python
await sheet[mc.年级=='高一'][mc.视力>4.8].order(年龄=False)[2:4]
await sheet[mc.年级=='高一'].order(年龄=False)[mc.视力>4.8][2:4]
await sheet.order(年龄=False)[mc.年级=='高一'][mc.视力>4.8][2:4]
```

2、可反复排序，查询\|修改\|删除 时是根据最后1次指定的顺序提取数据。以下代码最终是按年龄降序后提取数据：

```python
await sheet.order(年龄=True, 姓名=False).order(年龄=False)[:]
```

3、若想取消排序，则再次调用order方法，但不传入任何值。

```python
await sheet.order(年龄=True, 姓名=False).order()[:]
```

（为什么有时候要先排序，然后再取消排序，而不是一开始就不排序？这是因为在某些场景中这样做可以使代码整体上更优雅。参见后文 [ 如何写出优雅的代码 ](#如何写出优雅的代码) ）

## 统计

| **项目**  | **语法**                 | **返回**                                          |
| --------------- | ------------------------------ | ------------------------------------------------------- |
| 主键            | await sheet.getPK( )           | 'id'                                                    |
| 所有字段        | await sheet.getColumns( )      | [{'name':'id', 'comment':'', 'type':'int'}, {...}, ...] |
| 数据总量        | await sheet.len( )             | 0                                                       |
| 年龄>10的数据量 | await sheet[mc.年龄>10].len( ) | 0                                                       |

## orm（账户ORM）

| **功能**   | **语法**          | **返回**                                                         |
| ---------------- | ----------------------- | ---------------------------------------------------------------------- |
| 获取所有库的名称 | await orm.getDbNames( ) | ['information_schema', 'mysql', 'performance_schema', 'sys', '泉州市'] |
| 统计库的数量     | await orm.len( )        | 5                                                                      |

## db（库ORM）

| **功能**   | **语法**            | **返回** |
| ---------------- | ------------------------- | -------------- |
| 获取所有表的名称 | await db.getSheetNames( ) | ['希望小学']   |
| 统计表的数量     | await db.len( )           | 1              |

## 调用mysql函数

调用mysql函数的语法为 `mf.<函数名称>(<参数>)<运算符><值>` 。

```python
# 在查询、删除、修改的条件中使用
await sheet[mf.year('签到日期') == 2023][:]
await sheet[mf.year('签到日期') == 2029].delete()[:]
await sheet[mf.year('签到日期') == 2023].update({'性别':'女'})[:]

# 在修改中作为新值
await sheet.update({'备注': '签到日期'})[:]  # 修改为'签到日期'这个字符串
await sheet.update({'备注': mc.签到日期})[:]  # 修改为各自的'签到日期'字段的值
await sheet.update({'备注': mf.year('签到日期')})[:]  # 修改为各自的'签到日期'字段的值经year处理后的值
```

使用该语法可调用mysql的任意函数。

ORM已添加了（20几个）mysql常用函数的函数名提示，输入‘mf.’后，编辑器会提示可选函数名。如有需要，可添加更多提示，参见后文 [ mysql函数名提示 ](#mysql函数名提示) 。（不添加提示也不会影响调用。）

## 执行原生SQL语句

```python
data, cursor = await sheet.execute('select 姓名 from 希望小学 limit 1')
data
# >>> [{'姓名': '小一'}]

data, cursor = await sheet.execute('update 希望小学 set 爱好="编程" limit 3')
cursor.rowcount
# >>> 3

data, cursor = await sheet.execute("delete from 希望小学 limit 2")
cursor.rowcount
# >>> 2

sql = 'insert into 希望小学(姓名, 年龄) values (%s, %s)'
students = [('小七', 17), ('小八', 18)]
data, cursor = await sheet.executemany(sql, students)
cursor.lastrowid
# >>> 8
```

## 关闭mysql连接

对 orm、db、sheet 中的任意一个调用 close( ) 方法即可。

```python
await orm.close()

# 或者：
await db.close()

# 或者:
await sheet.close()
```

注：

1、关闭 mysql 连接后，orm、db、sheet 都可以再使用。当再次使用时，ORM 会调用 mkconn 方法创建一个新连接。

2、调用 orm.close( )、db.close( )、sheet.close( )  中的 1 个即可。若多次调用，ORM 会创建一个新连接，然后再关闭这个新连接。

3、若长时间没有调用 orm、db、sheet 中的任意一个，mysql 连接也会断开，这是 mysql 自身的机制。这不会影响这三者的后续使用，当再次调用它们时，ORM 会自动重新连接 mysql 。

## 代码提示

### 字段提示

变量 mc 无字段提示功能，输入‘mc.’后，编辑器不会提示可选字段。

为了获得字段提示功能，可自建一个‘mc2’：

```python
from asymysql import MysqlColumn

class MC2(MysqlColumn):
    姓名 = 年龄 = 签到日期 = 年级 = 爱好 = None

mc2 = MC2()

await sheet[mc2.年龄 > 10][:]
```

注：

1、mc2 与 mc 用法完全一致，可混用。

2、mc2 设置字段提示后，仅具备提示效果，而不产生任何实际约束。

### mysql函数名提示

ORM已添加了（20几个）mysql常用函数的函数名提示，输入‘mf.’后，编辑器会提示可选函数名。如有需要，可添加更多提示：

```python
from asymysql import MysqlFunc

class MF2(MysqlFunc):
    reverse = length = lower = upper = None

mf2 = MF2()

await sheet[mf2.reverse('姓名') == '二小'][:]
```

注：

1、mf2 与 mf 用法完全一致，可混用。

2、mf2 设置函数名提示后，仅具备提示效果，而不产生任何实际约束。

## 表ORM的独立性

### 表ORM的独立性

先看一条查询示例：

```python
await sheet[mc.年龄 > 5]['姓名','年龄'][mc.姓名.re('小')].order(id=False)[:]
```

以上示例代码可改为如下（两者效果相同）：

```python
d1 = sheet
d2 = d1[mc.年龄 > 5]
d3 = d2['姓名','年龄']
d4 = d3[mc.姓名.re('小')]
d5 = d4.order(id=False)
await d5[:]
```

以上代码中，d1\~d5是5个不同的表ORM，它们具有独立的数据空间（存放着过滤条件、字段限定、排序等信息），且互不干扰。d2\~d5每个都拷贝了前一个ORM的表空间，并增加了自身的新信息。

### 如何写出优雅的代码

利用表ORM的独立性，可以在一些复杂的场景中写出优雅简洁的代码。

不优雅的示范：

```python
def GetName():
    return requests.get('https://...').text

def output(datas):
    ...

while True:
    datas = await sheet[过滤器1][过滤器2]...[过滤器9][mc.name == GetName()][:]
    output(datas)
```

优雅的示范：

```python
def GetName():
    return requests.get('https://...').text

def output(datas):
    ...

baseSheet = sheet[过滤器1][过滤器2]...[过滤器9]
while True:
    datas = await baseSheet[mc.name == GetName()][:]
    output(datas)
```
