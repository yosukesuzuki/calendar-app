# -*- coding: utf-8 -*-
from kay.generics import crud
from kay.routing import (
    ViewGroup, Rule
)
from kay.exceptions import NotAuthorized
from kay.utils import url_for

from core.models import Event
from core.forms import EventForm


def only_editor_can_write(self, request, operation, obj=None, model_name=None, prop_name=None):
    if ('editor' in request.session) is False or request.session['editor'] is not True:
        raise NotAuthorized()


class EventCRUDViewGroup(crud.CRUDViewGroup):
    # TODO add Event creator info
    model = Event
    form = EventForm
    templates = {
        'update': 'main/event_update.html'
    }
    authorize = only_editor_can_write

    def get_list_url(self, cursor=None):
        return url_for('main/index')



view_groups = [
    ViewGroup(
        Rule('/', endpoint='index', view='main.views.index'),
        Rule('/login', endpoint='login', view='main.views.login'),
    ),
    EventCRUDViewGroup(),
]
