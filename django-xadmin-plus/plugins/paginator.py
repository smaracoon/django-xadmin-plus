from django.template import loader
from xadmin.sites import site
from xadmin.views import BaseAdminPlugin, ListAdminView
from xadmin.plugins.utils import get_context_dict


class PaginatorMenuPlugin(BaseAdminPlugin):
    paginator_list = []
    
    def block_top_toolbar(self, context, nodes):
        if self.paginator_list:
            context.update({
                'paginator_list': self.paginator_list,
            })
            nodes.append(loader.render_to_string('xadmin/blocks/model_list.top_toolbar.paginator.html', context=get_context_dict(context)))

site.register_plugin(PaginatorMenuPlugin, ListAdminView)
