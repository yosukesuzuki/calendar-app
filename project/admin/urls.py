# -*- coding: utf-8 -*-
from google.appengine.api import memcache
from kay.generics import crud
from kay.routing import (
    ViewGroup, Rule
)
from kay.conf import settings

from core.models import Editor, LiveSetting
from core.forms import EditorForm, LiveSettingForm
import hashlib


def generate_password(password):
    password_string = settings.SECRET_KEY + password
    sha512_password = hashlib.sha512(password_string).hexdigest()
    return sha512_password[:128]


class LiveSettingCRUDViewGroup(crud.CRUDViewGroup):
    model = LiveSetting
    form = LiveSettingForm
    templates = {
        'show': 'core/general_show.html',
        'list': 'core/general_list.html',
        'update': 'core/general_update.html'
    }

    def get_query(self, request):
        return self.model.all().order('-created_at')

    def get_additional_context_on_create(self, request, form):
        return {'key_name': request.form['setting_id']}

    def get_additional_context_on_update(self, request, form):
        memcache.delete('setting-restriction_ip')
        return {}


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
        return {'key_name': request.form['editor_id'], 'password': generate_password(request.form['password'])}

    def get_additional_context_on_update(self, request, form):
        return {'password': generate_password(request.form['password'])}


view_groups = [
    ViewGroup(
        Rule('/', endpoint='index', view='admin.views.index'),
    ),
    EditorCRUDViewGroup(),
    LiveSettingCRUDViewGroup(),
]
