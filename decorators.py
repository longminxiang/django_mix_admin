

def action_description(desc, without_queryset=False):
    '''
    action description装饰器
    \n@param desc 描述
    \n@param without_queryset 默认action需要选择有记录才能执行, 加此参数不选中也执行
    '''
    def decorator(func):
        func.short_description = desc
        func.without_queryset = without_queryset
        return func

    return decorator


def short_description(desc):
    '''
    short description装饰器
    \n@param desc 描述
    '''
    def decorator(func):
        func.short_description = desc
        return func

    return decorator
