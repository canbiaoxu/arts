一个用来对 字符串/列表/元组/数列 等数据按固定单元长度分组的功能：

```python
from skybox import sky_box


# 分字符串
data = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
sky_box(data, 3)  # >>> ['ABC', 'DEF', 'GHI', 'JKL', 'MNO', 'PQR', 'STU', 'VWX', 'YZ']


# 分列表
data = ['赤', '橙', '黄', '绿', '青', '蓝', '紫']
sky_box(data, 3)  # >>> [['赤', '橙', '黄'], ['绿', '青', '蓝'], ['紫']]


# 分元组
data = ('赤', '橙', '黄', '绿', '青', '蓝', '紫')
sky_box(data, 3)  # >>> [('赤', '橙', '黄'), ('绿', '青', '蓝'), ('紫',)]


# 分数列
data = range(1, 15)
sky_box(data, 3)  # >>> [range(1, 4), range(4, 7), range(7, 10), range(10, 13), range(13, 15)]
```
