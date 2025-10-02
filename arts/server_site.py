import asyncio, logging
from os.path import abspath
from pathlib import Path

from tornado.web import StaticFileHandler, Application
from tornado.httpserver import HTTPServer

try:
    logging.getLogger("tornado.access").setLevel(logging.ERROR)
    logging.getLogger("tornado.application").setLevel(logging.ERROR)
    logging.getLogger("tornado.general").setLevel(logging.ERROR)
except:
    pass

this_dir = Path(__file__).parent

ssl_options = {
    "certfile": abspath(this_dir / 'site_ssl/localhost.crt'),
    "keyfile": abspath(this_dir / 'site_ssl/localhost.key')
}

async def main():
    handlers = [(r'/(.*)', StaticFileHandler, {'path':this_dir, 'default_filename':'index.html'})]
    server = HTTPServer(
        Application(handlers=handlers, debug=False),
        ssl_options = ssl_options
    )
    server.listen(port=443, address="0.0.0.0")
    print(f"请访问:\nhttps://localhost/")
    await asyncio.Event().wait()

asyncio.run(main())