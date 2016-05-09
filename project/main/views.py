# -*- coding: utf-8 -*-
import calendar
import icalendar
import logging
from datetime import datetime, date, timedelta
from werkzeug import redirect, Response
from google.appengine.api import memcache
from kay.utils import render_to_response, url_for, render_json_response
from kay.utils import forms
from kay.i18n import gettext as _
from core.models import Editor, Event, EventTemplate, LiveSetting
from admin.urls import generate_password

from functools import update_wrapper


def get_restriction(restriction_key_name):
    memcache_key = 'setting-' + restriction_key_name
    restriction_data = memcache.get(memcache_key)
    if restriction_data is not None:
        return restriction_data
    restriction_data_entity = LiveSetting.get_by_key_name(restriction_key_name)
    if restriction_data_entity is None:
        return None
    restriction_data = restriction_data_entity.setting_value
    memcache.set(memcache_key, restriction_data)
    return restriction_data


def check_if_ip_address_match(restriction_data, remote_addr):
    ip_address_patterns = restriction_data.split(',')
    for pattern in ip_address_patterns:
        if remote_addr.startswith(pattern):
            return True
    return False


def access_restrict(func):
    def inner(request, *args, **kwargs):
        restriction_key_name = 'restriction_ip'
        restriction_data = get_restriction(restriction_key_name)
        if restriction_data is not None:
            if (check_if_ip_address_match(restriction_data, request.remote_addr) is False) and (
                            ('editor' in request.session) is False or request.session['editor'] is not True):
                logging.warning('access not allowed, remote addr: %s' % request.remote_addr)
                return redirect(url_for('main/error403'))
        return func(request, *args, **kwargs)
    update_wrapper(inner, func)
    return inner


def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = int(sourcedate.year + month / 12)
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


class eventCalendar(calendar.HTMLCalendar):
    def __init__(self, now, theyear, themonth):
        self.now = now
        self.theyear = theyear
        self.themonth = themonth

    def formatday(self, day, weekday):
        """
        Return a day as a table cell.
        """
        if day == 0:
            return '<td class="noday">&nbsp;</td>'  # day outside month
        else:
            td_id = "%s-%s-%s" % (str(self.theyear), str(self.themonth).zfill(2), str(day).zfill(2))
            if self.now.day == day and self.themonth == self.now.month and self.theyear == self.now.year:
                return '<td class="aday %s today selected" id="%s">%d<br/><span>&nbsp;</span></td>' % (
                    self.cssclasses[weekday], td_id, day)
            return '<td class="aday %s" id="%s">%d<br/><span>&nbsp;</span></td>' % (
                self.cssclasses[weekday], td_id, day)

    def formatmonth(self, withyear=True):

        """
        Return a formatted month as a table.
        """
        this_month = datetime(self.theyear, self.themonth, 1)
        next_month = add_months(this_month, 1)
        next_month_id = "%d-%s" % (next_month.year, str(next_month.month).zfill(2))
        pre_month = add_months(this_month, -1)
        pre_month_id = "%d-%s" % (pre_month.year, str(pre_month.month).zfill(2))
        v = []
        a = v.append
        a('<table class="table table-bordered calendar">')
        a('\n')
        a('<thead>')
        a('<tr>')
        a('<th class="left cmonth" id="%s">' % pre_month_id)
        a('<span class="glyphicon glyphicon-chevron-left" aria-hidden="true"></span></th>')
        a('<th colspan="5" class="center">%s %s</th>' % (calendar.month_name[self.themonth], str(self.theyear)))
        a('<th class="right cmonth" id="%s">' % next_month_id)
        a('<span class="glyphicon glyphicon-chevron-right" aria-hidden="true"></span></th></tr>')
        a(self.formatweekheader())
        a('</thead>\n')
        a('<tbody>\n')
        for week in self.monthdays2calendar(self.theyear, self.themonth):
            a(self.formatweek(week))
            a('\n')
        a('</tbody>')
        a('</table>')
        a('\n')
        return ''.join(v)


class LoginForm(forms.Form):
    editor_id = forms.TextField(required=True, max_length=30)
    password = forms.TextField(required=True, widget=forms.PasswordInput)


@access_restrict
def index(request):
    try:
        selectd_month_id = request.args["month"]
    except:
        selectd_month_id = None
    now = datetime.now()
    if selectd_month_id is not None:
        month_data = selectd_month_id.split("-")
        try:
            theyear = int(month_data[0])
            themonth = int(month_data[1])
            if themonth < 1 or themonth > 12:
                raise ValueError
        except:
            theyear = now.year
            themonth = now.month
    else:
        theyear = now.year
        themonth = now.month
    selected_month_calendar = eventCalendar(now, theyear, themonth)
    selected_month_calendar.setfirstweekday(calendar.SUNDAY)
    calendar_html = selected_month_calendar.formatmonth()
    next_month = add_months(datetime(theyear, themonth, 1), 1)
    next_month_calendar = eventCalendar(now, next_month.year, next_month.month)
    next_month_calendar.setfirstweekday(calendar.SUNDAY)
    calendar_html += next_month_calendar.formatmonth()
    return render_to_response('main/index.html', {'calendar': calendar_html})


