

def action_description(desc, without_queryset=False, confirm=False, confirm_message=None):
    '''
    action description装饰器
    \n@param desc 描述
    \n@param without_queryset 默认action需要选择有记录才能执行, 加此参数不选中也执行
    '''
    def decorator(func):
        func.short_description = desc
        func.without_queryset = without_queryset
        func.options = {'without_queryset': without_queryset, 'confirm': confirm, 'confirm_message': confirm_message}
        return func

    return decorator


def import_file_action(desc, accept=None):

    def decorator(func):
        func.short_description = desc
        func.without_queryset = True
        t_accept = accept
        if t_accept and t_accept == 'xls':
            t_accept = 'application/vnd.ms-excel, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        func.options = {'import_file': True, 'accept': t_accept, 'without_queryset': True}
        return func

    return decorator


def short_description(desc, boolean=False):
    '''
    short description装饰器
    \n@param desc 描述
    '''
    def decorator(func):
        func.short_description = desc
        if boolean:
            func.boolean = boolean
        return func

    return decorator
