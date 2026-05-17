# 描述

ChatGPT 工具包，支持多模态对话（gpt-4o）、连续对话、流式对话（逐字显示）、生成图像（DALL·E）、对话存档与载入、对话回滚、对话伪造、轮询 api_key 池、群聊多角色模拟、限制历史消息数量、异步请求。

# 安装

```
pip install https://github.com/canbiaoxu/skk/archive/refs/heads/main.zip
```

# [获取api_key](https://platform.openai.com/account/api-keys)

# 教程

## 导入

```python
from skk.openai import Chat
```

## 创建对话

```python
api_key = 'api_key'  # 更换成自己的api_key

Tony = Chat(api_key=api_key, model="gpt-3.5-turbo")
Lucy = Chat(api_key=api_key, model="gpt-3.5-turbo")  # 每个实例可使用 相同 或者 不同 的api_key
```

## 对话

```python
Tony.request('自然数50的后面是几?')  # >>> '51'
Lucy.request('自然数100的后面是几?')  # >>> '101'

Tony.request('再往后是几?')  # >>> '52'
Lucy.request('再往后是几?')  # >>> '102'

Tony.request('再往后呢?')  # >>> '53'
Lucy.request('再往后呢?')  # >>> '103'
```

## 流式对话

```python
for answer in Lucy.stream_request('世界上最大的海洋是哪个?'):
    print(answer)
世
界
上
最
大
的
海
洋
是
太
平
洋
。
```

## 异步对话

```python
import asyncio
from skk.openai import Chat

Tony = Chat(api_key=api_key, model="gpt-3.5-turbo")

async def main():
    answer = await Tony.async_request('世界上最大的海洋是哪个')
    print(answer)

asyncio.run(main())  # >>> '世界上最大的海洋是太平洋。'
```

## 异步流式对话

```python
async for answer in Tony.async_stream_request('世界上最大的海洋是哪个?'):
    print(answer)
世
界
上
最
大
的
海
洋
是
太
平
洋
。
```

## 多模态对话（gpt-4o）

```python
from pathlib import Path
from skk.openai import Chat, Multimodal_Part


Bruce = Chat(api_key='sk-jg93...', model="gpt-4o")


pic = Path(rf'C:\鼠标.jpeg').read_bytes()

answer = Bruce.request(

    '下面这张图片里画了什么？',
  
    Multimodal_Part.jpeg(pic)
)

print(answer)  # >>> '这张图片里画了一个鼠标。'
```

注：

1、Multimodal_Part 除了 jpeg 方法以外，还有 png、text …… 等方法。

2、对于 str 型对象，以下这两种写法是等价的：`Bruce.request(..., '这张图片里画了什么', ...)`、`Bruce.request(..., Multimodal_Part.text('这张图片里画了什么'), ...)`。

3、多模态对话支持同步对话、异步对话、同步流式对话、异步流式对话…… 相对于普通对话，唯一的区别就是支持多模态。

4、目前已知支持多模态对话的模型有：gpt-4o、gpt-4o-mini、gpt-4o-2024-05-13、gpt-4o-mini-2024-07-18。

## 对话回滚

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

## 轮询 api_key 池

```python
from skk.openai import Chat, AKPool

AK1 = 'sk-ug8w...'
AK2 = AKPool(['sk-mf40...', 'sk-m6g7...', ...])
AK3 = AKPool(['sk-affe...', 'sk-fam4...', ...])

Duke = Chat(api_key=AK1, model="gpt-3.5-turbo")  # 令 Duke 使用固定的 api_key

Carl = Chat(api_key=AK2, model="gpt-3.5-turbo")  # 令 Carl 和 Denny 使用同一个'api_key池', 系统将自动充分利用每个api_key
Denny = Chat(api_key=AK2, model="gpt-3.5-turbo")

Chris = Chat(api_key=AK3, model="gpt-3.5-turbo")  # 令 Chris 使用独立的'api_key池'
```

注：允许（而非不允许）同一个 api_key 投放到不同的 api_key 池中，但每个 api_key 池都是独立调度，不会互相通信。

## 重置 api_key

```python
AK5 = 'sk-jg93...'
AK6 = AKPool(['sk-vb7l...', 'sk-d3lv...'])
...

Carl.reset_api_key(AK5)  # 重置 api_key
Carl.reset_api_key(AK6)  # 再次重置 api_key
...
```

