"""Celery Tasks for the FOIA application"""

from celery.task import periodic_task, task
from celery.signals import task_failure
from celery.schedules import crontab
from django.core import management
from django.core.mail import send_mail
from django.template.loader import render_to_string
from sentry.client.handlers import SentryHandler
from settings import DOCUMNETCLOUD_USERNAME, DOCUMENTCLOUD_PASSWORD, \
                     GA_USERNAME, GA_PASSWORD, GA_ID


import dbsettings
import base64
import gdata.analytics.service
import json
import logging
import re
import urllib2
from datetime import date, timedelta
from vendor import MultipartPostHandler

from foia.models import FOIADocument, FOIARequest

foia_url = r'(?P<jurisdiction>[\w\d_-]+)/(?P<slug>[\w\d_-]+)/(?P<idx>\d+)'

logger = logging.getLogger('task')
logger.setLevel(logging.INFO)
if SentryHandler not in [x.__class__ for x in logger.handlers]:
    logger.addHandler(SentryHandler())

class FOIAOptions(dbsettings.Group):
    """DB settings for the FOIA app"""
    enable_followup = dbsettings.BooleanValue('whether to send automated followups or not')
options = FOIAOptions()

@task(ignore_result=True, max_retries=10)
def upload_document_cloud(doc_pk, change, **kwargs):
    """Upload a document to Document Cloud"""

    try:
        doc = FOIADocument.objects.get(pk=doc_pk)
    except FOIADocument.DoesNotExist, exc:
        # pylint: disable=E1101
        # give database time to sync
        upload_document_cloud.retry(args=[doc_pk, change], kwargs=kwargs, exc=exc)

    if doc.doc_id and not change:
        # not change means we are uploading a new one - it should not have an id yet
        return

    # these need to be encoded -> unicode to regular byte strings
    params = {
        'title': doc.title.encode('utf8'),
        'source': doc.source.encode('utf8'),
        'description': doc.description.encode('utf8'),
        'access': doc.access.encode('utf8'),
        'related_article': ('http://www.muckrock.com' + doc.foia.get_absolute_url()).encode('utf8'),
        }
    if change:
        params['_method'] = str('put')
        url = '/documents/%s.json' % doc.doc_id
    else:
        params['file'] = open(str(doc.document.path), 'rb')
        url = '/upload.json'

    opener = urllib2.build_opener(MultipartPostHandler.MultipartPostHandler)
    request = urllib2.Request('https://www.documentcloud.org/api/%s' % url, params)
    # This is just standard username/password encoding
    auth = base64.encodestring('%s:%s' % (DOCUMNETCLOUD_USERNAME, DOCUMENTCLOUD_PASSWORD))[:-1]
    request.add_header('Authorization', 'Basic %s' % auth)

    try:
        ret = opener.open(request).read()
        if not change:
        # pylint: disable=E1101
            info = json.loads(ret)
            doc.doc_id = info['id']
            doc.save()
            set_document_cloud_pages.apply_async(args=[doc.pk], countdown=1800)
    except urllib2.URLError, exc:
        # pylint: disable=E1101
        upload_document_cloud.retry(args=[doc.pk, change], kwargs=kwargs, exc=exc)


@task(ignore_result=True, max_retries=10)
def set_document_cloud_pages(doc_pk, **kwargs):
    """Get the number of pages from the document cloud server and save it locally"""

    doc = FOIADocument.objects.get(pk=doc_pk)

    if doc.pages:
        # already has pages set, just return
        return

    request = urllib2.Request('https://www.documentcloud.org/api/documents/%s.json' % doc.doc_id)
    # This is just standard username/password encoding
    auth = base64.encodestring('%s:%s' % (DOCUMNETCLOUD_USERNAME, DOCUMENTCLOUD_PASSWORD))[:-1]
    request.add_header('Authorization', 'Basic %s' % auth)

    try:
        ret = urllib2.urlopen(request).read()
        info = json.loads(ret)
        doc.pages = info['document']['pages']
        doc.save()
    except urllib2.URLError, exc:
        # pylint: disable=E1101
        set_document_cloud_pages.retry(args=[doc.pk], countdown=600, kwargs=kwargs, exc=exc)


@periodic_task(run_every=crontab(hour=1, minute=10))
def set_top_viewed_reqs():
    """Get the top 5 most viewed requests from Google Analytics and save them locally"""

    client = gdata.analytics.service.AnalyticsDataService()
    client.ClientLogin(GA_USERNAME, GA_PASSWORD)
    data = client.GetData(ids=GA_ID, dimensions='ga:pagePath', metrics='ga:pageviews',
                          start_date=(date.today() - timedelta(days=30)).isoformat(),
                          end_date=date.today().isoformat(), sort='-ga:pageviews')
    top_req_paths = [(entry.title.text, entry.pageviews) for entry in data.entry
                     if entry.title.text.startswith('ga:pagePath=/foi/view/')]
    path_re = re.compile('ga:pagePath=/foi/view/' + foia_url)

    for req_path, pageviews in top_req_paths:
        try:
            req = FOIARequest.objects.get(pk=path_re.match(req_path).group('idx'))
            req.times_viewed = pageviews
            req.save()
        except FOIARequest.DoesNotExist:
            pass



@periodic_task(run_every=crontab(hour=1, minute=0))
def update_index():
    """Update the search index every day at 1AM"""
    management.call_command('update_index')


@periodic_task(run_every=crontab(hour=5, minute=0))
def followup_requests():
    """Follow up on any requests that need following up on"""
    # change to this after all follows up have been resolved
    #for foia in FOIARequest.objects.get_followup(): 
    if options.enable_followup:
        for foia in FOIARequest.objects.filter(status='processed', date_followup__lte=date.today()):
            foia.followup()


@periodic_task(run_every=crontab(hour=6, minute=0))
def embargo_warn():
    """Warn users their requests are about to come off of embargo"""
    for foia in FOIARequest.objects.filter(embargo=True,
                                           date_embargo=date.today()+timedelta(1)):
        send_mail('[MuckRock] Embargo about to expire for FOI Request "%s"' % foia.title,
                  render_to_string('foia/embargo.txt', {'request': foia}),
                  'info@muckrock.com', [foia.user.email])


@periodic_task(run_every=crontab(hour=0, minute=0))
def set_all_document_cloud_pages():
    """Try and set all document cloud documents that have no page count set"""
    # pylint: disable=E1101
    for doc in FOIADocument.objects.filter(pages=0):
        set_document_cloud_pages.apply_async(args=[doc.pk])


def process_failure_signal(exception, traceback, sender, task_id,
                           signal, args, kwargs, einfo, **kw):
    """Log celery exceptions to sentry"""
    # http://www.colinhowe.co.uk/2011/02/08/celery-and-sentry-recording-errors/
    # pylint: disable=R0913
    # pylint: disable=W0613
    exc_info = (type(exception), exception, traceback)
    logger.error(
        'Celery job exception: %s(%s)' % (exception.__class__.__name__, exception),
        exc_info=exc_info,
        extra={
            'data': {
                'task_id': task_id,
                'sender': sender,
                'args': args,
                'kwargs': kwargs,
            }
        }
    )
task_failure.connect(process_failure_signal, dispatch_uid='muckrock.foia.tasks.logging')
