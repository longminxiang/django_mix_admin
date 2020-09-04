from django.contrib import admin
from django.conf import settings
from django.template.response import SimpleTemplateResponse
from django.forms.widgets import Media


class ModelAdmin(admin.ModelAdmin):

    search_placeholder = {}

    def get_search_placeholder(self, request):
        return self.search_placeholder

    def _get_search_placeholder(self, request):
        search_fields = self.get_search_fields(request)
        placeholder = "输入"
        for idx, field in enumerate(search_fields):
            name = self.get_search_placeholder(request).get(field, None)
            if not name:
                name = getattr(getattr(getattr(self.model, field, None), 'field', None), 'verbose_name', field)
            placeholder += ('' if idx == 0 else '/') + name
        placeholder += "搜索"
        return placeholder

    def get_changelist_instance(self, request):
        cl = super().get_changelist_instance(request)
        cl.search_placeholder = self._get_search_placeholder(request)

        return cl

    def changelist_view_extra_context(self, request, extra_context=None):
        extra_context = extra_context or {}
        action_choices = self.get_action_choices(request)
        action_choices = [(a, n if a != "delete_selected" else "删除所选") for (a, n) in action_choices if a != ""]
        extra_context['action_choices'] = action_choices
        return extra_context

    def changelist_view(self, request, extra_context=None):

        # 让action不用有选择数据也可以执行
        action = request.POST.get('action')
        if request.method == "POST" and action:
            no_post = False
            try:
                act_func = self.get_actions(request).get(action)[0]
                no_post = getattr(act_func, 'no_post', False)
            except Exception:
                pass
            if no_post:
                request.POST._mutable = True
                request.POST['_selected_action'] = '1'

        # 额外context
        extra_context = self.changelist_view_extra_context(request, extra_context)
        view = super().changelist_view(request, extra_context=extra_context)
        return view


def _resolve_context(self, context):
    context = self.__resolve_context(context)
    media = context.get('media', None)
    if media:
        ignore_jss = [
            'admin/js/vendor/jquery/jquery{}.js'.format('' if settings.DEBUG else '.min'),
            'admin/js/jquery.init.js'
        ]
        jss = [js for js in media._js if js not in ignore_jss]
        if len(jss) != len(media._js):
            media = Media(js=jss, css=media._css)
            context['media'] = media
    return context


SimpleTemplateResponse.__resolve_context = SimpleTemplateResponse.resolve_context
SimpleTemplateResponse.resolve_context = _resolve_context
