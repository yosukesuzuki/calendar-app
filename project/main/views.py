# -*- coding: utf-8 -*-
import calendar
from datetime import datetime, date
from kay.utils import render_to_response


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
                return '<td class="%s today selected" id="%s">%d</td>' % (self.cssclasses[weekday], td_id, day)
            return '<td class="%s" id="%s">%d</td>' % (self.cssclasses[weekday], td_id, day)

    def formatmonth(self, withyear=True):

        """
        Return a formatted month as a table.
        """
        v = []
        a = v.append
        a('<table class="table table-bordered">')
        a('\n')
        a('<thead>')
        a('<tr><th class="left"><span class="glyphicon glyphicon-chevron-left" aria-hidden="true"></span></th>')
        a('<th colspan="5" class="center">%s/%s</th>' % (str(self.theyear), str(self.themonth)))
        a('<th class="right"><span class="glyphicon glyphicon-chevron-right" aria-hidden="true"></span></th></tr>')
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


def index(request):
    now = datetime.now()
    selected_month_calendar = eventCalendar(now, now.year, now.month)
    selected_month_calendar.setfirstweekday(calendar.SUNDAY)
    calendar_html = selected_month_calendar.formatmonth()
    next_month = add_months(now, 1)
    next_month_calendar = eventCalendar(now, next_month.year, next_month.month)
    next_month_calendar.setfirstweekday(calendar.SUNDAY)
    calendar_html += next_month_calendar.formatmonth()
    return render_to_response('main/index.html', {'message': 'Hello', 'calendar': calendar_html})
