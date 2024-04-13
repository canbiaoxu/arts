# 项目描述

Base95 是一种用 95 个可见的 ASCII 字符（含空格）表示任意二进制数据的编码方法。

该实现使用了从空格（ASCII 32）到波浪符（ASCII 126）这 95 个字符来编码二进制数据，用 67 个字符表示 55 个字节，编码后的信息密度高于 Base64 编码（Base64 编码用 4 个字符表示 3 个字节）。

# 作者

[江南雨上](mailto:lcctoor@outlook.com)

[主页](https://lcctoor.github.io/arts) \| [Github](https://github.com/lcctoor) \| [PyPi](https://pypi.org/user/lcctoor) \| [微信](https://lcctoor.github.io/arts/arts/ip_static/WeChatQRC.jpg) \| [邮箱](mailto:lcctoor@outlook.com) \| [捐赠](https://lcctoor.github.io/arts/arts/ip_static/DonationQRC-0rmb.jpg)

# Bug提交、功能提议

你可以通过 [Github-Issues](https://github.com/lcctoor/arts/issues)、[微信](https://lcctoor.github.io/arts/arts/ip_static/WeChatQRC.jpg) 与我联系。

# 安装

```
pip install base95
```

# 教程 ([查看美化版](https://lcctoor.github.io/arts/arts/base95) 👈)

本文将以最简洁的方式向你介绍核心知识，而不会让你被繁琐的术语所淹没。

## 导入

```python
from base95 import encode, decode
```

## 编码

```python
bytestring: bytes = '君不见黄河之水天上来'.encode('utf8')  # 建构一个字节串

encoded_text: str = encode(bytestring)  # 编码成 Base95
```

## 解码

```python
decoded_bytes: bytes = decode(encoded_text)  # 解码成字节串
```

# 与 Base64、Base85 比较编码后的信息密度

Base64 使用 4 个字符表示 3 个字节；

Base85 使用 5 个字符表示 4 个字节；

Base95 使用 67 个字符表示 55 个字节；

在这三种编码方法下分别计算 0~30M 区间内的字节串编码后的字符累计数量，以比较这三种方法编码后的信息密度：

```python
import math

char_unit_64 = 4
char_unit_85 = 5
char_unit_95 = 67

byte_unit_64 = int(math.log(64, 2**8) * char_unit_64)  # 3
byte_unit_85 = int(math.log(85, 2**8) * char_unit_85)  # 4
byte_unit_95 = int(math.log(95, 2**8) * char_unit_95)  # 55

size_64 = 0
size_85 = 0
size_95 = 0

for text_size in range(1, 1024 * 30 + 1):  # 迭代 0~30M 区间
    size_64 += math.ceil(text_size / byte_unit_64) * char_unit_64
    size_85 += math.ceil(text_size / byte_unit_85) * char_unit_85
    size_95 += math.ceil(text_size / byte_unit_95) * char_unit_95

print(size_95 / size_64)  # 值为 0.9151834585321867 , 说明 Base95 比 base64 节省约 8.5% 的空间
print(size_95 / size_85)  # 值为 0.976163916034696 , 说明 Base95 比 base85 节省约 2.4% 的空间
```