@access_restrict
def event_feed(request):
    try:
        theyear_themonth = request.args['month'].split('-')
        theyear = int(theyear_themonth[0])
        themonth = int(theyear_themonth[1])
        feed_title = 'Events of: %s %d' % (calendar.month_name[themonth], theyear)
        if themonth < 1 or themonth > 12:
            raise ValueError
    except:
        now = datetime.now()
        theyear = now.year
        themonth = now.month
        feed_title = _('Upcoming Event')
    first_day_of_themonth = datetime(theyear, themonth, 1) + timedelta(days=-1)
    three_month_after = add_months(first_day_of_themonth, 2)
    results = Event.all().filter(u'event_date >=', first_day_of_themonth).filter(
        u'event_date <', three_month_after).order('event_date').fetch(1000)
    events = [
        {'date': r.event_date.strftime('%Y-%m-%d %H:%M'),
         'title': r.title, 'description': r.description, 'key': str(r.key())} for r in results]
    return render_json_response({'events': events, 'title': feed_title}, mimetype='application/json')


@access_restrict
def template_feed(request):
    memcache_key = 'template_feed'
    template_feed_dict = memcache.get(memcache_key)
    if template_feed_dict is not None:
        return render_json_response({'templates': template_feed_dict}, mimetype='application/json')
    results = EventTemplate.all().order('-updated_at').fetch(20)
    template_feed_dict = [
        {'template_name': r.template_name, 'title': r.title, 'id': r.key().id(), 'description': r.description} for r in
        results]
    memcache.set(memcache_key, template_feed_dict, 3600)
    return render_json_response({'templates': template_feed_dict}, mimetype='application/json')


@access_restrict
def ical(request, event_key):
    event = Event.get(event_key)
    if event is None:
        return render_json_response({'error': '404 not found'}, mimetype='application/json', status=404)
    cal = icalendar.Calendar()
    eve = icalendar.Event()
    eve['dtstart'] = event.event_date.strftime('%Y%m%dT%H%M%S')
    eve['created'] = event.created_at.strftime('%Y%m%dT%H%M%S')
    eve['last-modified'] = event.updated_at.strftime('%Y%m%dT%H%M%S')
    eve['summary'] = event.title
    eve['description'] = event.description
    eve['event_key'] = event_key
    eve['updated_log'] = event.updated_log
    cal.add_component(eve)
    return Response(cal.to_ical(), status=200, mimetype="text/calendar",
                    headers={'Content-Disposition': 'inline; filename=event.ics'})


@access_restrict
def ical_all(request):
    events_list = Event.all()
    cal = icalendar.Calendar()
    for event in events_list:
        eve = icalendar.Event()
        eve['dtstart'] = event.event_date.strftime('%Y%m%dT%H%M%S')
        eve['created'] = event.created_at.strftime('%Y%m%dT%H%M%S')
        eve['last-modified'] = event.updated_at.strftime('%Y%m%dT%H%M%S')
        eve['summary'] = event.title
        eve['description'] = event.description
        eve['event_key'] = event.key
        eve['updated_log'] = event.updated_log
        cal.add_component(eve)
    return Response(cal.to_ical(), status=200, mimetype="text/calendar",
                    headers={'Content-Disposition': 'inline; filename=event.ics'})


def login(request):
    form = LoginForm()
    if request.method == "POST":
        if form.validate(request.form):
            editor = Editor.get_by_key_name(request.form['editor_id'])
            if editor is None:
                return redirect(url_for('main/login', error="invalid"))
            if editor.password == generate_password(request.form['password']):
                request.session['editor'] = True
                request.session['editor_id'] = editor.key().name()
                request.session['editor_name'] = editor.editor_name
                return redirect(url_for('main/index'))
            return redirect(url_for('main/login', error="invalid"))
        else:
            return redirect(url_for('main/login', error="invalid"))
    return render_to_response("main/login.html", {"form": form.as_widget()})


def logout(request):
    if 'editor' in request.session:
        del request.session['editor']
    if 'editor_id' in request.session:
        del request.session['editor_id']
    if 'editor_name' in request.session:
        del request.session['editor_name']
    return redirect(url_for('main/index'))


def error403(request):
    return render_to_response('main/403.html', {}, status=403)
