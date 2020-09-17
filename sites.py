from django.contrib import admin
from django.urls import path, reverse


class AdminSite(admin.AdminSite):

    extra_sidebar = {}

    @classmethod
    def add_extra_sidebar(cls, app_label, name='', view=None, url=''):
        '''
        为侧边栏增加额外的链接
        '''
        sidebars = cls.extra_sidebar.setdefault(app_label, [])
        sidebars.append(
            {'name': name, 'url': url, 'perms': {'view': True}, 'view_only': True, 'view': view})

    def get_urls(self):
        urls = super().get_urls()
        for model, extras in self.extra_sidebar.items():
            for extra in extras:
                url = extra.get('url')
                admin_url = path('{}/{}'.format(model, url), extra.get('view'), name='{}_{}'.format(model, url))
                urls.append(admin_url)
        return urls

    def get_app_list(self, request):
        app_dict = self._build_app_dict(request)
        app_list = app_dict.values()
        for app in app_list:
            extras = self.extra_sidebar.get(app.get('app_label'))
            if extras:
                for extra in extras:
                    if extra.get('admin_url') is None:
                        extra['admin_url'] = reverse('admin:{}_{}'.format(app.get('app_label'), extra.get('url')))

                models = app.setdefault('models', [])
                models.extend(extras)
        return app_list

    def each_context(self, request):
        dic = super().each_context(request)
        if 'login' not in request.path and 'logout' not in request.path and 'password_change' not in request.path:
            dic['has_sidebar'] = True
        dic['sidebar_apps'] = self.get_sidebar_list(request)
        return dic

    def get_sidebar_list(self, request):
        app_list = self.get_app_list(request)
        return app_list
