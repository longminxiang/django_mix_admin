import json
from django import forms
from django.contrib.admin.widgets import AdminRadioSelect


class FileAgentWidget(forms.widgets.Input):
    input_type = 'text'

    def __init__(self, attrs=None, options=None):
        attrs = attrs or {}
        attrs['data-ftype'] = 'fileagent'
        attrs['data-options'] = json.dumps(options or {})
        super().__init__(attrs)

    class Media:
        css = {
            '': ('//cdn.jsdelivr.net/npm/vue-file-agent@latest/dist/vue-file-agent.css', )
        }
        js = (
            '//cdn.jsdelivr.net/npm/vue/dist/vue.min.js',
            '//cdn.jsdelivr.net/npm/vue-file-agent@latest/dist/vue-file-agent.umd.js',
            '//cdn.jsdelivr.net/npm/vue-slicksort@latest/dist/vue-slicksort.min.js',
            'admin/js/file_agent.js'
        )


class AdminHorizontalRadioSelect(AdminRadioSelect):
    template_name = 'admin/widgets/mix_radio.html'
    option_template_name = 'admin/widgets/mix_input_option.html'
