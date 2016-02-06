# -*- coding: utf-8 -*-

from kay.generics import crud
from kay.routing import (
    ViewGroup, Rule
)

from core.models import Editor
from core.forms import EditorForm


class EditorCRUDViewGroup(crud.CRUDViewGroup):
    model = Editor
    form = EditorForm
    templates = {
        'show': 'core/general_show.html',
        'list': 'core/general_list.html',
        'update': 'core/general_update.html'
    }

    def get_query(self, request):
        return self.model.all().order('-created_at')

    def get_additional_context_on_create(self, request, form):
        return {'key_name': request.form['editor_id']}


view_groups = [
    ViewGroup(
        Rule('/', endpoint='index', view='admin.views.index'),
    ),
    EditorCRUDViewGroup(),
]
