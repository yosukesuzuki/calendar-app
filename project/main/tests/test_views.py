# -*- coding: utf-8 -*-

import datetime
import icalendar
import urlparse
from kay.ext.testutils.gae_test_base import GAETestBase
from kay.app import get_application
from werkzeug import BaseResponse, Client

from core.models import Event


class DownloadicsTest(GAETestBase):

    def setUp(self):
        app = get_application()
        self.client = Client(app, BaseResponse)

        self.test_values_0 = {
            'date': datetime.datetime(2216, 5, 20, 15, 0),
            'title': 'THIS IS TITLE',
            'description': 'THIS IS SUMMARY',
        }

        self.test_values_1 = {
            'date': datetime.datetime(2216, 6, 20, 15, 0),
            'title': 'THIS IS ALSO TITLE',
            'description': 'THIS IS ALSO SUMMARY',
        }

        eve_0 = Event(
            event_date=self.test_values_0['date'],
            title=self.test_values_0['title'],
            description=self.test_values_0['description'],
        )

        eve_1 = Event(
            event_date=self.test_values_1['date'],
            title=self.test_values_1['title'],
            description=self.test_values_1['description'],
        )

        eve_0.put()
        eve_1.put()
        events = Event.all().fetch(100)
        self.assertEquals(len(events), 2)
        self.assertEquals(events[0].title, 'THIS IS TITLE')
        self.event_key = str(events[0].key())

    def test_download_individual_icsfile(self):
        target_url = urlparse.urljoin('/ical/', self.event_key)
        res = self.client.get(target_url)
        self.assertEquals(res.status_code, 200)

        downloaded = res.get_data()
        reparsed = icalendar.Calendar.from_ical(downloaded)
        reparsed_eve = reparsed.walk('VEVENT')[0]
        stringfied = self.test_values_0['date'].strftime('%Y%m%dT%H%M%S')
        self.assertEquals(reparsed_eve['summary'].to_ical(), self.test_values_0['title'])
        self.assertEquals(reparsed_eve['dtstart'].to_ical(), stringfied)
        self.assertEquals(reparsed_eve['description'].to_ical(), self.test_values_0['description'])

    def test_download_all_events_icsfile(self):
        target_url = urlparse.urljoin('/ical/', 'future')
        res = self.client.get(target_url)
        self.assertEquals(res.status_code, 200)

        downloaded = res.get_data()
        reparsed = icalendar.Calendar.from_ical(downloaded)
        reparsed_eve = reparsed.walk('VEVENT')[1]
        stringfied = self.test_values_1['date'].strftime('%Y%m%dT%H%M%S')
        self.assertEquals(reparsed_eve['summary'].to_ical(), self.test_values_1['title'])
        self.assertEquals(reparsed_eve['dtstart'].to_ical(), stringfied)
        self.assertEquals(reparsed_eve['description'].to_ical(), self.test_values_1['description'])
