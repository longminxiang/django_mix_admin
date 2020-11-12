from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.conf import settings
from django.template.response import SimpleTemplateResponse
from django.forms.widgets import Media
from django.contrib import messages
from django.urls import reverse
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.http import HttpResponseRedirect


class FileImportHandler:

    handlers = None
    media = forms.Media(js=['admin/js/import_xls.js'])

    def __init__(self):
        if not self.handlers:
            raise ValueError('handlers未设置')
        self.tools = []
        for handler in self.handlers:
            js = '''
            $('#{0}').click(function() {{
                import_file('./', '{0}', '{2}');
            }});
            '''.format(*handler)
            self.tools.append({'id': handler[0], 'title': handler[1], 'js': js})
        super().__init__()

    def _file_process(self, request, handler, f):
        pass

    def view(self, request):
        handler = request.POST.get('_import')
        if handler in [f[0] for f in self.handlers]:
            try:
                f = request.FILES.get('file', None)
                return self._file_process(request, handler, f)
            except Exception as e:
                if isinstance(e, ValidationError):
                    for err in e.error_list:
                        messages.add_message(request, messages.ERROR, err.message)
                else:
                    print(e)
                    msg = getattr(e, 'message', '文件不存在或格式不正确')
                    messages.add_message(request, messages.ERROR, msg)


class ModelAdminProxy:

    def is_changelist_request(self, request):
        '''
        判断是否是列表
        '''
        url = 'admin:%s_%s_changelist' % (self.opts.app_label, self.opts.model_name)
        return request.path == reverse(url)

    def is_autocomplete_request(self, request):
        '''
        判断是否是autocomplete列表
        '''
        url = 'admin:%s_%s_autocomplete' % (self.opts.app_label, self.opts.model_name)
        return request.path == reverse(url)

    def is_change_request(self, request):
        return '/{}/{}/'.format(self.opts.app_label, self.opts.model_name) in request.path \
            and '/change/' in request.path


class ModelAdmin(admin.ModelAdmin, ModelAdminProxy):

    search_placeholder = {}

    # 自定义详情按钮
    # 格式：(NAME, {'display': BTN_NAME, 'action': ACTION_FUNC}),
    custom_form_buttons = ()
    # 隐藏原生按钮
    hide_original_form_buttons = False

    # 导入
    import_handler = None

    # 预览图片
    enable_preview_image = True

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
        action_choices = [(a, n if a != "delete_selected" else "批量删除") for (a, n) in action_choices if a != ""]
        extra_context['action_choices'] = action_choices
        return extra_context

    def changelist_view(self, request, extra_context=None):
        if self.import_handler is not None:
            extra_context = extra_context or {}
            custom_tools = extra_context.get('custom_tools', [])
            custom_tools.extend(self.import_handler.tools)
            extra_context['custom_tools'] = custom_tools
            if request.method == 'POST':
                response = self.import_handler.view(request)
                if response:
                    return response

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

    def _changeform_view(self, request, object_id, form_url, extra_context):
        # 自定义详情按钮
        if bool(self.custom_form_buttons) and bool(object_id):
            extra_context = extra_context or {}
            extra_context['custom_form_buttons'] = self.custom_form_buttons
        # 隐藏原生按钮
        if self.hide_original_form_buttons:
            extra_context = extra_context or {}
            extra_context['hide_original_form_buttons'] = self.hide_original_form_buttons

        if request.method == 'POST':
            for name, btn in self.custom_form_buttons:
                if name not in request.POST:
                    continue
                qs = self.model.objects.filter(pk=object_id)
                btn.get('action')(self, request, qs)
                return HttpResponseRedirect(request.path)

        return super()._changeform_view(request, object_id, form_url, extra_context)

    def response_action(self, request, queryset):
        response = None
        try:
            response = super().response_action(request, queryset)
        except ValidationError as e:
            self.message_user(request, e.message, messages.ERROR)
        return response

    @property
    def media(self):
        media = super().media
        if self.import_handler is not None:
            media += self.import_handler.media
        if self.enable_preview_image:
            media += forms.Media(
                js=['popup/jquery.magnific-popup.min.js', 'admin/js/preview_img.js'],
                css={'': ['popup/magnific-popup.css']})
        return media


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
