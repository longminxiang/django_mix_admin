from django.urls import reverse


def get_changelist_url(model_admin):
    changelist_url = 'admin:%s_%s_changelist' % (model_admin.opts.app_label, model_admin.opts.model_name)
    return reverse(changelist_url)
