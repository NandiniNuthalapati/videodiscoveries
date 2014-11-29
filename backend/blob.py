import urllib, logging, json
from google.appengine.api import users
from google.appengine.ext import ndb, blobstore, webapp
from google.appengine.ext.webapp import blobstore_handlers
from models import Video, User


BLOB_ROOT = '/blobstore/'
BLOB_UPLOAD_PATH = BLOB_ROOT + 'upload/'
BLOB_DOWNLOAD_PATH = BLOB_ROOT + '([^/]+)/.*'


class DownloadHandler(blobstore_handlers.BlobstoreDownloadHandler):
  def get(self, encodedBlobKey):
    blobKey = str( urllib.unquote( encodedBlobKey ) )
    blob_info = blobstore.BlobInfo.get( blobKey )
    if not blob_info:
      return self.error( 404 )
    if not users.get_current_user():
      return self.error( 401 )
    self.send_blob( blob_info )


class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
  def post(self):

    videoBlobInfo = self.get_uploads('video')
    screenshotBlobInfo = self.get_uploads('screenshot')
    title = self.request.get("title")
    description = self.request.get("description")

    if len( videoBlobInfo ) != 1 or len( screenshotBlobInfo ) != 1 or not title or not description:
      return self.uploadError( 400 )
    if not users.is_current_user_admin():
      return self.uploadError( 401 )

    uploadRoot = self.request.host_url + BLOB_ROOT
    videoBlobKey = str(videoBlobInfo[0].key())
    videoBlobUri = uploadRoot + videoBlobKey + "/" + videoBlobInfo[0].filename
    screenshotBlobKey = str(screenshotBlobInfo[0].key())
    screenshotBlobUri = uploadRoot + screenshotBlobKey + "/" + screenshotBlobInfo[0].filename
    userId = users.get_current_user().user_id()

    userEntity = User.getById( userId )
    videoEntity = Video(id=videoBlobKey, videoUri=videoBlobUri, screenshotUri=screenshotBlobUri, uploadUser=userId, title=title, description=description, vector=[])
    ndb.put_multi([userEntity, videoEntity])

    self.response.headers['Content-Type'] = 'application/json'
    self.response.out.write( json.dumps({ 'id' : videoBlobKey }) )

  def uploadError(self, errorCode):
    uploads = self.get_uploads()
    for blob in uploads:
      blob.delete()
    return self.error( errorCode )


app = webapp.WSGIApplication([
    (BLOB_UPLOAD_PATH, UploadHandler),
    (BLOB_DOWNLOAD_PATH, DownloadHandler)
])