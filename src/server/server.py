import threading
import asyncio
import queue
import logging
import os

#############################################################################
#                                                                           #
#       Server running on a thread using asyncio to serve requests          #
#                                                                           #
#   
#                                                                           #
#############################################################################

HOST:str = os.getenv('HOST') or "127.0.0.1"
PORT:int = int(os.getenv('PORT') or 65000)

# size of request msg in bytes
REQ_SIZE = 1024

logging.basicConfig(level=logging.INFO)

class Server(threading.Thread):
    '''

        Async server that reads requested log file or forwards to writer thread

    '''

    def __init__(self, host: str= HOST, port: int=PORT) -> None:
        super().__init__()
        self.host = host
        self.port = port
        self.server = None
        self.kill_switch = threading.Event()

    def run(self):
        asyncio.run(self.start_server())

    async def start_server(self) -> None:
        self.server = await asyncio.start_server(
            self.accept_connections, self.host, self.port
        )
        self.loop = asyncio.get_running_loop()
        self.loop.create_task(self.stop_serving())

        host, port, *_ = self.server.sockets[0].getsockname()
        logging.info(f"Server started at http://{host}:{port}")

        async with self.server:
            try:
                await self.server.serve_forever()
            except asyncio.CancelledError:
                logging.info('Server cancelled from outside')

    async def accept_connections(self,
                                 reader: asyncio.StreamReader,
                                 writer: asyncio.StreamWriter
                                 ) -> None:
        request = await reader.read(REQ_SIZE)
        await asyncio.sleep(2)
        writer.write(request)
        await writer.drain()
        writer.close()

    def stop_server(self):
        self.kill_switch.set()

    async def stop_serving(self) -> None:
        self.kill_switch.wait()
        logging.info('Kill switch was set. Stopping all async tasks')
        if self.server is not None:
            self.server.close()
            await self.server.wait_closed()
        if self.loop is not None:
            for task in asyncio.all_tasks(loop=self.loop):
                task.cancel()



if __name__ == "__main__":
    server = Server()
    server.start()
    try:
        server.join()
    except KeyboardInterrupt:
        server.stop_server()