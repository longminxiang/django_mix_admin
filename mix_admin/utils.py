from django.urls import reverse


def get_changelist_url(model_admin):
    changelist_url = 'admin:%s_%s_changelist' % (model_admin.opts.app_label, model_admin.opts.model_name)
    return reverse(changelist_url)


def get_changeform_url(model_admin, obj):
    url = 'admin:%s_%s_change' % (model_admin.opts.app_label, model_admin.opts.model_name)
    return reverse(url, args=(obj.pk,))


def change_action_to_custom_form_button(action):
    name = action.__name__
    des = getattr(action, 'short_description', name)
    options = getattr(action, 'options', {})
    return (name, {'display': des, 'action': action, 'options': options})
