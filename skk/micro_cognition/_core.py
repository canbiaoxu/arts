'''
基于微范式的 AI 推理模型
'''
import inspect, itertools
from collections import OrderedDict
from typing import Callable

def get_param_count(func) -> int:
    sig = inspect.signature(func)
    return sum(1 for p in sig.parameters.values() if p.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD))

def is_subclass(cls, class_or_tuple):
    return inspect.isclass(cls) and issubclass(cls, class_or_tuple)

paradigm_registry: OrderedDict|dict['Paradigm', None] = OrderedDict()  # 范式分布
object_registry: OrderedDict|dict['Obj', None] = OrderedDict()  # 对象分布

class Base:
    keywords: list[list[str]]

    @classmethod
    def match_likelihood(cls, question: str):
        for kw_list in cls.keywords:
            positions = [question.find(x) + 1 for x in kw_list]
            if all(positions):
                return min(positions)

class Paradigm(Base):
    '''
    范式类
    '''
    def __init_subclass__(cls):
        paradigm_registry[cls] = None
    reason: Callable

class Obj(Base):
    '''
    对象类
    '''
    def __init_subclass__(cls):
        object_registry[cls] = None

def memorize(*objs: Paradigm|Obj):
    for obj in objs:
        if is_subclass(obj, Paradigm):
            paradigm_registry.move_to_end(obj, last=False)
        elif is_subclass(obj, Obj):
            object_registry.move_to_end(obj, last=False)

def reasoning(question: str, iq: int = 100):
    def loop(used: list = None, base_objs: list[Obj] = None):
        used = used or []
        base_objs = base_objs or []

        cognition = [(p, p.match_likelihood(question)) for p in paradigm_registry][:iq * 100]
        cognition = [(a, b) for a, b in cognition if b]
        cognition.sort(key=lambda x: x[1])
        cognition = dict.fromkeys([a for a, b in cognition])
        for x in used: cognition.pop(x, 1)

        objs = [(o, o.match_likelihood(question)) for o in object_registry][:iq * 100]
        objs = [(a, b) for a, b in objs if b]
        objs.sort(key=lambda x: x[1])
        objs = dict.fromkeys([a for a, b in objs])
        for x in used: objs.pop(x, 1)

        for c in cognition:
            reason_func = c.reason
            combinations_list = itertools.combinations(objs, get_param_count(reason_func) - len(base_objs))
            for args in combinations_list:
                args = [*base_objs, *args]
                try:
                    result = reason_func(*args)
                except:
                    pass
                else:
                    if result:
                        memorize(*args)
                        if is_subclass(result, Obj):
                            return loop([c], [result]) or result
                        else:
                            return result
    result = loop(question)
    if is_subclass(result, Obj):
        return f"会变成{result.__name__}"
    else:
        return result
