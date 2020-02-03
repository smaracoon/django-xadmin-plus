import copy
from collections import OrderedDict
from django.db import transaction
from django.core.exceptions import PermissionDenied, ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth import get_permission_codename
from django.contrib.auth.models import Group
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.shortcuts import get_object_or_404
from django.urls.base import reverse
from django.http import Http404, HttpResponseRedirect
from django.utils import six
from django.utils.html import escape
from django.utils.encoding import force_text
from django.utils.translation import ugettext as _
from django.template.response import TemplateResponse

from xadmin.util import unquote
from xadmin.sites import site
from xadmin.views import ModelAdminView, FormAdminView
from xadmin.views.base import filter_hook, csrf_protect_m
from xadmin.layout import FormHelper, Main, Layout, Fieldset, TabHolder, Container, Column, Col, Field

from guardian.forms import UserObjectPermissionsForm, GroupObjectPermissionsForm
from guardian.shortcuts import get_user_perms, get_group_perms, get_users_with_perms, get_groups_with_perms, get_perms_for_model


class AdminUserObjectPermissionsForm(UserObjectPermissionsForm):

    def get_obj_perms_field_widget(self):
        return FilteredSelectMultiple(_("permission"), False)


class AdminGroupObjectPermissionsForm(GroupObjectPermissionsForm):

    def get_obj_perms_field_widget(self):
        return FilteredSelectMultiple(_("permission"), False)


class GuardianyView(ModelAdminView):
    guardiany_template_name = 'xadmin/guardiany/guardiany.html'

    def init_request(self, object_id, *args, **kwargs):
        self.org_obj = self.get_object(unquote(object_id))

        # 如果又修改权限，意味着可以进入编辑模型界面，即可以进入查看权限的页面
        if self.has_change_permission() or self.has_change_permission_obj(self.org_obj):
            pass
        else:
            raise PermissionDenied

        if self.org_obj is None:
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') %
                          {'name': force_text(self.opts.verbose_name), 'key': escape(object_id)})

    def get_media(self):
        media = super(GuardianyView, self).get_media()
        media = media + self.vendor('xadmin.plugin.guardiany.css')
        return media

    # 判断用户有没有修改权限的权限，暂时定为超级用户可以修改，后面可以对于不同的对象进行定制
    # 例如只有在某个群组中的用户才可以修改，可以在这个类前面添加一个群组的名字
    def has_change_guardiany(self):
        if self.user.is_superuser:
            return True
        else:
            return False

    @filter_hook
    def get_context(self):

        users_perms = OrderedDict(
            sorted(
                get_users_with_perms(self.org_obj,
                                        attach_perms=True,
                                        with_group_users=False).items(),
                key=lambda user:getattr(user[0], get_user_model().USERNAME_FIELD)
            )
        )

        groups_perms = OrderedDict(
            sorted(
                get_groups_with_perms(self.org_obj,
                                     attach_perms=True).items(),
                key=lambda group: group[0].name
            )
        )

        context = super(GuardianyView, self).get_context()
        new_context = {
            'original': self.org_obj,
            'change_url': self.model_admin_url('change', self.org_obj.pk),
            'has_change_permission': self.has_change_permission() or self.has_change_permission_obj(self.org_obj),
            'has_change_guardiany': self.has_change_guardiany(),
            'model_perms': get_perms_for_model(self.org_obj),
            'users_perms': users_perms,
            'groups_perms': groups_perms,
        }
        context.update(new_context)
        return context

    @filter_hook
    def get(self, request, *args, **kwargs):
        context = self.get_context()
        return TemplateResponse(request, self.guardiany_template_name, context)

    @filter_hook
    @csrf_protect_m
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        if 'submit_manage_user' in request.POST:
            username = request.POST.get('username', '')
            user_obj = get_object_or_404(get_user_model(), username=username)
            if user_obj:
                user_id = user_obj.pk
                return HttpResponseRedirect("user-manage/" + str(user_id))
            else:
                msg = '用户名不存在，请重新输入'
                self.message_user(msg, 'error')
                return self.get(self.request, *args, **kwargs)
        elif 'submit_manage_group' in request.POST:
            groupname = request.POST.get('groupname', '')
            group_obj = get_object_or_404(Group, name=groupname)
            if group_obj:
                group_id = group_obj.pk
                return HttpResponseRedirect("group-manage/" + str(group_id))
            else:
                msg = '群组名不存在，请重新输入'
                self.message_user(msg, 'error')
                return self.get(self, request, *args, **kwargs)