## 对话导出与导入

### 对话导出

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

### 对话存档

你可以把导出的对话持久化保存：

```python
import json
from pathlib import Path

record = Ariel.fetch_messages()
record = json.dumps(record, ensure_ascii=False)
Path('record.json').write_text(record, encoding="utf8")
```

### 对话导入

导出的对话可以再导入到其他对话中：

```python
record = Ariel.fetch_messages()

Jenny = Chat(api_key=api_key, model="gpt-3.5-turbo")
Jenny.add_dialogs(*record)

Jenny.request('再往后呢?')  # >>> 4
```

导出的对话也可以再导入到原对话中，但这样做会在原对话中产生重复的历史消息。

### 对话伪造

利用对话导入功能，可以伪造对话：

```python
from skk.openai import Chat, user_msg, assistant_msg

Mickey = Chat(api_key=api_key, model="gpt-3.5-turbo")

Mickey.add_dialogs(
    user_msg('请问1+1=几?'),  # 等价于 {"role": "user", "content": '请问1+1=几?'}
    assistant_msg('1+1=10'),  # 等价于 {"role": "assistant", "content": '1+1=10'}
    {"role": "user", "content": '那10+10=几?'},
    {"role": "assistant", "content": '10+10=你大爷, 你提的这些问题真弱智!'},
)

answer = Mickey.request('哦吼, 你还敢骂我呀?')
print(answer)  # >>> 非常抱歉，我刚才的回答有些不适当。1+1=2, 10+10=20。非常抱歉给你带来困扰！
```

注：对话导出与导入可以穿插在对话中的任何时刻。

## 生成图像（DALL·E）

返回图片的二进制：

```python
from pathlib import Path
from skk.openai import Chat

Tony = Chat(api_key='sk-jg93...', model="dall-e-2")

images = Tony.dalle('请画一只猫', image_count=2)

for i, x in enumerate(images):
    Path(f"第{i}张.png").write_bytes(x)
```

返回图片的URL：

```python
from skk.openai import Chat

Tony = Chat(api_key='sk-jg93...', model="dall-e-2")

images = Tony.dalle('请画一只猫', image_count=2, return_format='url')

for i, url in enumerate(images):
    print(f"第{i}张的URL是：", url)
```

## 异步生成图像（DALL·E）

返回图片的二进制：

```python
import asyncio
from pathlib import Path
from skk.openai import Chat

async def main():
    Tony = Chat(api_key='sk-jg93...', model="dall-e-2")

    images = await Tony.async_dalle('请画一只猫', image_count=2)
  
    for i, x in enumerate(images):
        Path(f"第{i}张.png").write_bytes(x)

asyncio.run(main())
```

返回图片的URL：

```python
import asyncio
from skk.openai import Chat

async def main():
    Tony = Chat(api_key='sk-jg93...', model="dall-e-2")

    images = await Tony.async_dalle('请画一只猫', image_count=2, return_format='url')
  
    for i, url in enumerate(images):
        print(f"第{i}张的URL是：", url)

asyncio.run(main())
```

## 群聊多角色模拟

```python
import json
from skk.openai import GroupChat

api_key = '...'  # 更换成自己的 api_key
group = GroupChat(api_key=api_key, model="gpt-3.5-turbo")

# 设置角色
group.roles['苏轼'] = '宋朝诗人，他的词风格独特，既有儒家的教诲，又有生活的乐趣。'
group.roles['李清照'] = '宋代著名的女词人，其词句优美，情感真挚。'
group.roles['杜甫'] = '唐朝著名诗人。'

# 添加角色历史对话
group.add_dialog(speaker='苏轼', audiences=['李清照'], remark='你好呀')
group.add_dialog(speaker='李清照', audiences=['苏轼'], remark='好久不见, 你最近在忙什么?')
group.add_dialog(speaker='杜甫', audiences=['苏轼'], remark='上次托你帮我写的那首《茅屋为秋风所破歌》写好了吗?')

# 让 ChatGPT 模拟角色发言
answer = group.request([
    ('苏轼', ['李清照']),  # 第 1 个元素表示说话人, 第 2 个元素表示对谁说话. 由于一个人可以同时对多个人说话, 因此第 2 个元素为列表
    ('苏轼', ['杜甫']),
])

try:
    print( json.loads(answer) )
except:
    print(answer)

# 返回:
[
    {
        "speaker": "苏轼",
        "audiences": "李清照",
        "remark": "最近我在写一首新的诗，题目是《听雨》"
    },
    {
        "speaker": "苏轼",
        "audiences": "杜甫",
        "remark": "那首《茅屋为秋风所破歌》已经写好啦，我在信里寄给你了，请查收"
    }
]
```

