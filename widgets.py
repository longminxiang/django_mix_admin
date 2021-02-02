import json
from django import forms
from django.contrib.admin.widgets import AdminRadioSelect, FilteredSelectMultiple
from django.core.cache import cache
from django.forms.utils import to_current_timezone


class FileAgentWidget(forms.widgets.Input):
    input_type = 'text'

    def __init__(self, attrs=None, options=None):
        attrs = attrs or {}
        attrs['data-ftype'] = 'fileagent'
        attrs['data-options'] = json.dumps(options or {})
        super().__init__(attrs)
        self.options = options

    class Media:
        css = {
            '': ('//cdn.jsdelivr.net/npm/vue-file-agent@latest/dist/vue-file-agent.css', )
        }
        js = (
            '//cdn.jsdelivr.net/npm/vue/dist/vue.min.js',
            '//cdn.jsdelivr.net/npm/vue-file-agent@latest/dist/vue-file-agent.umd.js',
            '//cdn.jsdelivr.net/npm/vue-slicksort@latest/dist/vue-slicksort.min.js',
            'admin/js/file_agent_0119.js'
        )


class AdminHorizontalRadioSelect(AdminRadioSelect):
    template_name = 'admin/widgets/mix_radio.html'
    option_template_name = 'admin/widgets/mix_input_option.html'


class JsonSelectMultiple(FilteredSelectMultiple):

    def __init__(self, verbose_name, validate_keys, split_flag='__', attrs=None, choices=()):
        self.validate_keys = validate_keys
        self.split_flag = split_flag or '__'
        super().__init__(verbose_name, False, attrs, choices)

    def format_value(self, value):
        vals = []
        try:
            val = json.loads(value)
            for k, v in val.items():
                vals.extend('{}{}{}'.format(k, self.split_flag, vv) for vv in v if isinstance(v, list))
        except Exception:
            pass
        return vals

    def value_from_datadict(self, data, files, name):
        val = super().value_from_datadict(data, files, name)
        val_dict = {}
        for v in val:
            for key in self.validate_keys:
                if not v.startswith(key + self.split_flag):
                    continue
                sub_vals = val_dict.setdefault(key, [])
                sub_val = v.split(self.split_flag)[1]
                sub_vals.append(sub_val)
        return json.dumps(val_dict)


class BindingWechatWidget(forms.widgets.Input):
    input_type = 'text'

    def __init__(self, token_url, check_url, attrs=None):
        attrs = attrs or {}
        attrs['data-mixtype'] = 'bindingwx'
        attrs['data-tokenurl'] = token_url
        attrs['data-checkurl'] = check_url
        super().__init__(attrs)

    def value_from_datadict(self, data, files, name):
        val = data.get(name)
        if val.startswith('changed__'):
            key = val.replace('changed__', '')
            val = cache.get(key) or {}
            val = json.dumps(val)
        return val

    class Media:
        js = (
            '//cdn.jsdelivr.net/npm/vue/dist/vue.min.js',
            '//cdn.jsdelivr.net/npm/qrcode_js@1.0.0/qrcode.min.js',
            'admin/js/binding_wx.js'
        )


class EleDateTimeWidget(forms.widgets.DateTimeInput):

    def __init__(self, attrs=None, format=None):
        attrs = attrs or {}
        attrs['data-mixtype'] = 'ele_date_picker'
        super().__init__(attrs, format)

    def format_value(self, value):
        value = to_current_timezone(value)
        val = super().format_value(value)
        return val

    def value_from_datadict(self, data, files, name):
        val = super().value_from_datadict(data, files, name)
        if bool(val):
            val = val.split(' ')
        return val

    def decompress(self, value):
        if value:
            value = to_current_timezone(value)
            return [value.date(), value.time()]
        return [None, None]

    class Media:
        css = {
            '': ('admin/ele_date_picker/EleDatePicker.css', )
        }
        js = (
            '//cdn.jsdelivr.net/npm/vue/dist/vue.min.js',
            'admin/ele_date_picker/EleDatePicker.umd.min.js'
        )


class EleDateWidget(forms.widgets.DateInput):

    def __init__(self, attrs=None, format=None):
        attrs = attrs or {}
        attrs['data-mixtype'] = 'ele_date_picker'
        attrs['data-datetype'] = 'date'
        super().__init__(attrs, format)

    class Media:
        css = {
            '': ('admin/ele_date_picker/EleDatePicker.css', )
        }
        js = (
            '//cdn.jsdelivr.net/npm/vue/dist/vue.min.js',
            'admin/ele_date_picker/EleDatePicker.umd.min.js'
        )
