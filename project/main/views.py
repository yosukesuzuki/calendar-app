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
                return '<td class="aday %s today selected" id="%s">%d</td>' % (self.cssclasses[weekday], td_id, day)
            return '<td class="aday %s" id="%s">%d</td>' % (self.cssclasses[weekday], td_id, day)

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
        a('<table class="table table-bordered">')
        a('\n')
        a('<thead>')
        a('<tr>')
        a('<th class="left cmonth" id="%s">' % pre_month_id)
        a('<span class="glyphicon glyphicon-chevron-left" aria-hidden="true"></span></th>')
        a('<th colspan="5" class="center">%s/%s</th>' % (str(self.theyear), str(self.themonth)))
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
    return render_to_response('main/index.html', {'message': 'Hello', 'calendar': calendar_html})
