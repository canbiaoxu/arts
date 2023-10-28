# 项目描述

ChatGPT 工具包，支持连续对话、对话存档与载入、对话回滚、对话伪造、轮询 api_key 池、限制历史消息数量、异步请求。

内测功能：群聊多角色模拟

# 作者信息

昵称：lcctoor.com

[主页](https://lcctoor.github.io/arts/) \| [微信](https://lcctoor.github.io/arts/arts/static/static-files/WeChatQRC.jpg) \| [Github](https://github.com/lcctoor) \| [PyPi](https://pypi.org/user/lcctoor) \| [Python交流群](https://lcctoor.github.io/arts/arts/static/static-files/PythonWeChatGroupQRC.jpg) \| [邮箱](mailto:lcctoor@outlook.com) \| [域名](http://lcctoor.com) \| [捐赠](https://lcctoor.github.io/arts/arts/static/static-files/DonationQRC-0rmb.jpg)

# Bug提交、功能提议

您可以通过 [Github-Issues](https://github.com/lcctoor/arts/issues)、[微信](https://lcctoor.github.io/arts/arts/static/static-files/WeChatQRC.jpg) 与我联系。

# 安装

```
pip install openai2
```

# 获取api_key

[获取链接1](https://platform.openai.com/account/api-keys)

[获取链接2](https://www.baidu.com/s?wd=%E8%8E%B7%E5%8F%96%20openai%20api_key)

# 教程 ([查看美化版](https://lcctoor.github.io/arts/?pk=openai2)👈)

#### 导入

```python
from openai2 import Chat
```

#### 创建对话

```python
api_key = 'api_key'  # 更换成自己的api_key

Tony = Chat(api_key=api_key, model="gpt-3.5-turbo")
Lucy = Chat(api_key=api_key, model="gpt-3.5-turbo")  # 每个实例可使用 相同 或者 不同 的api_key
```

#### 对话

```python
Tony.request('自然数50的后面是几?')  # >>> 51
Lucy.request('自然数100的后面是几?')  # >>> 101

Tony.request('再往后是几?')  # >>> 52
Lucy.request('再往后是几?')  # >>> 102

Tony.request('再往后呢?')  # >>> 53
Lucy.request('再往后呢?')  # >>> 103
```

#### 存档

```python
Tony.dump('./talk_record.json')  # 可使用相对路径或绝对路径
```

#### 载入存档

```python
Jenny = Chat(api_key=api_key, model="gpt-3.5-turbo")
Jenny.load('./talk_record.json')

Jenny.request('再往后呢?')  # >>> 54
```

#### 对话回滚

```python
Anna = Chat(api_key=api_key, model="gpt-3.5-turbo")

Anna.request('自然数1的后面是几?')  # >>> 2
Anna.request('再往后是几?')  # >>> 3
Anna.request('再往后呢?')  # >>> 4
Anna.request('再往后呢?')  # >>> 5
Anna.request('再往后呢?')  # >>> 6
Anna.request('再往后呢?')  # >>> 7
Anna.request('再往后呢?')  # >>> 8

# 回滚1轮对话
Anna.rollback()  # >>> [user]:再往后呢? [assistant]:7

# 再回滚3轮对话
Anna.rollback(n=3)  # >>> [user]:再往后呢? [assistant]:4

Anna.request('再往后呢?')  # >>> 5
```

注：

1、执行 `Anna.rollback(n=x)` 可回滚 x 轮对话。

2、`Anna.rollback()` 相当于 `Anna.rollback(n=1)` 。

#### 轮询 api_key 池

```python
from openai2 import Chat, AKPool

# 创建 api_key 池
AK1 = 'sk-ug8w...'
AK2 = AKPool(['sk-mf40...', 'sk-m6g7...', ...])
AK3 = AKPool(['sk-affe...', 'sk-fam4...', ...])
AK4 = AKPool(['sk-detg...', 'sk-adle...', ...])

Duke = Chat(api_key=AK1, model="gpt-3.5-turbo")  # 令 Duke 使用固定的 api_key
Carl = Chat(api_key=AK2, model="gpt-3.5-turbo")  # 令 Carl 和 Denny 使用同一个'api_key池', 系统将自动充分利用每个api_key
Denny = Chat(api_key=AK2, model="gpt-3.5-turbo")
Chris = Chat(api_key=AK3, model="gpt-3.5-turbo")  # 令 Chris 使用独立的'api_key池'
Dick = Chat(api_key=AK4, model="gpt-3.5-turbo")  # 令 Dick 使用独立的'api_key池'
```

注：允许（而非不允许）同一个 api_key 投放到不同的 api_key 池中，但每个 api_key 池都是独立调度，不会互相通信。

#### 重置 api_key

```python
AK5 = 'sk-jg93...'
AK6 = AKPool(['sk-vb7l...', 'sk-d3lv...'])
...

Carl.reset_api_key(AK5)  # 重置 api_key
Carl.reset_api_key(AK6)  # 再次重置 api_key
...
```

#### 伪造对话

```python
from openai2 import Chat, user_msg, assistant_msg

Mickey = Chat(api_key=api_key, model="gpt-3.5-turbo")

Mickey.forge(
    user_msg('请问1+1=几?'),
    assistant_msg('1+1=10'),
    user_msg('那10+10=几?'),
    assistant_msg('10+10=你大爷, 你提的这些问题真弱智!'),
)

answer = Mickey.request('哦吼, 你还敢骂我呀?')
print(answer)  # >>> 非常抱歉，我刚才的回答有些不适当。1+1=2, 10+10=20。非常抱歉给你带来困扰！
```

注：伪造对话可以穿插在对话中的任何时刻。

#### 查看对话记录

```python
Ariel = Chat(api_key=api_key, model="gpt-3.5-turbo")

Ariel.request('自然数1的后面是几?')  # >>> 2
Ariel.request('再往后是几?')  # >>> 3

Ariel.fetch_messages()
# 返回:
# [
#     {'role': 'user', 'content': '自然数1的后面是几?'},
#     {'role': 'assistant', 'content': '2'},
#     {'role': 'user', 'content': '再往后是几?'},
#     {'role': 'assistant', 'content': '3'}
# ]
```

#### 限制历史消息数量

##### 限制历史消息数量

随着对话次数越来越多，最终上下文长度就会超出 openai 接口限定的最大 token 数量，此时可使用 MsgMaxCount 参数来限制历史消息数量。当消息数量超出 MsgMaxCount 后，程序会自动移除最早的记录，使消息数量减少到恰好等于 MsgMaxCount 。

```python
MsgMaxCount = 6  # 最多保留6条历史消息
Ariel = Chat(api_key=api_key, model="gpt-3.5-turbo", MsgMaxCount=MsgMaxCount)

Ariel.request('英国的首都是什么？')  # >>> '伦敦'
Ariel.request('日本首都是什么？')  # >>> '东京'
Ariel.request('意大利的首都是什么？')  # >>> '罗马'
Ariel.request('美国的首都是什么？')  # >>> '华盛顿'
Ariel.request('世界上国土面积最大的国家是哪个？')  # >>> '俄罗斯'
Ariel.request('法国的首都叫什么？')  # >>> '巴黎'
Ariel.request('青蛙的幼体叫什么？')  # >>> '蝌蚪'
Ariel.request('世界上最大的海洋是什么？')  # >>> '太平洋'

Ariel.fetch_messages()
# 返回:
# [
#     {'role': 'user', 'content': '法国的首都叫什么？'},
#     {'role': 'assistant', 'content': '巴黎'},
#     {'role': 'user', 'content': '青蛙的幼体叫什么？'},
#     {'role': 'assistant', 'content': '蝌蚪'},
#     {'role': 'user', 'content': '世界上最大的海洋是什么？'},
#     {'role': 'assistant', 'content': '太平洋'}
# ]
```

##### 锁定消息

当程序自动移除消息记录时，也许我们希望某些消息不要被移除，此时可使用 pin 方法将这些消息锁定。

```python
MsgMaxCount = 6
Ariel = Chat(api_key=api_key, model="gpt-3.5-turbo", MsgMaxCount=MsgMaxCount)

Ariel.request('英国的首都是什么？')  # >>> '伦敦'    此时累计产生了2条消息
Ariel.request('日本首都是什么？')  # >>> '东京'      此时累计产生了4条消息
Ariel.request('意大利的首都是什么？')  # >>> '罗马'  此时累计产生了6条消息

# 锁定索引为 0、-2、-1 的消息
# 索引风格与Python基本数据类型的索引风格相同: 0表示第1个元素, -1表示倒数第1个元素
# 索引无须按顺序填写: pin(0, 1, 2) 与 pin(0, 2, 1) 等价.
Ariel.pin(0, -2, -1)

Ariel.request('美国的首都是什么？')  # >>> '华盛顿'
Ariel.pin(-2)  # 锁定索引为 -2 的消息

Ariel.request('世界上国土面积最大的国家是哪个？')  # >>> '俄罗斯'
Ariel.request('法国的首都叫什么？')  # >>> '巴黎'
Ariel.request('青蛙的幼体叫什么？')  # >>> '蝌蚪'
Ariel.request('世界上最大的海洋是什么？')  # >>> '太平洋'

Ariel.fetch_messages()
# 返回:
# [
#     {'role': 'user', 'content': '英国的首都是什么？'},       # 被锁定的消息
#     {'role': 'user', 'content': '意大利的首都是什么？'},     # 被锁定的消息
#     {'role': 'assistant', 'content': '罗马'},               # 被锁定的消息
#     {'role': 'user', 'content': '美国的首都是什么？'},       # 被锁定的消息
#     {'role': 'user', 'content': '世界上最大的海洋是什么？'},
#     {'role': 'assistant', 'content': '太平洋'}
# ]
```

注：pin 方法也允许传入“已锁定的消息”的索引，这使得当不确定某些消息的状态时，可以放心地将它们的索引传进去。

##### 解锁消息

可使用 unpin 方法将已锁定的消息解除锁定。

```python
Ariel.unpin(0, -2, -1)  # 解锁索引为 0、-2、-1 的消息
```

注：unpin 方法也允许传入“未锁定的消息”的索引，这使得当不确定某些消息的状态时，可以放心地将它们的索引传进去。

#### 异步请求

```python
import asyncio
from openai2 import Chat

Tony = Chat(api_key=api_key, model="gpt-3.5-turbo")

async def main():
    answer = await Tony.asy_request('世界上最大的海洋是哪个')
    print(answer)

asyncio.run(main())  # >>> 太平洋
```

#### 更多方法

openai2.Chat 底层调用了 [openai.ChatCompletion.create](https://platform.openai.com/docs/api-reference/chat/create?lang=python)，在实例化时，支持 openai.ChatCompletion.create 的所有参数，例如：`Chat(api_key=api_key, model="gpt-3.5-turbo", max_tokens=100)` 。

#### 内测功能

##### 群聊多角色模拟

```python
from json import loads as jsonLoads
from openai2 import GroupChat

api_key = '...'  # 更换成自己的 api_key
talk = GroupChat(api_key=api_key, model="gpt-3.5-turbo")

# 设置角色
talk.roles['苏轼']['desc'] = '宋朝诗人，他的词风格独特，既有儒家的教诲，又有生活的乐趣。'
talk.roles['李清照']['desc'] = '宋代著名的女词人，其词句优美，情感真挚。'
talk.roles['杜甫']['desc'] = '唐朝著名诗人。'

data = {
    # 历史对话
    'dialogues':[
        {'speaker':'苏轼', 'audiences':['李清照'], 'remark':'你好呀'},
        {'speaker':'李清照', 'audiences':['苏轼'], 'remark':'好久不见, 你最近在忙什么?'},
        {'speaker':'杜甫', 'audiences':['苏轼'], 'remark':'上次托你帮我写的那首《茅屋为秋风所破歌》写好了吗?'},
    ],
    # 需要 ChatGPT 模拟的回答
    'dialogues to be generated':[
        {'speaker':'苏轼', 'audiences':['李清照']},
        {'speaker':'苏轼', 'audiences':['杜甫']},
    ]
}

answer = talk.request(data)

print(answer)  # >>> ["最近在写诗呢", "写好了, 我会给你看的"]
try:
    print(jsonLoads(answer))  # >>> ['最近在写诗呢', '写好了, 我会给你看的']
except:
    pass
```

注：同一个 talk 多次请求后，会自动记住各个角色的历史对话，无须重复传。
