from os.path import abspath

_counts = {}
def _assert_import_count(file:str):
    file = abspath(file)
    _counts.setdefault(file, 0)
    _counts[file] += 1
    assert _counts[file] == 1