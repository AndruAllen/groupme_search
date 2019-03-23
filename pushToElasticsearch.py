from elasticsearch import Elasticsearch, helpers
from elasticsearch.exceptions import TransportError
from pprint import pprint
import os
import json

SCRIPT_DIR = os.path.dirname(__file__)
CLIENT = Elasticsearch()

DEFAULT_ANALYZER = {
    "analysis": {
      "filter": {
        "english_stop": {
          "type":       "stop",
          "stopwords":  "_english_" 
        },
        "english_keywords": {
          "type":       "keyword_marker",
          "keywords":   ["a&m"] 
        },
        "english_stemmer": {
          "type":       "stemmer",
          "language":   "english"
        },
        "english_possessive_stemmer": {
          "type":       "stemmer",
          "language":   "possessive_english"
        }
      },
      "analyzer": {
        "rebuilt_english": {
          "type":       "custom"
          "tokenizer":  "standard",
          "filter": [
            "english_possessive_stemmer",
            "lowercase",
            "english_stop",
            "english_keywords",
            "english_stemmer"
          ]
        }
      }
    }
  }

MESSAGE_MAPPING = {
        'message': {
          'properties': {
            'Sender': {'type': 'keyword'},
            'Text': {'type': 'text', 'analyzer': 'rebuilt_english'},
            'Timestamp': {'type': 'date', 'format': "format":"yyyy-MM-dd HH:mm"}
          }
        }
      }

def files_to_choose_from(relative_path = []):
  print("Expecting a list of directories from the current one, defaults to datafiles directory")
  if relative_path == []:
    relative_path.append('datafiles')
  path_of_files = os.path.join(SCRIPT_DIR,*relative_path) # * <- splat operator
  out_files = []
  with os.scandir(path_of_files) as entries:
    for entry in entries:
      if(entry.is_file()):
        out_files.append(entry)
  return path_of_files,out_files

def yeild_messages(filename):
  with open(os.path.join(SCRIPT_DIR,'datafiles', filename)) as file:
    for line in file:
      context = json.loads(line)
      yield   {
            "_index": chat_index,
            "_type": "message",
            "_source": {
              "Sender":context['sender'],
              "Text":context['text'],
              "Timestamp": context['date']
            }
          }

def push_from_file(filename):
  print("Indexing", filename)
  chat_index = filename.lower().replace('.','_').replace(' ','_')
  try:

    res = helpers.bulk(CLIENT, yeild_messages(filename, chat_index))
    return res
  except TransportError as e:
    if e.error == 'index_already_exists_exception':
            pass
        else:
      raise

filename = "Messages for D&D Is For The Boys.txt"
push_from_file(filename)

def searchByKeyword(filename, keyword):
  chat_index = filename.lower().replace('.','_').replace(' ','_')
  res = CLIENT.search(index=chat_index, doc_type="message", body={"size":100, "query": {"query_string": {"query": keyword}}})
  results = []
  for hit in res["hits"]["hits"]:
    results.append(hit["_source"])
  return results

def deleteIndex(filename):
  chat_index = filename.lower().replace('.','_').replace(' ','_')
  res = CLIENT.indices.delete(index=chat_index, ignore=[400, 404])
  return res