import re


class Coolstr:

    string: str

    s_az = 'abcdefghijklmnopqrstuvwxyz'
    s_AZ = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    s_09 = '0123456789'
    s_09az = '0123456789abcdefghijklmnopqrstuvwxyz'
    s_09AZ = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    s_azAZ = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    s_09azAZ = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    
    def __init__(self, *args, **kwargs):
        self.string = str(*args, **kwargs)
    
    def __str__(self): return self.string
    
    @property
    def suffixes(self):
        '''
        Coolstr( '.a.json..ce.' ).suffixes
        >>> ['.a', '.json', '.', '.ce', '.']
        '''
        return re.findall(r'\.[^.]*', self.string)
    
    @property
    def suffix(self):
        '''
        # 当没有后缀时, 应该返回 '' 还是 None ?

            这两者的意义有很大的不同:

            如果返回 '', 说明这是一个空的后缀, 但它仍然是一个后缀. 既然它是一个后缀, 那么, 在获取 suffixes 时是否也要在列表中放一个空后缀 '' 呢?

            如果返回 None, 则说明没有后缀.

            决策: 返回 None
        '''
        if suffixes := self.suffixes:
            return suffixes[-1]
        else:
            return None
        
    @property
    def long_suffix(self):
        if suffix := re.findall(r'\..*', self.string):
            return suffix[0]
        else:
            return None
    
    def wash_paragraph(self):  # 单段清洗
        text = re.sub(r'\s+', ' ', self.string)
        text = re.sub(r'^ +', '', text)
        text = re.sub(r' +$', '', text)
        return text

    def visible(self):  # 是否含可视字符
        return bool(re.search(r'[^\s]', self.string))

    def has_sound(self):  # 是否含有有声字符(目前支持中文和英文)
        return bool(re.search(r'[\u4e00-\u9fa5\da-zA-Z]', self.string))

    def has_chinese(self):
        return bool(re.search(r'[\u4e00-\u9fa5]', self.string))

    def __contains__(self, string: str):
        return string in self.string