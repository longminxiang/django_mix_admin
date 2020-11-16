from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.conf import settings
from django.template.response import SimpleTemplateResponse
from django.forms.widgets import Media
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect


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

        # action额外参数
        action_options = extra_context.setdefault('action_options', {})
        extra_context['is_mix'] = True
        for name, tpl in self.get_actions(request).items():
            act_func = tpl[0]
            act_data = getattr(act_func, 'options', None)
            action_options[name] = act_data

        return extra_context

    def changelist_view(self, request, extra_context=None):
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
            for err in e.error_list:
                self.message_user(request, err.message, messages.ERROR)
        return response

    @property
    def media(self):
        media = super().media
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
