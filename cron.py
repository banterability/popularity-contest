from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from helpers import *
from models import sweep_old_hits, queue_score_updates, get_all_counts
from google.appengine.api import memcache


class HitSweeper(Handler):
    def get(self):
        sweep_old_hits()
        self.respondWithText("Old hits removed.")


class RefreshCounts(Handler):
    def get(self):
        queue_score_updates()
        self.respondWithText("Hit refreshes queued.")


class UpdateHomepage(Handler):
    def get(self):
        get_all_counts(force_update=True)
        self.respondWithText("Updated homepage")
        
        
def main():
  application = webapp.WSGIApplication([('/cron/sweep/', HitSweeper),
                                        ('/cron/score/', RefreshCounts),
                                        ('/cron/homepage/', UpdateHomepage)],
                                       debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
