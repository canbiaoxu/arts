import asyncio, logging
from pathlib import Path

from tornado.web import StaticFileHandler, Application
from tornado.httpserver import HTTPServer

logging.getLogger("tornado.access").setLevel(logging.ERROR)
logging.getLogger("tornado.application").setLevel(logging.ERROR)
logging.getLogger("tornado.general").setLevel(logging.ERROR)

this_dir = Path(__file__).parent

async def main():
    handlers = [(r'/(.*)', StaticFileHandler, {'path':this_dir, 'default_filename':'index.html'})]
    server = HTTPServer(
        Application(handlers=handlers, debug=False),
    )
    server.listen(port=80, address="0.0.0.0")
    print(f"请访问:\nhttp://localhost/")
    await asyncio.Event().wait()

asyncio.run(main())