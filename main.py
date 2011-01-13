import os
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from helpers import *
from models import count_hit, get_all_counts

class MainHandler(Handler):
    def get(self):
        results = get_all_counts()
        self.respondWithTemplate('index.html', {'results': results[:20]})
        

class CountHandler(Handler):
    def get(self):
        callback = self.request.get('callback')
        url = self.request.get('url')
        title = self.request.get('title')
        count_hit(url, title)
        self.respondWithJS('%s({"stat": "ok","data": {"url":"%s", "title": "%s"}})' % (callback, url, title))


def main():
    application = webapp.WSGIApplication([
        ('/', MainHandler),
        ('/count/', CountHandler)
    ], debug=False)
    
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
