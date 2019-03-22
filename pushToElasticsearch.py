from elasticsearch import Elasticsearch, helpers
from pprint import pprint
import os
import json

SCRIPT_DIR = os.path.dirname(__file__)
CLIENT = Elasticsearch()

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
	chat_index = filename.lower().replace('.','_').replace(' ','_')
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
	return helpers.bulk(CLIENT, yeild_messages(filename))

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