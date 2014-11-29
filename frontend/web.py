import os, jinja2, webapp2


JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
                                       extensions=['jinja2.ext.autoescape'],
                                       autoescape=True)


class ViewVideos(webapp2.RequestHandler):
  def get(self):
    template = JINJA_ENVIRONMENT.get_template('templates/view.html')
    self.response.write( template.render() )


class UploadVideos(webapp2.RequestHandler):
  def get(self):
    template = JINJA_ENVIRONMENT.get_template('templates/upload.html' )
    self.response.write( template.render() )


app = webapp2.WSGIApplication([
  ('/', ViewVideos),
  ('/upload/', UploadVideos)
], debug=True)
