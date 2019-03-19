from elasticsearch import Elasticsearch, helpers
import os.path
import json

SCRIPT_DIR = os.path.dirname(__file__)
CLIENT = Elasticsearch()

def yeild_messages(filename):
	chat_index = filename.lower().replace('.','').replace(' ','_')
	with open(os.path.join(SCRIPT_DIR,'datafiles', filename)) as file:
		stop = False
		for line in file:
			context = json.loads(line)
			if(not stop):
				print(context)
				stop = True
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
	print(helpers.bulk(CLIENT, yeild_messages(filename)))
