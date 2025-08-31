import asyncio
import time


async def func1():
    print("Function 1 started..")
    await asyncio.sleep(2)
    print("Function 1 Ended")


async def func2():
    print("Function 2 started..")
    await asyncio.sleep(3)
    print("Function 2 Ended")

async def func3():
    print("Function 3 started..")
    await asyncio.sleep(1)
    print("Function 3 Ended")

async def main():
    await asyncio.gather(func1(), func2(), func3())
    print("Main Ended..")


#
# async def main():
#     scripts = []
#     for file in os.listdir('tests'):
#         if len(file.split('.')) == 2 and file.split('.')[1] == 'py' and file.split('.')[0] != 'run_tests':
#             scripts.append('tests.{}'.format(file.split('.')[0]))
#             await asyncio.gather(*[run_script(script) for script in scripts])


asyncio.run(main())