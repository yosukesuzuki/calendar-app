# -*- coding: utf-8 -*-
# core.models

from google.appengine.ext import db

# Create your models here.
from kay.auth.models import GoogleUser


class AdminUser(GoogleUser):
    allowed = db.BooleanProperty(default=False)


class LiveSetting(db.Model):
    setting_id = db.StringProperty(verbose_name="Setting ID", required=True)
    setting_value = db.StringProperty(verbose_name="Setting Value", required=True)
    updated_at = db.DateTimeProperty(auto_now=True)
    created_at = db.DateTimeProperty(auto_now_add=True)

    def __unicode__(self):
        return self.setting_id


class Editor(db.Model):
    editor_id = db.StringProperty(verbose_name="Editor ID", required=True)
    password = db.StringProperty(verbose_name="Password", required=True)
    editor_name = db.StringProperty(verbose_name="Editor Name", required=True)
    updated_at = db.DateTimeProperty(auto_now=True)
    created_at = db.DateTimeProperty(auto_now_add=True)

    def __unicode__(self):
        return self.editor_name


class Event(db.Model):
    event_date = db.DateTimeProperty(verbose_name="Event Date", required=True)
    title = db.StringProperty(verbose_name="Title", required=True)
    description = db.TextProperty(verbose_name="Description (markdown)", required=True)
    updated_log = db.TextProperty()
    updated_at = db.DateTimeProperty(auto_now=True)
    created_at = db.DateTimeProperty(auto_now_add=True)

    def __unicode__(self):
        return self.title


class EventTemplate(db.Model):
    template_name = db.StringProperty(verbose_name="Name of Template", required=True)
    title = db.StringProperty(verbose_name="Title")
    description = db.TextProperty(verbose_name="Description", required=True)
    updated_log = db.TextProperty()
    updated_at = db.DateTimeProperty(auto_now=True)
    created_at = db.DateTimeProperty(auto_now_add=True)

    def __unicode__(self):
        return self.template_name
