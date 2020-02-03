from __future__ import absolute_import
import xadmin
from .models import UserSettings, Log, MenuView
from xadmin.layout import *

from django.utils.translation import ugettext_lazy as _, ugettext
from guardian.models import UserObjectPermission, GroupObjectPermission


class UserSettingsAdmin(object):
    model_icon = 'fas fa-cog'
    hidden_menu = True


xadmin.site.register(UserSettings, UserSettingsAdmin)


class LogAdmin(object):

    def link(self, instance):
        if instance.content_type and instance.object_id and instance.action_flag != 'delete':
            admin_url = self.get_admin_url('%s_%s_change' % (instance.content_type.app_label, instance.content_type.model), 
                instance.object_id)
            return "<a href='%s'>%s</a>" % (admin_url, _('Admin Object'))
        else:
            return ''
    link.short_description = ""
    link.allow_tags = True
    link.is_column = False

    list_display = ('action_time', 'user', 'ip_addr', '__str__', 'link')
    list_filter = ['user', 'action_time']
    search_fields = ['ip_addr', 'message']
    model_icon = 'fas fa-cog'


xadmin.site.register(Log, LogAdmin)


class UserObjectPermissionAdmin(object):
    def object_str(self, instance):
        return instance.content_type.get_object_for_this_type(pk=instance.object_pk)

    object_str.short_description = '对象名'
    object_str.allow_tags = True
    object_str.is_column = True

    list_display = ('user', 'content_type', 'object_str', 'object_pk', 'permission')
    list_filter = ('user', 'content_type', 'object_pk', 'permission')

    model_icon = 'fas fa-user-cog'


xadmin.site.register(UserObjectPermission, UserObjectPermissionAdmin)


class GroupObjectPermissionAdmin(object):
    def object_str(self, instance):
        return instance.content_type.get_object_for_this_type(pk=instance.object_pk)

    object_str.short_description = '对象名'
    object_str.allow_tags = True
    object_str.is_column = True

    list_display = ('group', 'content_type', 'object_str', 'object_pk', 'permission')
    list_filter = ('group', 'content_type', 'object_pk', 'permission')

    model_icon = 'fas fa-users-cog'


xadmin.site.register(GroupObjectPermission, GroupObjectPermissionAdmin)


class MenuViewAdmin(object):
    list_display = ('app_label', 'menu_label')
    model_icon = 'fas fa-file-code'


xadmin.site.register(MenuView, MenuViewAdmin)


