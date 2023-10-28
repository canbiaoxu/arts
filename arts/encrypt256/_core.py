from hashlib import shake_256
from random import randbytes
from pathlib import Path as libpath
from Crypto.Cipher.AES import new as AesNew  # pip install pycryptodome
from Crypto.Cipher.AES import MODE_CBC
from typing import Union


assert bytes(range(256)) == b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~\x7f\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf\xb0\xb1\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xbb\xbc\xbd\xbe\xbf\xc0\xc1\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf\xd0\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xdb\xdc\xdd\xde\xdf\xe0\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xeb\xec\xed\xee\xef\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff'


def _EncodeKey(version, key):
    if version in [1]:
        if type(key) is bytes: return key
        if type(key) is str: return key.encode('utf8')
        if type(key) is int: return str(key).encode('utf8')
        raise TypeError(key)
    raise ValueError(version)

def _padding(text):
    dsize = 16 - len(text) % 16
    text += chr(dsize).encode('utf8') * dsize
    return text

def _invertPadding(text):
    # CBC的_padding区块为16字节(<=127字节), 在此范围内可直接使用text[-1]来知道填充了多少
    return text[:-text[-1]]

def _encodePtext(version, text):  # 用于加密时
    if version in [1]:
        if type(text) is bytes: return 1, text
        if type(text) is str: return 2, text.encode('utf8')
        raise TypeError(text)
    raise ValueError(version)

def _decodePtext(version, ptype, plaTextCode:bytes):
    if version in [1]:
        if ptype == 1: return plaTextCode
        if ptype == 2: return plaTextCode.decode('utf8')
        raise TypeError(ptype)
    raise ValueError(version)


class Encrypt256():
    version = 1

    def __init__(self, password: Union[bytes, str, int]):
        self._versionKeys = {v: _EncodeKey(v, password) for v in range(1, self.version+1)}
            # 密钥可以是 bytes、str、int 类型，程序将自动转化为bytes型
            # 密钥允许使用空字符和空字节

    def encrypt(self, text: Union[bytes, str], checkSize: int=8):
        if not 0 <= checkSize <= 255:
            raise ValueError("校验值长度须介于[0, 255]")
            # 超出此范围需要使用2个字节来存储checkSize, 会使算法变复杂
        ptype, text = _encodePtext(self.version, text)
        saltSize = 32
        salt = randbytes(saltSize)
            # 加盐是为了防止使用同一密钥加密相同明文时, 得到的密文相同.
            # AES本身需要传递的IV, 则通过hash(密钥+盐)生成.
            # 相比直接产生随机IV, 好处是可以节省存储checkSalt的空间.
        password = self._versionKeys[self.version]
        KeyIvCksalt = shake_256(password + salt).digest(80)  # shake_256支持根据空字节(b'')生成哈希
        cbckey = KeyIvCksalt[:32]
        iv = KeyIvCksalt[32:48]
        if checkSize:
            checkSalt = KeyIvCksalt[48:]
            check = shake_256(checkSalt + text).digest(checkSize)
            # 之所以添加 checkSalt, 是为了防止校验值恰好就是另一个加密的密钥
            # 也即: 防止要加密的明文正是另一个哈希加密的密钥
        else:
            check = b''
        realCipText = AesNew(key=cbckey, mode=MODE_CBC, iv=iv).encrypt(_padding(text))
            # AES密钥支持128位、192位、256位, 此处 32字节 * 8 = 256位
            # 由于密钥经过 shake_256 转换, 破解难度为: min(256 ** 32, 2 ** 256) ==> 破解难度较原始AES-CBC-256算法未变
        cipText = bytes([self.version, ptype, checkSize, saltSize]) + check + salt + realCipText
        return cipText

    def decrypt(self, text: bytes):
        version = text[0]
        if version in [1]:
            ptype, checkSize, saltSize = text[1:4]
            check = text[4: 4+checkSize]
            salt = text[4+checkSize: 4+checkSize+saltSize]
            realCipText = text[4+checkSize+saltSize:]
            password = self._versionKeys[version]
            KeyIvCksalt = shake_256(password + salt).digest(80)
            cbckey = KeyIvCksalt[:32]
            iv = KeyIvCksalt[32:48]
            plaTextCode = _invertPadding(AesNew(key=cbckey, mode=MODE_CBC, iv=iv).decrypt(realCipText))
            if checkSize:
                checkSalt = KeyIvCksalt[48:]
                if shake_256(checkSalt + plaTextCode).digest(checkSize) != check:
                    raise ValueError('密钥错误')
            plaText =  _decodePtext(version, ptype, plaTextCode)
            return plaText
        raise ValueError(version)