## 限制历史消息数量

### 限制历史消息数量

随着对话次数越来越多，最终上下文长度就会超出 openai 接口限定的最大 token 数量，此时可使用 msg_max_count 参数来限制历史消息数量。当消息数量超出 msg_max_count 后，程序会自动移除最早的记录，使消息数量减少到恰好等于 msg_max_count 。

```python
msg_max_count = 6  # 最多保留6条历史消息

Ariel = Chat(api_key=api_key, model="gpt-3.5-turbo", msg_max_count=msg_max_count)

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

### 锁定消息

当程序自动移除消息记录时，也许我们希望某些消息不要被移除，此时可将这些消息锁定。

```python
msg_max_count = 6

Ariel = Chat(api_key=api_key, model="gpt-3.5-turbo", msg_max_count=msg_max_count)

Ariel.request('英国的首都是什么？')  # >>> '伦敦'
Ariel.request('日本首都是什么？')  # >>> '东京'
Ariel.request('意大利的首都是什么？')  # >>> '罗马'
```

此时共有 6 条消息记录：

| 消息                 | 正序索引 | 逆序索引 |
| -------------------- | :------: | :------: |
| 英国的首都是什么？   |    0    |    -6    |
| 伦敦                 |    1    |    -5    |
| 日本首都是什么？     |    2    |    -4    |
| 东京                 |    3    |    -3    |
| 意大利的首都是什么？ |    4    |    -2    |
| 罗马                 |    5    |    -1    |

锁定索引为 0、-2、-1 的消息：

```python
Ariel.pin_messages(0, -2, -1)  # 索引无须按顺序填写: pin_messages(0, 1, 2) 与 pin_messages(0, 2, 1) 等价.
```

继续请求：

```python
Ariel.request('美国的首都是什么？')  # >>> '华盛顿'
```

由于设置了 msg_max_count = 6，此时共有 6 条消息记录：

| 消息                 | 正序索引 | 逆序索引 | 锁定状态 |
| -------------------- | :------: | :------: | :------: |
| 英国的首都是什么？   |    0    |    -6    |  已锁定  |
| 东京                 |    1    |    -5    |    -    |
| 意大利的首都是什么？ |    2    |    -4    |  已锁定  |
| 罗马                 |    3    |    -3    |  已锁定  |
| 美国的首都是什么？   |    4    |    -2    |    -    |
| 华盛顿               |    5    |    -1    |    -    |

继续执行：

```python
Ariel.pin_messages(-2)  # 锁定'美国的首都是什么？'

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

注：pin_messages 方法也允许传入“已锁定的消息”的索引，这使得当不确定某些消息的状态时，可以放心地将它们的索引传进去。

### 解锁消息

可使用 unpin_messages 方法将已锁定的消息解除锁定。

```python
Ariel.unpin_messages(0, -2, -1)  # 解锁索引为 0、-2、-1 的消息
```

注：unpin_messages 方法也允许传入“未锁定的消息”的索引，这使得当不确定某些消息的状态时，可以放心地将它们的索引传进去。

## 更多方法

1、`openai.Chat` 底层调用了 `openai.OpenAI`，支持 `openai.OpenAI` 的所有参数。

2、`openai.Chat.request` 与 `openai.Chat.stream_request` 底层调用了 `openai.OpenAI.chat.completions.create`，支持 `openai.OpenAI.chat.completions.create` 的所有参数。

3、`openai.Chat.async_request` 与 `openai.Chat.async_stream_request` 底层调用了 `openai.AsyncOpenAI.chat.completions.create`，支持 `openai.AsyncOpenAI.chat.completions.create` 的所有参数。

[查看相关参数](https://platform.openai.com/docs/api-reference/chat) 👈
