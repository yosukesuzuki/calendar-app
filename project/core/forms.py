# -*- coding: utf-8 -*-

from kay.utils.forms.modelform import ModelForm
from core.models import Editor, Event, EventTemplate, LiveSetting


class LiveSettingForm(ModelForm):
    class Meta:
        model = LiveSetting


class EditorForm(ModelForm):
    class Meta:
        model = Editor


class EventForm(ModelForm):
    class Meta:
        model = Event
        exclude = ('updated_log')


class EventTemplateForm(ModelForm):
    class Meta:
        model = EventTemplate
        exclude = ('updated_log')
