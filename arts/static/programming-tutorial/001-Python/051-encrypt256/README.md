# 项目描述

str 型和 bytes 型数据加密器。

1、底层加密算法为 AES-CBC-256。

2、加密时，会自动创建随机 salt、随机 iv、原始明文的校验值，并把校验值添加到密文中。

3、解密时，会自动根据校验值校验“解密得到的明文”与“原始明文”是否一致。

# 作者信息

昵称：lcctoor.com

域名：lcctoor.com

邮箱：lcctoor@outlook.com

[主页](https://lcctoor.github.io/arts/) \| [微信](https://lcctoor.github.io/arts/arts/static/static-files/WeChatQRC.jpg) \| [Python交流群](https://lcctoor.github.io/arts/arts/static/static-files/PythonWeChatGroupQRC.jpg) \| [捐赠](https://lcctoor.github.io/arts/arts/static/static-files/DonationQRC-1rmb.jpg)

# Bug提交、功能提议

您可以通过 [Github-Issues](https://github.com/lcctoor/arts/issues)、[微信](https://lcctoor.github.io/arts/arts/static/static-files/WeChatQRC.jpg) 与我联系。

# 安装

```
pip install encrypt256
```

# 教程

#### 导入

```python
from encrypt256 import Encrypt256
```

#### 创建加密器

```python
password1 = 123456789  # 支持int型密钥
password2 = '黄河之水天上来'  # 支持str型密钥
password3 = '床前明月光'.encode('utf8')  # 支持bytes型密钥

enctool = Encrypt256(password1)  # 创建加密器
```

#### 加密

```python
p1 = '人生自古谁五死'  # 可加密str型数据
p2 = '莎士比亚'.encode('utf8')  # 可加密bytes型数据

c1 = enctool.encrypt(p1)
c2 = enctool.encrypt(p2)
```

#### 解密

```python
r1 = enctool.decrypt(c1)
r2 = enctool.decrypt(c2)

assert p1 == r1
assert p2 == r2
assert type(p1) is type(r1)
assert type(p2) is type(r2)
```

当发生以下情况时，会解密失败并报错：

1、密钥错误。

2、由于密文被篡改，导致 AES 算法解密失败。

3、由于密文被篡改，虽然 AES 算法解密成功，但校验值错误。
