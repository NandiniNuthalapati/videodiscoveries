import sys, logging, endpoints
sys.path.append( 'backend' ) # For importing NLTK in subfolder
from google.appengine.ext import blobstore
from protorpc import remote, messages, message_types
from models import Video, User
from blob import BLOB_UPLOAD_PATH


class UploadUrlResponse(messages.Message):
  uploadUrl = messages.StringField(1)

class VideoResponse(messages.Message):
  id = messages.StringField(1)
  title = messages.StringField(2)
  description = messages.StringField(3)
  videoUri = messages.StringField(4)
  screenshotUri = messages.StringField(5)
  similarity = messages.FloatField(6)
  clusterGroup = messages.IntegerField(7)

class VideoListRequest(messages.Message):
  referenceId = messages.StringField(1)
  limit = messages.IntegerField(2, default=4)

class VideoListResponse(messages.Message):
  logging.info("building VideoList")
  items = messages.MessageField( VideoResponse, 1, repeated=True )

class ViewedVideoMessage(messages.Message):
  viewedVideoIds = messages.StringField(1, repeated=True)

def ViewedVideoListToMessage( viewedVideoList ):
  return ViewedVideoMessage( viewedVideoIds=viewedVideoList )

def VideoListToMessage( videoList ):
  return VideoListResponse( items=[VideoToMessage(video) for video in videoList] )

def VideoToMessage( video ):
  return VideoResponse( id=video.key.string_id(), title=video.title, description=video.description, videoUri=video.videoUri, screenshotUri=video.screenshotUri, similarity=video.similarity, clusterGroup=video.clusterGroup)


@endpoints.api(name='videodiscovery', version='v1', description='Video Discovery API', allowed_client_ids=[endpoints.API_EXPLORER_CLIENT_ID, '337666371549-tur26e822fdqtim89majsuo4n8mvvefh.apps.googleusercontent.com'])
class VideoDiscoveryAPI(remote.Service):


  @endpoints.method(message_types.VoidMessage, UploadUrlResponse, path='upload', http_method='GET', name='upload.get')
  def get_upload_url(self, request):
    self.validateCurrentUser()
    return UploadUrlResponse( uploadUrl = blobstore.create_upload_url( BLOB_UPLOAD_PATH ) )


  @endpoints.method(VideoListRequest, VideoListResponse, path='videos', http_method='GET', name='videos.list' )
  def list_videos(self, request):

    currentUserEntity = self.getCurrentUser()

    referenceId = None
    if request.referenceId:
      referenceId = request.referenceId
    elif currentUserEntity.viewedVideoIds:
      referenceId = currentUserEntity.viewedVideoIds[-1]

    videos = Video.query().fetch()
    referenceVideo = None
    if referenceId:
      referenceVideo = videos.pop( [ video.key.string_id() for video in videos].index( referenceId ) )
    videos = [video for video in videos if video.key.string_id() not in currentUserEntity.viewedVideoIds]

    if referenceVideo:
      for video in videos:
        video.calculateSimilarity( referenceVideo.vector )
      videos.sort( key=lambda x: x.similarity, reverse=True )

    return VideoListToMessage( videos[0:request.limit] )


  @endpoints.method(ViewedVideoMessage, ViewedVideoMessage, path='user/viewedVideoIds', http_method='PUT', name='viewedVideoIds.set' )
  def set_viewed_ids(self, request):
    currentUserEntity = self.getCurrentUser()
    currentUserEntity.viewedVideoIds = request.viewedVideoIds
    currentUserEntity.put()
    return ViewedVideoListToMessage( currentUserEntity.viewedVideoIds )


  @endpoints.method(ViewedVideoMessage, ViewedVideoMessage, path='user/viewedVideoIds', http_method='POST', name='viewedVideoIds.update' )
  def update_viewed_ids(self, request):
    currentUserEntity = self.getCurrentUser()
    if request.viewedVideoIds:
      currentUserEntity.viewedVideoIds += request.viewedVideoIds
      currentUserEntity.put()
    return ViewedVideoListToMessage( currentUserEntity.viewedVideoIds )


  @classmethod
  def getCurrentUser(self):
    self.validateCurrentUser()
    return User.getById( endpoints.get_current_user().user_id() )


  @classmethod
  def validateCurrentUser(self):
    if not endpoints.get_current_user():
      raise endpoints.UnauthorizedException('Invalid token.')

app = endpoints.api_server([VideoDiscoveryAPI])