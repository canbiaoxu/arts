import re


class coolstr:

    string: str

    def __init__(self, *s):
        self.string = str(s[0])
    
    @property
    def suffixes(self):
        '''
        coolstr( '.a.json..ce.' ).suffixes
        >>> ['.a', '.json', '.', '.ce', '.']
        '''
        return re.findall('\.[^.]*', self.string)
    
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
        if suffix := re.findall('\..*', self.string):
            return suffix[0]
        else:
            return None