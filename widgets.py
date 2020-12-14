from django import forms


class FileAgentWidget(forms.widgets.Input):
    input_type = 'text'
    template_name = 'admin/widgets/file_agent.html'

    class Media:
        css = {
            '': ('//cdn.jsdelivr.net/npm/vue-file-agent@latest/dist/vue-file-agent.css', )
        }
        js = (
            '//cdn.jsdelivr.net/npm/vue/dist/vue.min.js',
            '//cdn.jsdelivr.net/npm/vue-file-agent@latest/dist/vue-file-agent.umd.js',
            '//cdn.jsdelivr.net/npm/vue-slicksort@latest/dist/vue-slicksort.min.js'
        )
