import asyncio
import time


async def count(name):
    for i in range(3):
        print(f"{name} {i}")
        await asyncio.sleep(1)

async def main():
    await asyncio.gather(count(1), count(2), count(3))


if __name__ == '__main__':

    s = time.perf_counter()
    asyncio.run(main())
    elapsed = time.perf_counter() - s
    print(f"executed in {elapsed:0.2f} sec")
