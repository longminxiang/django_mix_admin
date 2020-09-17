from django import forms
from django.forms import ModelForm
from django.utils.safestring import mark_safe
from django.contrib.admin.options import FORMFIELD_FOR_DBFIELD_DEFAULTS


class BoundFieldHooker():

    def __enter__(self):
        self.old_label_tag = forms.BoundField.label_tag

        def label_tag(bf_self, contents=None, attrs=None, label_suffix=None):
            if bf_self.field.required:
                extra_attrs = {'class': 'required'}
                attrs = extra_attrs if not attrs else {**attrs, **extra_attrs}
            return self.old_label_tag(bf_self, contents=contents, attrs=attrs, label_suffix=label_suffix)

        forms.BoundField.label_tag = label_tag
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        forms.BoundField.label_tag = self.old_label_tag


bound_field_hooker = BoundFieldHooker()


class MixAdminModelForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        field_dict = getattr(self._meta.model, '_field_dict', None)
        if field_dict is None:
            field_dict = {f.name: f for f in self._meta.model._meta.fields}
            setattr(self._meta.model, '_field_dict', field_dict)

        for name, field in self.fields.items():
            model_field = field_dict.get(name)
            if model_field is None:
                continue
            filed_mapper = FORMFIELD_FOR_DBFIELD_DEFAULTS.get(model_field.__class__, {})
            form_class = filed_mapper.get('form_class')
            if form_class is not None:
                self.fields[name] = field = form_class(**field.__dict__)
            widget_class = filed_mapper.get('widget')
            if widget_class is not None:
                field.widget = widget_class()

    def validate_unique(self):
        if self._meta.model._meta.abstract:
            pass
        else:
            super().validate_unique()

    def __str__(self):
        return self.as_div()

    def _as_div(self):
        with bound_field_hooker:
            output = self._html_output(
                normal_row='<div class="form-row">%(errors)s%(label)s%(field)s%(help_text)s</div>',
                error_row='<div class="form-row"><div colspan="2">%s</div></div>',
                row_ender='</div>',
                help_text_html='<div class="help">%s</div>',
                errors_on_separate_row=False,
            )
            return output

    def as_div(self):
        fieldsets = getattr(self, 'fieldsets', None)
        if fieldsets is not None:
            fields = self.fields
            output = ''
            for fieldset in fieldsets:
                h2 = '<h2>' + fieldset[0] + '</h2>' if fieldset[0] is not None else ''
                self.fields = {k: fields[k] for k in fieldset[1].get('fields')}
                output += '<fieldset class="module aligned">' + h2 + self._as_div() + '</fieldset>'
            self.fields = fields
        else:
            output = '<fieldset class="module aligned">' + self._as_div() + '</fieldset>'
        return mark_safe(output)

    @property
    def media(self):
        media = super().media
        js = [
            'core.js',
            'admin/RelatedObjectLookups.js',
            'urlify.js',
            'vendor/xregexp/xregexp.min.js'
        ]
        media = forms.Media(js=['admin/js/%s' % url for url in js]) + media
        return media
