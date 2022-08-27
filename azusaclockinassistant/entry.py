import asyncio
import itertools
import pkgutil
import importlib
import inspect

from azusaclockinassistant.common.base import BaseInterface
from azusaclockinassistant.common.decorators import clockin_method


def find_all_class():
    classes = []
    for _, name, _ in pkgutil.iter_modules(['azusaclockinassistant/interface']):
        module = importlib.import_module(f'.{name}', 'azusaclockinassistant.interface')
        for _, member in inspect.getmembers(module):
            if inspect.isclass(member) and member != BaseInterface and issubclass(member, BaseInterface):
                classes.append(member)
    return classes


def find_all_method(obj):
    methods = []
    for _, member in inspect.getmembers(obj):
        if getattr(member, '__decorator__', None) == clockin_method.__name__:
            methods.append(member)
    return methods


async def gather_with_concurrency(n, *tasks):
    semaphore = asyncio.Semaphore(n)

    async def sem_task(task):
        async with semaphore:
            try:
                await task
            except Exception as e:
                print(f'{task.__name__} 异常 {str(e)} 即将重试')
    await asyncio.gather(*(sem_task(task) for task in tasks))


async def main():
    tasks = set()
    for cls in find_all_class():
        o = cls()
        for method in find_all_method(o):
            task = method()
            tasks.add(task)
    await gather_with_concurrency(10, *tasks)


def start():
    asyncio.run(main())
