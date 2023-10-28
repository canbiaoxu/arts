# 项目描述

全球最人性化的时间模块。

# 作者信息

昵称：lcctoor.com

[主页](https://lcctoor.github.io/arts/) \| [微信](https://lcctoor.github.io/arts/arts/static/static-files/WeChatQRC.jpg) \| [Github](https://github.com/lcctoor) \| [PyPi](https://pypi.org/user/lcctoor) \| [Python交流群](https://lcctoor.github.io/arts/arts/static/static-files/PythonWeChatGroupQRC.jpg) \| [邮箱](mailto:lcctoor@outlook.com) \| [域名](http://lcctoor.com) \| [捐赠](https://lcctoor.github.io/arts/arts/static/static-files/DonationQRC-0rmb.jpg)

# Bug提交、功能提议

您可以通过 [Github-Issues](https://github.com/lcctoor/arts/issues)、[微信](https://lcctoor.github.io/arts/arts/static/static-files/WeChatQRC.jpg) 与我联系。

# 安装

```
pip install cooltime
```

# 教程 ([查看美化版](https://lcctoor.github.io/arts/?pk=cooltime)👈)

#### 导入

```python
from cooltime import cooltime
```

#### 生成时间

```python
t1 = cooltime()  # 生成1个当前时间
t2 = cooltime.random()  # 生成1个随机时间
t3 = cooltime(1687271066.000028)  # 从时间戳生成
t4 = cooltime(1687271066)  # 从时间戳生成, 精确到秒
t5 = cooltime(t3)  # 从 cooltime 生成
t6 = cooltime('2023-06-20 22:24:26.000028')  # 从字符串生成
t7 = cooltime('2023-06-20 22:24:26')  # 从字符串生成, 精确到秒
t8 = cooltime('2023-06-20 22:24')  # 从字符串生成, 精确到分
t9 = cooltime('2023-06-20 22')  # 从字符串生成, 精确到时
t10 = cooltime('2023-06-20')  # 从字符串生成, 精确到日
t11 = cooltime([2023, 6, 20, 22, 24, 26, 28])  # 从其它类型生成, 如: list, tuple, datetime, time.localtime ……
```

注：

1、从字符串生成时，生成器会执行 `re.findall('\d+', text)[:7]` 提取前 7 个数字串来生成时间。因此字符串的格式可为任意，比如：`2023/06/20/22/24/26/000028` 、`2023_06_20_22_24_26_000028` 。

2、从 时间戳、cooltime、字符串 以外的其它类型生成时，生成器会先执行 `str(obj)` 将对象转化成字符串，然后按处理字符串的方式生成。

#### 将时间转化为其它类型

| 语法                             | 返回                         | 描述                       |
| -------------------------------- | ---------------------------- | -------------------------- |
| float( t3 )                      | 1687271066.000028            | 转化为时间戳               |
| int( t3 )                        | 1687271066                   | 转化为时间戳，精确到秒     |
| t3.date( )                       | '2023-06-20'                 | 提取日期字符串             |
| str( t3 )                        | '2023-06-20 22:24:26.000028' | 转化为时间字符串           |
| t3.floor( )                      | '2023-06-20 22:24:26'        | 转化为时间字符串，精确到秒 |
| t3.strftime("%Y-%m-%d %H:%M:%S") | '2023-06-20 22:24:26'        | 按指定格式转化为时间字符串 |
| t3.strftime("%Y_%m_%d %H_%M_%S") | '2023_06_20 22_24_26'        | 按指定格式转化为时间字符串 |

#### 比较时间大小

```python
# == 号
assert t3 == t5 == t6 == t11
assert t4 == t7

# > 号
assert t6 > t7 > t8 > t9 > t10

# < 号
assert t10 < t9 < t8 < t7 < t6

# >= 号
assert t3 >= t5 >= t6 >= t11
assert t4 >= t7
assert t6 >= t7 >= t8 >= t9 >= t10

# <= 号
assert t3 <= t5 <= t6 <= t11
assert t4 <= t7
assert t10 <= t9 <= t8 <= t7 <= t6
```

#### 时间的增量操作

```python
t26 = cooltime('2023-06-20 22:24:26')
t23 = t26 - 3  # 增量单位为秒
t29 = t26 + 3
print(t23)  # 2023-06-20 22:24:23
print(t29)  # 2023-06-20 22:24:29
print(t23 < t26 < t29)  # True
```
