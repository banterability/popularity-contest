import wsgiref.handlers
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
import os

class Handler(webapp.RequestHandler):
    
    def respondWithText(self, text):
        self.response.out.write(text)
        self.response.out.write("\n")
    
    
    def respondWithJS(self, data):
        self.response.headers['Content-Type'] = "text/javascript"
        self.response.out.write(data)

        
    def respondWithTemplate(self, template_name, template_values={}):
        values = {
            'request': self.request,
        }
        
        values.update(template_values)
        directory = os.path.dirname(__file__)
        path = os.path.join(directory, os.path.join('templates', template_name))
        self.response.out.write(template.render(path, values))