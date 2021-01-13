

def action_description(
        desc, without_queryset=False, confirm=False, confirm_message=None,
        style=None, ajax=False, href=None, attrs=None, show_in_add=False):
    '''
    action description装饰器
    \n@param desc 描述
    \n@param without_queryset 默认action需要选择有记录才能执行, 加此参数不选中也执行
    \n@param confirm 是否弹出确认弹窗
    \n@param confirm_message 确认弹窗消息
    \n@param style 按钮style
    \n@param ajax 是否执行异步js
    \n@param href <a>的href
    \n@param attrs <a>的属性
    \n@param show_in_add 当用来装饰form button时，表示是否在add form中显示
    '''
    def decorator(func):
        func.short_description = desc
        func.without_queryset = without_queryset
        func.show_in_add = show_in_add or False
        func.options = {
            'name': func.__name__, 'without_queryset': without_queryset, 'confirm': confirm,
            'confirm_message': confirm_message, 'style': style, 'ajax': ajax, 'href': href,
            'attrs': attrs, 'show_in_add': show_in_add
        }
        return func

    return decorator


def import_file_action(desc, accept=None, style=None):
    '''
    导入文件 action description装饰器
    \n@param desc 描述
    \n@param accept 接受的文件格式
    \n@param style 按钮style
    '''
    def decorator(func):
        func.short_description = desc
        func.without_queryset = True
        t_accept = accept
        if t_accept and t_accept == 'xls':
            t_accept = 'application/vnd.ms-excel, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        func.options = {'import_file': True, 'accept': t_accept, 'without_queryset': True, 'style': style}
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
