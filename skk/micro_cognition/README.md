# 描述

一个基于微范式的 AI 推理模型。

# 教程

本文将以简洁的方式向你介绍核心知识，而不会让你被繁琐的术语所淹没。

## 安装

```bash
pip install https://github.com/canbiaoxu/skk/archive/refs/heads/main.zip
```

## 导入

```python
from skk.micro_cognition import (
    Paradigm,  # 范式类
    Obj,  # 对象类
    reasoning,  # 推理引擎
)
```

## 尝试推理: `把水泼脸上`

```python
question = '把水泼脸上'
print(reasoning(question))  # >>> None
```

由于我们尚未创建任何范式和对象, 所以推理结果为None.

## 建模并推理: `把水泼脸上`

```python
# 创建水对象
class 水(Obj):
    keywords = [
        ['水'],
        ['H2O'],
    ]

# 创建脸对象
class 脸(Obj):
    keywords = [
        ['脸'],
    ]

# 创建范式
class 接触(Paradigm):
    keywords = [
        ['泼'],
    ]
    @classmethod
    def reason(cls, obj1, obj2):
        if {obj1, obj2} == {水, 脸}:
            return '脸会变湿'

# 推理
print(reasoning('把水泼脸上'))  # >>> '脸会变湿'
print(reasoning('泼脸上, 用水'))  # >>> '脸会变湿'
```

## 增量建模并推理: `把沸腾的水泼脸上`

```python
# 创建沸水对象
class 沸腾的水(Obj):
    keywords = [
        ['沸水'],
        ['沸腾', '水'],
        ['沸腾', 'H2O'],
    ]

# 更新接触范式
class 接触(Paradigm):
    keywords = [
        ['泼'],
    ]
    @classmethod
    def reason(cls, obj1, obj2):
        if {obj1, obj2} == {水, 脸}:
            return '脸会变湿'
        # 新增以下代码
        if {obj1, obj2} == {沸腾的水, 脸}:
            return '脸会被烫伤'

print(reasoning('把沸腾的水泼脸上'))  # >>> '脸会被烫伤'
print(reasoning('泼脸上, 用沸腾的水'))  # >>> '脸会被烫伤'
```

## 尝试推理: `把水加热, 然后泼脸上`

```python
print(reasoning('把水加热, 然后泼脸上'))  # >>> '脸会变湿'
```

由于我们尚未创建 `水->加热->沸水` 的范式, 所以推理结果仍为 `脸会变湿` .

## 增量建模并推理: `把水加热, 然后泼脸上`

```python
# 创建加热范式
class 加热(Paradigm):
    keywords = [
        ['加热'],
        ['加温度'],
        ['提高温度'],
    ]
    @classmethod
    def reason(cls, obj):
        if issubclass(obj, 水): 
            return 沸腾的水

print(reasoning('把水加热, 然后泼脸上'))  # >>> '脸会被烫伤'
print(reasoning('加热水, 然后泼脸上'))  # >>> '脸会被烫伤'
```
