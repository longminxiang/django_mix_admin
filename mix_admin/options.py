import traceback
from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.conf import settings
from django.db.models import DateField, DateTimeField
from django.template.response import SimpleTemplateResponse
from django.forms.widgets import Media
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect
from .widgets import LayDateWidget, LayDateTimeWidget


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
    # 格式：(NAME, {'display': BTN_NAME, 'action': ACTION_FUNC, 'show_in_addform': SHOW_IN_ADD_FORM}),
    custom_form_buttons = ()
    # 隐藏原生按钮
    hide_original_form_buttons = False

    # 预览图片
    enable_preview_image = True

    list_display_min_width = {}

    formfield_overrides = {
        DateField: {'widget': LayDateWidget},
        DateTimeField: {'widget': LayDateTimeWidget}
    }

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

    def get_list_tips(self, request):
        return None

    def get_list_display_min_width(self, request):
        return self.list_display_min_width

    def get_custom_form_buttons(self, request, object_id):
        return self.custom_form_buttons

    def get_hide_original_form_buttons(self, request, object_id):
        return self.hide_original_form_buttons

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

        extra_context['list_tips'] = self.get_list_tips(request)

        min_width_fields = self.get_list_display_min_width(request)
        extra_context['min_width_fields'] = [(k, v) for k, v in min_width_fields.items()]

        return extra_context

    def changelist_view(self, request, extra_context=None):
        # 额外context
        extra_context = self.changelist_view_extra_context(request, extra_context)
        view = super().changelist_view(request, extra_context=extra_context)
        return view

    def _changeform_view(self, request, object_id, form_url, extra_context):
        # 自定义详情按钮
        custom_form_buttons = self.get_custom_form_buttons(request, object_id)
        if bool(custom_form_buttons):
            extra_context = extra_context or {}
            extra_context['custom_form_buttons'] = custom_form_buttons
        # 隐藏原生按钮
        hide_original_form_buttons = self.get_hide_original_form_buttons(request, object_id)
        if hide_original_form_buttons:
            extra_context = extra_context or {}
            extra_context['hide_original_form_buttons'] = hide_original_form_buttons

        if request.method == 'POST':
            origin_btns = ['_save', '_saveasnew', '_continue', '_addanother', '_continue']
            for name, btn in custom_form_buttons:
                if name not in request.POST or name in origin_btns or name.startswith('_'):
                    continue
                qs = self.model.objects.filter(pk=object_id)
                res = btn.get('action')(self, request, qs)
                return res or HttpResponseRedirect(request.path)

            # 如果隐藏了原生按钮，不响应原生操作
            if hide_original_form_buttons:
                custom_buttons = [n[0] for n in custom_form_buttons]
                is_origin = [n for n in origin_btns if n in request.POST and n not in custom_buttons]
                if len(is_origin):
                    return HttpResponseRedirect(request.path)

        return super()._changeform_view(request, object_id, form_url, extra_context)

    def response_action(self, request, queryset):
        response = None
        try:
            response = super().response_action(request, queryset)
        except ValidationError as e:
            for err in e.error_list:
                self.message_user(request, err.message, messages.ERROR)
        except Exception as e:
            print(traceback.format_exc(-3))
            msg = e.message if hasattr(e, 'message') else '请稍后再试'
            self.message_user(request, msg, messages.ERROR)
        return response

    def message_user(self, request, message, level=messages.INFO, extra_tags='', fail_silently=False):
        if '修改成功' in message or '你可以在下面再次编辑它' in message:
            message = '保存成功'
        elif '添加成功' in message:
            message = '添加成功'
        elif '删除成功' in message or '成功删除' in message:
            message = '删除成功'
        return super().message_user(request, message, level, extra_tags, fail_silently)

    @property
    def media(self):
        media = super().media
        if self.enable_preview_image:
            media += forms.Media(
                js=[
                    '//cdn.jsdelivr.net/npm/sweetalert2@10.12.5/dist/sweetalert2.min.js',
                    '//cdn.jsdelivr.net/npm/video.js@7.10.2/dist/video.min.js',
                    '//cdn.jsdelivr.net/npm/magnific-popup@1.1.0/dist/jquery.magnific-popup.min.js',
                    '//cdn.jsdelivr.net/npm/floatthead@2.2.1/dist/jquery.floatThead.min.js',
                    'admin/js/mix_admin_02041.js',
                    'admin/js/preview_files_0113.js',
                    'admin/js/custom_action_0222.js'
                ],
                css={'': [
                    '//cdn.jsdelivr.net/npm/sweetalert2@10.12.5/dist/sweetalert2.min.css',
                    '//cdn.jsdelivr.net/npm/magnific-popup@1.1.0/dist/magnific-popup.min.css',
                    '//cdn.jsdelivr.net/npm/video.js@7.10.2/dist/video-js.min.css'
                ]})
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
