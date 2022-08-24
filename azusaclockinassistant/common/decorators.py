import click


def clockin_method(method):
    async def wrapper(obj):
        click.echo("========================================")
        click.echo(click.style(f'正在执行: {obj.__doc__} {method.__doc__} ...', fg='green'))
        response = await method(obj)
        if response is None:
            click.echo(click.style(f'执行失败: {obj.__doc__} {method.__doc__} 返回格式错误', fg='red'))
        elif response[0] is True:
            click.echo(click.style(f'执行成功: {obj.__doc__} {method.__doc__} {response[1]}', fg='green'))
        else:
            click.echo(click.style(f'执行失败: {obj.__doc__} {method.__doc__} {response[1]}', fg='red'))
        click.echo("========================================")
        return response

    wrapper.__decorator__ = clockin_method.__name__
    return wrapper
