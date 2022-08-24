import asyncio
import itertools
import pkgutil
import importlib
import inspect

from azusa_clockin_assistant.common.base import BaseInterface
from azusa_clockin_assistant.common.decorators import clockin_method


def find_all_class():
    classes = []
    for _, name, _ in pkgutil.iter_modules(['interface']):
        module = importlib.import_module(f'.{name}', 'azusa_clockin_assistant.interface')
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


async def main():
    tasks = set()
    for cls in find_all_class():
        o = cls()
        for method in find_all_method(o):
            task = asyncio.create_task(method())
            task.add_done_callback(tasks.discard)
            tasks.add(task)
    while len(tasks) != 0:
        await asyncio.gather(*[t for _, t in enumerate(itertools.islice(tasks, 10))])


if __name__ == '__main__':
    asyncio.run(main())
