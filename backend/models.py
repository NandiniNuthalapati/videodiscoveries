import description_analysis, logging, endpoints
from google.appengine.ext import ndb, deferred
from google.appengine.api import oauth
from protorpc import messages


class Video(ndb.Model):

  NUM_CLUSTERS = 3

  title = ndb.StringProperty(required=True, indexed=False)
  description = ndb.StringProperty(required=True, indexed=False)
  vector = ndb.JsonProperty(indexed=False)
  videoUri = ndb.StringProperty(indexed=False, required=True)
  screenshotUri = ndb.StringProperty(indexed=False, required=True)
  uploadDate = ndb.DateTimeProperty(auto_now_add=True, required=True)
  clusterGroup = ndb.IntegerProperty(default=0, required=True)
  uploadUser = ndb.StringProperty(indexed=False, required=True)

  similarity = None

  def _pre_put_hook(self):
    oldVideo = self.key.get(use_cache=False)
    if not oldVideo or oldVideo.description != self.description:
      self.updateVector()

  def calculateSimilarity(self, referenceVector):
    self.similarity = description_analysis.calculateSimilarity(self.vector, referenceVector)

  def updateVector(self):
    tokenCount = description_analysis.getTokenCount( self.description )
    wordSpace = Vocabulary.updateVocabulary( tokenCount )
    self.vector = description_analysis.buildNormalizedVector( tokenCount, wordSpace )
    deferred.defer( self.updateClustering, len(wordSpace), _countdown=60 )

  @classmethod
  def updateClustering(self, wordSpaceLength):
    videos = self.query().fetch()
    vectors = [video.vector for video in videos]

    if len(vectors) >= self.NUM_CLUSTERS:
      clusterer = description_analysis.getClusterer( vectors, self.NUM_CLUSTERS, wordSpaceLength )
      for video in videos:
        video.clusterGroup = clusterer.classify( video.vector )
      ndb.put_multi_async(videos)


class User( ndb.Model ):

  viewedVideoIds = ndb.JsonProperty(indexed=False)

  @classmethod
  def getById(self, userId):
    currentUserEntity = self.get_or_insert( userId )
    if not currentUserEntity.viewedVideoIds:
      currentUserEntity.viewedVideoIds = []
    return currentUserEntity

  def _pre_put_hook(self):
    seen = set()
    self.viewedVideoIds = [x for x in self.viewedVideoIds if x not in seen and not seen.add(x)]


class Vocabulary( ndb.Model ):

  ID = 'Vocabulary'
  wordSpace = ndb.JsonProperty(indexed=False)

  @classmethod
  def getVocabulary( self ):
    vocabularyEntity = self.get_or_insert( self.ID )
    if not vocabularyEntity.wordSpace:
      vocabularyEntity.wordSpace = []
    return vocabularyEntity

  @classmethod
  def updateVocabulary( self, tokenCount ):
    vocabularyEntity = self.getVocabulary()
    for term in tokenCount:
      if not term in vocabularyEntity.wordSpace:
        vocabularyEntity.wordSpace.append( term )
    vocabularyEntity.put_async()
    return vocabularyEntity.wordSpace