# -*- coding: utf-8 -*-
# core.models

from google.appengine.ext import db

# Create your models here.
from kay.auth.models import GoogleUser


class AdminUser(GoogleUser):
    allowed = db.BooleanProperty(default=False)


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
    description = db.TextProperty(verbose_name="Description", required=True)
    updated_log = db.TextProperty()
    updated_at = db.DateTimeProperty(auto_now=True)
    created_at = db.DateTimeProperty(auto_now_add=True)

    def __unicode__(self):
        return self.title
