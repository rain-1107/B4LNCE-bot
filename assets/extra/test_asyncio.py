import asyncio
import threading


async def _async():
    print("Ran")
    await await_func()


async def await_func():
    print("hallelujah")


def run(loop):
    print("Starting coroutine")
    asyncio.set_event_loop(loop)
    loop = asyncio.get_event_loop()
    loop.create_task(_async())
    loop.run_forever()


if __name__ == "__main__":
    new_loop = asyncio.new_event_loop()
    threading.Thread(target=run, args=[new_loop]).start()
