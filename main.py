#!/usr/bin/env python
#
from __future__ import with_statement

from google.appengine.api import files

import os
import urllib
import calendar


import StringIO
import gzip

import hashlib

from google.appengine.ext import blobstore
from google.appengine.ext import webapp
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

class MainHandler(webapp.RequestHandler):
    def get(self):
        upload_url = blobstore.create_upload_url('/upload')
        self.response.headers.add_header("Access-Control-Allow-Origin", "*")
        self.response.out.write('<html><body>')
        self.response.out.write('<form action="%s" method="POST" enctype="multipart/form-data">' % upload_url)
        self.response.out.write("""Upload File: <input type="file" name="file"><br> <input type="submit" 
            name="submit" value="Submit"> </form></body></html>""")

class InputHandler(webapp.RequestHandler):
    def get(self):
        self.response.headers.add_header("Access-Control-Allow-Origin", "*")
        self.response.out.write('<html><body>')
        self.response.out.write('<form action="/store" method="POST">')
        self.response.out.write("""Upload File: <textarea name="file" cols=80 rows=25></textarea><br> <input type="submit" 
            name="submit" value="Submit"> </form></body></html>""")

class FileHandler(webapp.RequestHandler):
    def post(self):
        # we want a better way of getting 
        encodedContent = self.request.get('file').encode('utf-8')
        filehash_name = hashlib.sha1(encodedContent).hexdigest()
        file_name = files.gs.create('/gs/profile-store/' + filehash_name, mime_type='plain/text', acl='public-read',content_encoding='gzip')

        # Open the file and write to it
        with files.open(file_name, 'a') as f:
              # this should do the trick
              out = StringIO.StringIO()
              gf = gzip.GzipFile(fileobj=out, mode='w')
              gf.write(encodedContent)
              gf.close()
              f.write(out.getvalue())

        # Finalize the file. Do this before attempting to read it.
        files.finalize(file_name)
        
        # Get the file's blob key
        #self.redirect('/serve/%s' % blob_key)
        self.response.headers.add_header("Access-Control-Allow-Origin", "*")
        self.response.out.write(filehash_name)
    def options(self):
        self.response.headers.add_header("Access-Control-Allow-Origin", "*")
        self.response.out.write("Food");
        pass

class TestFileHandler(webapp.RequestHandler):
    def post(self):
        # we want a better way of getting 
        encodedContent = self.request.get('file').encode('utf-8')
        filehash_name = hashlib.sha1(encodedContent).hexdigest()
        
        # this should do the trick
        out = StringIO.StringIO()
        gf = gzip.GzipFile(fileobj=out, mode='w')
        gf.write(encodedContent)
        gf.close()
        self.response.write(out.getvalue())


        # Get the file's blob key
        #self.redirect('/serve/%s' % blob_key)
        self.response.headers.add_header("Access-Control-Allow-Origin", "*")
        self.response.out.write(filehash_name)
    def options(self):
        self.response.headers.add_header("Access-Control-Allow-Origin", "*")
        self.response.out.write("Food");
        pass


class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        upload_files = self.get_uploads('file')  # 'file' is file upload field in the form
        blob_info = upload_files[0]
        self.redirect('/serve/%s' % blob_info.key())

class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, resource):
        self.response.headers.add_header("Access-Control-Allow-Origin", "*")
        #Calendar future = Calendar.getInstance();
        #future.add(Calendar.YEAR, +1);
        #self.response.setDateHeader("Expires", future.getTimeInMillis());
        self.response.headers["Cache-control"] = "max-age=30";
        self.response.headers['Content-Encoding'] = 'gzip'
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        self.send_blob(blob_info, content_type="text/plain; charset=utf-8")

class ListHandler(webapp.RequestHandler):
    def get(self):
        self.response.headers.add_header("Access-Control-Allow-Origin", "*")
        self.response.out.write('<html><body>')
        self.response.out.write('count: ' + str(blobstore.BlobInfo.all().count()))


def main():
    application = webapp.WSGIApplication(
          [('/', MainHandler),
           ('/upload', UploadHandler),
           ('/input', InputHandler),
           ('/store', FileHandler),
           ('/test-store', TestFileHandler),
           ('/list', ListHandler),
           ('/serve/([^/]+)?', ServeHandler),
          ], debug=True)
    run_wsgi_app(application)

if __name__ == '__main__':
  main()