class GuardianyBaseView(FormAdminView):
    form = None
    title = '权限修改'
    guardiany_base_template_name = None

    def has_change_permission(self):
        codename = get_permission_codename('change', self.model._meta)
        return self.user.has_perm('%s.%s' % (self.model._meta.app_label, codename))

    def has_change_permission_obj(self, obj):
        codename = get_permission_codename('change', self.model._meta)
        return self.user.has_perm('%s.%s' % (self.model._meta.app_label, codename), obj)

    def get_base_obj(self, base_id):
        pass

    @filter_hook
    def get_object(self, object_id):
        model = self.model
        try:
            object_id = model._meta.pk.to_python(object_id)
            return model.objects.get(pk=object_id)
        except(model.DoseNotExist, ValidationError):
            return None

    def init_request(self, object_id, base_id, *args, **kwargs):
        self.org_obj = self.get_object(unquote(object_id))
        self.base_obj = self.get_base_obj(base_id)

        if self.org_obj is None:
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') %
                          {'name': force_text(self.opts.verbose_name), 'key': escape(object_id)})

        if self.base_obj is None:
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') %
                          {'name': 'User or Group', 'key': escape(base_id)})

        if not self.has_change_permission_obj(self.org_obj):
            raise PermissionDenied

        self.form_class = self.get_obj_perms_manage_base_form()

    @filter_hook
    def prepare_form(self):
        self.view_form = self.form

    @filter_hook
    def instance_forms(self):
        self.form_obj = self.view_form

    @filter_hook
    def valid_forms(self):
        return self.form_obj.is_valid()

    @csrf_protect_m
    @filter_hook
    def get(self, request, *args, **kwargs):
        self.form = self.form_class(self.base_obj, self.org_obj, None)
        self.prepare_form()
        self.instance_forms()
        return self.get_response()

    @csrf_protect_m
    @transaction.atomic
    @filter_hook
    def post(self, request, *args, **kwargs):
        self.form = self.form_class(self.base_obj, self.org_obj, request.POST)
        self.prepare_form()
        self.instance_forms()

        if self.valid_forms():
            self.form_obj.save_obj_perms()
            response = self.post_response()
            cls_str = str if six.PY3 else basestring
            if isinstance(response, cls_str):
                return HttpResponseRedirect(response)
            else:
                return response

        return self.get_response()

    # 'xadmin.plugin.guardiany_base.widgets.responsive.css'这个好像没啥用，删除了。和response.css完全一致
    def get_media(self):
        media = super(GuardianyBaseView, self).get_media()
        media = media + self.vendor('xadmin.plugin.guardiany_base.css', 'xadmin.plugin.themes.js')
        return media

    @filter_hook
    def get_context(self):
        context = super(GuardianyBaseView, self).get_context()
        new_context = {
            'opts': self.model._meta,
            'original': self.org_obj,
            'base_obj': self.base_obj,
            'title': self.title,
            'change_url': reverse("%s:%s_%s_%s" % (self.admin_site.app_name, self.model._meta.app_label, self.model._meta.model_name, 'change'), args=(self.org_obj.pk,)),
            'guardiany_url': reverse("%s:%s_%s_%s" % (self.admin_site.app_name, self.model._meta.app_label, self.model._meta.model_name, 'guardiany'), kwargs={'object_id': self.org_obj.pk}),
            'has_change_permission': self.has_change_permission() or self.has_change_permission_obj(self.org_obj),
        }
        context.update(new_context)
        return context

    @filter_hook
    def get_response(self):
        context = self.get_context()
        context.update(self.args or {})
        return TemplateResponse(self.request, self.guardiany_base_template_name, context)

    @filter_hook
    def post_response(self):
        request = self.request
        msg = _('The %s was changed successfully.') % self.title
        self.message_user(msg, 'success')

        if "_redirect" in request.GET:
            return request.GET["_redirect"]
        else:
            return self.get_redirect_url()

    @filter_hook
    def get_redirect_url(self):
        return reverse("%s:%s_%s_%s" % (self.admin_site.app_name,
                                        self.model._meta.app_label,
                                        self.model._meta.model_name,
                                        'guardiany'),
                       kwargs={'object_id': self.org_obj.pk})


class GuardianyUserView(GuardianyBaseView):
    title = '用户权限修改'
    guardiany_base_template_name = 'xadmin/guardiany/guardiany_user.html'

    def get_obj_perms_manage_base_form(self):
        return AdminUserObjectPermissionsForm

    def get_base_obj(self, base_id):
        return get_object_or_404(get_user_model(), pk=base_id)


class GuardianyGroupView(GuardianyBaseView):
    title = '群组权限修改'
    guardiany_base_template_name = 'xadmin/guardiany/guardiany_group.html'

    def get_obj_perms_manage_base_form(self):
        return AdminGroupObjectPermissionsForm

    def get_base_obj(self, base_id):
        return get_object_or_404(Group, pk=base_id)


site.register_modelview(r'^(?P<object_id>\d+)/guardiany/$', GuardianyView, name='%s_%s_guardiany')
site.register_modelview(r'^(?P<object_id>\d+)/guardiany/user-manage/(?P<base_id>\d+)/$', GuardianyUserView, name='%s_%s_guardiany_user')
site.register_modelview(r'^(?P<object_id>\d+)/guardiany/group-manage/(?P<base_id>\d+)/$', GuardianyGroupView, name='%s_%s_guardiany_group')


