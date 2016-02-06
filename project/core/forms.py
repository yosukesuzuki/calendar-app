# -*- coding: utf-8 -*-

from kay.utils.forms.modelform import ModelForm
from core.models import Editor, Event


class EditorForm(ModelForm):
    class Meta:
        model = Editor


class EventForm(ModelForm):
    class Meta:
        model = Event
        exclude = ('updated_log')
