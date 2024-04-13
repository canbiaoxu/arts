from os.path import abspath
from arts.cooltypes import moduledb


sheet: moduledb.File = moduledb.DB(abspath(__file__), depth=1)['sheet_1']


def set_environment_name(name: str):
    sheet['environment_name'] = name

def read_environment_name():
    name = sheet.get('environment_name')
    if not name:
        try:
            import platform
            name = platform.processor()
        except: ...
    return name or 'null'