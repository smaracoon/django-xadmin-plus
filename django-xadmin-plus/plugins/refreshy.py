from xadmin.sites import site
from xadmin.views import BaseAdminPlugin, ListAdminView
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe


class RefreshyPlugin(BaseAdminPlugin):
    refreshy = False
    
    def get_media(self, media):
        if self.refreshy:
            media += self.vendor('xadmin.plugin.refreshy.js')
        return media
        
    def block_top_toolbar(self, context, nodes):
        if self.refreshy:
            nodes.append(mark_safe('<div class="btn-group"><button id="refreshy_id" class="btn btn-sm btn-default"><i class="fas fa-sync"></i> %s</button></div>' % (_(u"刷新"))))

site.register_plugin(RefreshyPlugin, ListAdminView)
