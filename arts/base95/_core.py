from collections import deque


characters = bytes(range(32, 127)).decode('utf8')
char_count, char_unit, bytes_unit = 95, 67, 55
assert len(characters) == 95
character_indexes = dict(zip(characters, range(len(characters))))


def encode(bytestring: bytes) -> str:
    group_count, remainder = divmod(len(bytestring), bytes_unit)
    if remainder:
        padding_length = bytes_unit - remainder
        bytestring += (b'0' * padding_length)
        group_count += 1
    else:
        padding_length = 0
    result_string = []
    for gi in range(group_count):
        xbytes = bytestring[bytes_unit * gi: bytes_unit * (gi + 1)]
        x_result = deque()
        num = int.from_bytes(xbytes, 'big')  # 转换字节为大整数
        for _ in range(char_unit):  # 确保每组都是 67 个字符
            num, i = divmod(num, char_count)
            x_result.appendleft(characters[i])
        result_string += x_result
    result_string.append(chr(32 + padding_length))  # 加 32 是为了使字符进入可视范围
    return ''.join(result_string)


def decode(encoded_text: str) -> bytes:
    padding_length = ord(encoded_text[-1]) - 32
    encoded_text = encoded_text[:-1]
    result_bytes = bytearray()
    group_count = len(encoded_text) // char_unit
    for gi in range(group_count):
        group_text = encoded_text[char_unit * gi: char_unit * (gi + 1)]
        # 从字符转换回大整数
        num = 0
        for char in group_text:
            num = num * char_count + character_indexes[char]
        group_bytes = num.to_bytes(bytes_unit, 'big')  # 指定字节数为 bytes_unit, 以避免缺失高位零
        result_bytes.extend(group_bytes)
    if padding_length:
        result_bytes = result_bytes[: -padding_length]
    return bytes(result_bytes)