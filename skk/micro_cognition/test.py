from skk.micro_cognition import Paradigm, Obj, reasoning

class 水(Obj):
    keywords = [
        ['水'],
        ['H2O'],
    ]

class 沸腾的水(Obj):
    keywords = [
        ['沸水'],
        ['沸腾', '水'],
        ['沸腾', 'H2O'],
    ]

class 脸(Obj):
    keywords = [
        ['脸'],
    ]

class 加热(Paradigm):
    keywords = [
        ['加热'],
        ['加温度'],
    ]
    @classmethod
    def reason(cls, obj: Obj):
        if issubclass(obj, 水): 
            return 沸腾的水

class 接触(Paradigm):
    keywords = [
        ['泼'],
    ]
    @classmethod
    def reason(cls, obj1: Obj, obj2: Obj):
        if {obj1, obj2} == {水, 脸}: 
            return '脸会变湿'
        if {obj1, obj2} == {沸腾的水, 脸}: 
            return '脸会被烫伤'

questions = [
    '把水加热',
    '把水泼脸上',
    '把水加热, 然后泼脸上',
]
for x in questions:
    print(reasoning(x))