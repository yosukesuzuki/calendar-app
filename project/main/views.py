# -*- coding: utf-8 -*-
import calendar
import icalendar
from datetime import datetime, date, timedelta
from werkzeug import redirect, Response
from google.appengine.api import memcache
from kay.utils import render_to_response, url_for, render_json_response
from kay.utils import forms
from core.models import Editor, Event, EventTemplate
from admin.urls import generate_password


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


def event_feed(request):
    try:
        theyear_themonth = request.args['month'].split('-')
        theyear = int(theyear_themonth[0])
        themonth = int(theyear_themonth[1])
        feed_title = 'Events of: %s %d' % (calendar.month_name[themonth], theyear)
    except:
        now = datetime.now()
        theyear = now.year
        themonth = now.month
        feed_title = 'Upcoming Event'
    first_day_of_themonth = datetime(theyear, themonth, 1) + timedelta(days=-1)
    three_month_after = add_months(first_day_of_themonth, 2)
    results = Event.all().filter(u'event_date >=', first_day_of_themonth).filter(
        u'event_date <', three_month_after).order('event_date').fetch(1000)
    events = [
        {'date': r.event_date.strftime('%Y-%m-%d %H:%M'),
         'title': r.title, 'description': r.description, 'key': str(r.key())} for r in results]
    return render_json_response({'events': events, 'title': feed_title}, mimetype='application/json')


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


def ical(request, event_key):
    event = Event.get(event_key)
    if event is None:
        return render_json_response({'error': '404 not found'}, mimetype='application/json', status=404)
    cal = icalendar.Calendar()
    cal['dtstart'] = event.event_date.strftime('%Y%m%dT%H%M%S')
    cal['summary'] = event.description
    return Response(cal.to_ical(), status=200, mimetype="text/calendar")


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
