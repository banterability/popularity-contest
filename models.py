from google.appengine.ext import db
from datetime import datetime, timedelta
from google.appengine.api import memcache
from google.appengine.api import taskqueue
import logging

#### Score Helpers ####
# based on http://amix.dk/blog/post/19574
GRAVITY = 0.9  # default: 1.8
WINDOW = 18  # max age in hours

def hours_from_dt(dt):
    delta = datetime.now() - dt
    hrs = 0
    if delta.days > 0:
        hrs = delta.days * 24
    hrs += delta.seconds / 3600
    return hrs


def score(age, gravity=GRAVITY):
    hour_age = hours_from_dt(age)
    if hour_age > WINDOW:
        return 0
    else:
        return 1 / pow((hour_age + 1), gravity)


#### DB Models ####
class Page(db.Model):
    """Tracks page title by URL"""
    url = db.LinkProperty(required=True)
    title = db.StringProperty(required=True)
    score = db.FloatProperty()


class Hit(db.Model):
    url = db.LinkProperty(required=True)
    created_at = db.DateTimeProperty(auto_now=True)
    page = db.ReferenceProperty(Page)


#### Model Convenience Methods ####
def strip_qs_and_hash(uri):
    index = uri.find('?')
    if index != -1:
        uri = uri[:index]

    index = uri.find('#')
    if index != -1:
        uri = uri[:index]
    return uri


def rewrite_ips(url):
    return url.replace('66.226.4.226/','www.scpr.org/').replace('66.226.4.227/','www.scpr.org/')


def normalize_url(url):
    return strip_qs_and_hash(rewrite_ips(url))


def count_hit(url, title):
    clean_url = normalize_url(url)
    
    page = Page.all().filter('url = ', clean_url).get()
    if page:
        page.title = title
    else:
        page = Page(url=clean_url, title=title)
    db.put(page)
    
    hit = Hit(url= clean_url, page=page)
    db.put(hit)
    return


def get_score_for_page(page):
    total_score = 0
    p = db.get(page)
    for hit in p.hit_set:
        this_score = score(hit.created_at)
        total_score += this_score
        if this_score == 0:
            hit.delete()
    if total_score == 0:
        p.delete()
    else:
        taskqueue.add(queue_name='db-saves', url='/tasks/save/', params={'page': p.key(), 'score': total_score})
    return


def set_score_for_page(page, score):
    p = db.get(page)
    p.score = float(score)
    p.put()
    return


def queue_score_updates():
    pages = Page.all(keys_only=True)
    for page in pages:
        taskqueue.add(queue_name='score-calculation', url='/tasks/score/', params={'page': page})
    return


def get_all_counts(force_update=False):
    homepage_key = "homepage:all-scores"
    results = memcache.get(homepage_key)
    if force_update == True:
        results = None
    if results == None:
        results = []
        results = Page.all().order('-score').fetch(25)
        memcache.set(homepage_key, results)
    return results


def sweep_old_hits():
    old_hits = Hit.all(keys_only=True).filter('created_at < ', datetime.now() - timedelta(hours=WINDOW))
    logging.info("Purging %s hits" % old_hits.count())
    for hit in old_hits:
        taskqueue.add(queue_name='db-saves', url='/tasks/sweep/', params={'hit': hit})
    return