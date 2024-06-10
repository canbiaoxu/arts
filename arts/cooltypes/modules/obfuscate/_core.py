from typing import Any
from hashlib import shake_256


codingTypes = {}


class Obfuscate:
    _encode_table: list
    _decode_table: list

    def __new__(cls, key: bytes|Any):
        if type(key) is not bytes:
            key = str(key).encode('utf8')
        key = shake_256(key).digest(256)
        if self := codingTypes.get(key):
            return self
        else:
            _encode_table = []
            _decode_table = [None] * 256
            array = list(range(256))
            for p, num in enumerate(key):
                c = array.pop(num % (256 - p))
                _encode_table.append(c)
                _decode_table[c] = p
            assert _encode_table != _decode_table  # 由于哈希算法的结果可能为任意值，因此有可能出现 _encode_table == _decode_table 的情况，但概率极低
            self = object.__new__(cls)
            self._encode_table = _encode_table
            self._decode_table = _decode_table
            codingTypes[key] = self
            return self
    
    def encode(self, _p: bytes) -> bytes:
        _encode_table = self._encode_table
        return bytes([_encode_table[num] for num in _p])

    def decode(self, _c: bytes) -> bytes:
        _decode_table = self._decode_table
        return bytes([_decode_table[num] for num in _c])
    

if __name__ == '__main__':
    obf = Obfuscate(key='自定义密钥')
    明文 = 'beautiful'.encode('utf8')
    密文 = obf.encode(明文)
    print(obf.decode(密文).decode('utf8'))