[![Circle CI](https://circleci.com/gh/yosukesuzuki/kay-template.svg?style=svg)](https://circleci.com/gh/yosukesuzuki/kay-template)

# What's this?
This is the template for Kay-framework application.
Built-in tox

# Setup
## Setup Google Cloud SDK
install Google Cloud SDK


## make symlink 
```
sudo ln -s /some/whare/google_appengine /usr/local/google_appengine
```

## run tox
```
$ tox
```

# add application folder
```
$ cd project
$ python manage.py startapp appname
```

# how to localize your app(e.g.`main` into Japanese) in your language
### mark the texts in python files or jinja2 templates which need to be translated
```
# in main/views.py
....
....
from kay.i18n import gettext as _ # in views.py
from kay.i18n import lazy_gettext as _ # in models.py/forms.py
# you do not have to import any modules in jinja2 template files.
....
....
.... 

# [before marking]
feed_title = 'Upcoming Event'

# [after marking]
feed_title = _('Upcoming Event')
....
....
.... 
```

### at the first time
```
$ pwd
<<your path>>/calendar-app/project

$ python manage.py extract_messages main # Generated `main/i18n/messages.pot`
$ python manage.py add_translations main -l ja # Generated `main/i18n/ja/LC_MESSAGES/messages.po`

# Open `main/i18n/ja/LC_MESSAGES/messages.po` and translate into the lang

## `main/i18n/ja/LC_MESSAGES/messages.po`
## ....
## #: main/views.py:161
## msgid "Upcoming Event"
## msgstr "<<Translated strigs>>"
## ....

$ python manage.py compile_translations main # Generated `main/i18n/ja/LC_MESSAGES/messages.mo`
```
### from the second time
```
# mark the texts to be tranlated
$ pwd
<<your path>>/calendar-app/project
$ python manage.py extract_messages main
$ python manage.py update_translations -t main -l ja # diff
# Edit `main/i18n/ja/LC_MESSAGES/messages.po`
$ python manage.py compile_translations main
```

