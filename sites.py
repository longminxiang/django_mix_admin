from django.contrib import admin
from django.urls import path


class AdminSite(admin.AdminSite):
    '''
    自定义admin site
    '''

    extra_app_funcs = []
    extra_urls = []

    def get_urls(self):
        urls = super().get_urls()
        # 添加额外的url
        urls.extend(self.extra_urls)
        return urls

    def get_app_list(self, request):
        '''
        覆盖get_app_list逻辑
        1.去掉按名称排序逻辑
        2.添加额外的model
        3.处理sidebar是否active
        '''
        app_dict = self._build_app_dict(request)
        app_list = app_dict.values()
        for app in app_list:
            for func in self.extra_app_funcs:
                func(self, request, app.get('app_label'), app.get('models'))
            # sidebar的active状态
            for model in app.get('models'):
                url = model.get('admin_url', '').split('?')[0]
                if url in request.path:
                    model['active'] = True
        return app_list

    def app_index(self, request, app_label, extra_context=None):
        '''
        覆盖app index页面逻辑
        1.去掉按名称排序逻辑
        2.增加额外的model
        '''
        # 用extra_context覆盖父类的app_list
        app_dict = self._build_app_dict(request, app_label)
        for func in self.extra_app_funcs:
            func(self, request, app_dict.get('app_label'), app_dict.get('models'))
        extra_context = {'app_list': [app_dict]}

        response = super().app_index(request, app_label, extra_context)
        return response

    def each_context(self, request):
        dic = super().each_context(request)
        # 除这些页面外，都加上侧边栏
        if 'login' not in request.path and 'logout' not in request.path and 'password_change' not in request.path:
            dic['has_sidebar'] = True
        # site url 不需要显示
        dic.pop('site_url')
        return dic


def add_extra_app(func):
    AdminSite.extra_app_funcs.append(func)
    return func


def add_extra_url(url, name=None):

    def wrapper(func):
        xurl = path(url, func, name=name)
        AdminSite.extra_urls.append(xurl)
        return func

    return wrapper
