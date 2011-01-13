from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from helpers import *
from google.appengine.ext import db
from models import get_score_for_page, set_score_for_page


class ScoreWorker(Handler):
    def post(self):
        page = self.request.get('page')
        get_score_for_page(page)
        return


class SaveWorker(Handler):
    def post(self):
        page = self.request.get('page')
        score = self.request.get('score')
        set_score_for_page(page, score)
        return


class SweepWorker(Handler):
    def post(self):
        hit = self.request.get('hit')
        db.delete(hit)
        return
        
        
def main():
    application = webapp.WSGIApplication([
        ('/tasks/score/', ScoreWorker),
        ('/tasks/save/', SaveWorker),
        ('/tasks/sweep/', SweepWorker)
    ], debug=False)
    
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
