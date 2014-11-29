import logging, yaml, collections, numpy
from nltk.tokenize.regexp import RegexpTokenizer
from nltk.stem.porter import PorterStemmer
from nltk.cluster.gaac import GAAClusterer


def getTokenCount( description ):
  tokens = RegexpTokenizer(r'\w+').tokenize( description )
  tokens = [w.lower() for w in tokens]
  stopwords = yaml.load( open("backend/nltk/stopwords.yaml", "r") )
  tokens = [w for w in tokens if not w in stopwords]
  tokens = [w for w in tokens if len(w) > 2]
  stemmer = PorterStemmer()
  tokens = [stemmer.stem(w) for w in tokens]
  tokenCount = collections.Counter( tokens )
  return tokenCount

def buildNormalizedVector( tokenCount, wordSpace ):
  vectorLength = numpy.sqrt( numpy.sum( numpy.power( tokenCount.values(), 2 ) ) )
  vector = [0] * len(wordSpace)
  for term in tokenCount:
    vector[ wordSpace.index(term) ] = tokenCount[term] / vectorLength
  return vector

def getClusterer( vectors, numClusters, wordSpaceLength ):
  for vector in vectors:
    vector.extend( [0]*(wordSpaceLength-len(vector)) )
  clusterer = GAAClusterer(numClusters, False) 
  clusterer.cluster(vectors)
  return clusterer

def calculateSimilarity( vector1, vector2 ):
  shorterLength = min(len(vector1), len(vector2))
  return numpy.dot( vector1[:shorterLength], vector2[:shorterLength] )