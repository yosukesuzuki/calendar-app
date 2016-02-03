# -*- coding: utf-8 -*-
import calendar
from datetime import datetime
from kay.utils import render_to_response


class eventCalendar(calendar.HTMLCalendar):
    def __init__(self, now):
        self.now = now

    def formatday(self, day, weekday):
        """
        Return a day as a table cell.
        """
        if day == 0:
            return '<td class="noday">&nbsp;</td>'  # day outside month
        else:
            if self.now.day == day:
                return '<td class="%s today">%d</td>' % (self.cssclasses[weekday], day)
            return '<td class="%s">%d</td>' % (self.cssclasses[weekday], day)

    def formatmonth(self, theyear, themonth, withyear=True):
        """
        Return a formatted month as a table.
        """
        v = []
        a = v.append
        a('<table class="table table-bordered">')
        a(u'<caption>%s/%s</caption>' % (str(theyear), str(themonth)))
        a('\n')
        a('\n')
        a('<thead>')
        a(self.formatweekheader())
        a('</thead>\n')
        a('<tbody>\n')
        for week in self.monthdays2calendar(theyear, themonth):
            a(self.formatweek(week))
            a('\n')
        a('</tbody>')
        a('</table>')
        a('\n')
        return ''.join(v)


def index(request):
    now = datetime.now()
    selected_month = eventCalendar(now)
    selected_month.setfirstweekday(calendar.SUNDAY)
    calendar_html = selected_month.formatmonth(now.year, now.month)
    return render_to_response('main/index.html', {'message': 'Hello', 'calendar': calendar_html})
