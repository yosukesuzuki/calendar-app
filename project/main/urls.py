# -*- coding: utf-8 -*-
from google.appengine.api import memcache
from kay.generics import crud
from kay.routing import (
    ViewGroup, Rule
)
from kay.exceptions import NotAuthorized
from kay.utils import url_for

from core.models import Event, EventTemplate
from core.forms import EventForm, EventTemplateForm


def only_editor_can_write(self, request, operation, obj=None, model_name=None, prop_name=None):
    if ('editor' in request.session) is False or request.session['editor'] is not True:
        raise NotAuthorized()


class EventCRUDViewGroup(crud.CRUDViewGroup):
    # TODO add Event creator info
    model = Event
    form = EventForm
    entities_per_page = 10
    templates = {
        'update': 'main/event_update.html',
        'list': 'core/general_list.html',
    }
    authorize = only_editor_can_write

    def get_list_url(self, cursor=None):
        return url_for('main/index')

    def get_query(self, request):
        return self.model.all().order('-event_date')


class EventTemplateCRUDViewGroup(crud.CRUDViewGroup):
    # TODO add Event creator info
    model = EventTemplate
    form = EventTemplateForm
    templates = {
        'update': 'main/event_update.html',
        'list': 'core/general_list.html',
    }
    authorize = only_editor_can_write
    memcache_key = 'template_feed'

    def _clear_memcache(self):
        memcache.delete(self.memcache_key)

    def get_query(self, request):
        return self.model.all().order('-updated_at')

    def get_additional_context_on_create(self, request, form):
        self._clear_memcache()
        return {}

    def get_additional_context_on_update(self, request, form):
        self._clear_memcache()
        return {}


view_groups = [
    ViewGroup(
        Rule('/', endpoint='index', view='main.views.index'),
        Rule('/feed/events', endpoint='event_feed', view='main.views.event_feed'),
        Rule('/feed/templates', endpoint='template_feed', view='main.views.template_feed'),
        Rule('/login', endpoint='login', view='main.views.login'),
        Rule('/logout', endpoint='logout', view='main.views.logout'),
    ),
    EventCRUDViewGroup(),
    EventTemplateCRUDViewGroup(),
]
