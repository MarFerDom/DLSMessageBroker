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

# Get Host and Port from the environment variables.
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
        # Event is used to hold the parallel task that closes the server
        # from continuing. It continues after kill_switch.set()
        self.kill_switch = asyncio.Event()

    def run(self):
        # Run is called by Thread.start().
        # This is asyncio starting point
        asyncio.run(self.start_server())

    async def start_server(self) -> None:
        # Start server that produces Tasks to serve requests
        self.server = await asyncio.start_server(
            self.accept_connections, self.host, self.port
        )
        # Get current Loop and add parallel Task.
        # stop_serving closes the server but first awaits for the kill_switch.
        self.loop = asyncio.get_running_loop()
        self.loop.create_task(self.stop_serving())

        host, port, *_ = self.server.sockets[0].getsockname()
        logging.info(f"Server started at http://{host}:{port}")

        # Start the Loop that only stops if server is cancelled.
        async with self.server:
            try:
                await self.server.serve_forever()
            except asyncio.CancelledError:
                logging.info('Server cancelled from outside')

    async def accept_connections(self,
                                 reader: asyncio.StreamReader,
                                 writer: asyncio.StreamWriter
                                 ) -> None:
        '''
            Task that serves requests.

            TODO: Substitute for plugin design pattern to extend functionality
        '''
        # Read requests
        request = await reader.read(REQ_SIZE)
        logging.info(f"Received {request.decode()}")
        await asyncio.sleep(2)
        # Write response
        writer.write(request)
        await writer.drain()
        writer.close()

    async def stop_serving(self) -> None:
        '''
            Run as a parallel Task to close server after waiting
            for the Event kill_switch to be set.
        '''
        await self.kill_switch.wait()
        logging.info('Kill switch was set. Stopping all async tasks')
        if self.server is not None:
            self.server.close()
            await self.server.wait_closed()
        if self.loop is not None:
            for task in asyncio.all_tasks(loop=self.loop):
                task.cancel()

    def stop_server(self):
        '''
            Insert parallel Task to set the kill_switch into Loop
            from outside of the thread.
        '''
        self.loop.call_soon_threadsafe(self.kill_switch.set)

if __name__ == "__main__":
    # Start server and translate a KeyboardInterrupt into
    # stopping the server
    server = Server()
    server.start()
    try:
        server.join()
    except KeyboardInterrupt:
        server.stop_server()