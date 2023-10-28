# 项目描述

简单好用的异步 web 框架。

# 作者信息

昵称：lcctoor.com

[主页](https://lcctoor.github.io/arts/) \| [微信](https://lcctoor.github.io/arts/arts/static/static-files/WeChatQRC.jpg) \| [Github](https://github.com/lcctoor) \| [PyPi](https://pypi.org/user/lcctoor) \| [Python交流群](https://lcctoor.github.io/arts/arts/static/static-files/PythonWeChatGroupQRC.jpg) \| [邮箱](mailto:lcctoor@outlook.com) \| [域名](http://lcctoor.com) \| [捐赠](https://lcctoor.github.io/arts/arts/static/static-files/DonationQRC-0rmb.jpg)

# Bug提交、功能提议

您可以通过 [Github-Issues](https://github.com/lcctoor/arts/issues)、[微信](https://lcctoor.github.io/arts/arts/static/static-files/WeChatQRC.jpg) 与我联系。

# 教程

#### 导入

```python
import asyncio
from arts.coolapi import handler, creat_server
```

#### 一个最简单的例子

```python
class LoginHandler(handler):
    urls = ['/login/?']

    # url必须以'/'开头
    # '?'是正则表达式语法, 相当于 urls = ['/login', '/login/']

    async def get(self):
        return self.write('You are accessing the get method of login')
  
    async def post(self):
        return self.write('You are accessing the post method of login')

async def main():
    creat_server(handlers=[LoginHandler], port=5050)  # 启动http异步任务
    await asyncio.sleep( float('inf') )  # float('inf')表示无穷大

asyncio.run(main())

# 此时可在浏览器访问：
# http://localhost:5050/login
# http://localhost:5050/login/
```

#### 设置 cookie

```python
class PersonalHandler(handler):
    urls = ['/personal/?']

    async def get(self):
        self.set_cookie(name='username', value='tony')
        return self.write('Welcome to the personal center!')
```

#### 重定向

```python
def judge_login(self):
    ...

class PersonalHandler(handler):
    urls = ['/personal/?']

    async def get(self):
        if judge_login(self):
            return self.write('Welcome to the personal center!')
        else:
            return self.redirect('/login')  # 重定向到'/login'
```

#### 常用的视图操作

| 功能         | 代码                                           |
| ------------ | ---------------------------------------------- |
| 返回响应     | return self.write('......')                    |
| 设置 cookie  | self.set_cookie(name='username', value='tony') |
| 获取 cookie  | self.get_cookie(name='username')               |
| 重定向       | return self.redirect('/login')                 |
| 获取访客ip   | ip = self.get_ip( )                            |
| 获取请求数据 | body = self.get_body( )                        |

#### 使用通配路由

路由支持正则表达式，因此可实现通配路由：

```python
class ArticleHandler(handler):
    urls = ['/article/(\d+)/([a-z0-9]+)/?']

    async def get(self, userid, article_id):
        text = f"The article you are reading is '{article_id}' written by {userid}"
        return self.write(text)

# 运行后可在浏览器访问：
# http://localhost:5050/article/641872/r9mf44
# http://localhost:5050/article/740357/8d1h6d
# ...
```

```python
class DocumentionHandler(handler):
    urls = ['/documention/python([\d.]+)/?']

    async def get(self, version):
        text = f"You are reading the documentation for Python{version}"
        return self.write(text)

# 运行后可在浏览器访问：
# http://localhost:5050/documention/python3
# http://localhost:5050/documention/python3.9
# ...
```

#### 启动 http 服务

```python
class LoginHandler(handler):
    urls = ['/login/?']
    async def get(self):
        return self.write('You are accessing the get method of login')

class ArticleHandler(handler):
    ...

async def main():
    creat_server(
        handlers = [LoginHandler, ArticleHandler],  # 视图类列表
        port = 5050,  # 端口, 默认为80
        static_path = None,  # 静态文件服务, 默认为None
        debug = False,  # 启用调试模式, 默认为False
        
        # 支持更多参数, 可参考 https://www.tornadoweb.org/en/stable/web.html#tornado.web.Application
    )
  
    await asyncio.sleep(float('inf'))  # float('inf')表示无穷大

asyncio.run(main())
```

#### 更多用法

coolapi 是对 tornado 的二次封装，其中：

1、coolapi.handler（视图类）继承自 [tornado.web.RequestHandler](https://www.tornadoweb.org/en/stable/web.html#request-handlers)，可使用 tornado.web.RequestHandler 的任何功能。

2、creat_server 支持 [tornado.web.Application](https://www.tornadoweb.org/en/stable/web.html#tornado.web.Application) 的所有参数。
