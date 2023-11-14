import sys, json
from pathlib import Path
from ._apikey import apikey
from ._core import Chat


parent = Path(__file__).parent

def chat_on_cmd():
    print("\n您已进入命令行聊天模式, 该模式使用'gpt-4-1106-preview'模型, 请确保您的apikey支持该模型.")
    record_file = parent / '_cmd_record.json'
    gpt = Chat(api_key=apikey, model='gpt-4-1106-preview')
    try:
        record = json.loads(record_file.read_text('utf8'))
        gpt.add_dialogs(*record)
    except:
        pass
    while True:
        try:
            user = input('\n\n:')
            print()
            for x in gpt.stream_request(user):
                print(x, end='', flush=True)
            record = gpt.fetch_messages()
            record_file.write_text(json.dumps(record, ensure_ascii=False), 'utf8')
        except Exception as e:
            print(f"\n\n{e}")

def _parsecmd():
    kws = sys.argv[1:]
    if kws:
        kw = kws[0].lower()
        if kw == 'set_apikey' and len(kws) > 1:
            py = parent / '_apikey.py'
            py.write_text(f"apikey = '{kws[1]}'", 'utf8')
            print('创建 apikey 成功!')
        elif kw == 'read_apikey':
            print(apikey)
        elif kw == 'chat':
            chat_on_cmd()
    else:
        print('''指令集:
openai2 set_apikey <名称> | 创建环境名称
openai2 read_apikey       | 查看环境名称
openai2 chat              | 与chatGPT对话
''')