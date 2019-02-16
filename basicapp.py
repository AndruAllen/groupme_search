# RESOURCE: http://www.apnorton.com/blog/2017/02/28/How-I-wrote-a-Groupme-Chatbot-in-24-hours/


# IMPORTS
import os
import json
import requests
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from flask import Flask, request

app = Flask(__name__)
bot_id = 'b423cb077ae898e45feb4a9a1e'

# Called whenever the app's callback URL receives a POST request
# That'll happen every time a message is sent in the group
@app.route('/', methods=['GET','POST'])
def webhook():
    # 'message' is an object that represents a single GroupMe message.
    message = request.get_json()
    message_text = message['text']

    if message_text[0] == '/':
        # If there are multiple spaces, GroupMe turns some of them into
        # \xa0. I'm not sure why. Replace them with a space
        message_text = message_text.replace(u'\xa0', ' ')
        # The command should be the first word (split by whitespace),
        # while the arguments will be passed as a list
        split_message = message_text.split()
        command = split_message[0]
    print(message)
    print(message_text)
    
    if(message['sender_type'] != 'bot'):
        reply("Hi, "+message['name'])

    return "ok", 200

################################################################################

# Send a message in the groupchat
def reply(msg):
	url = 'https://api.groupme.com/v3/bots/post'
	data = {
		'bot_id'		: bot_id,
		'text'			: msg
	}
	request = Request(url, urlencode(data).encode())
	json = urlopen(request).read().decode()

# Send a message with an image attached in the groupchat
def reply_with_image(msg, imgURL):
	url = 'https://api.groupme.com/v3/bots/post'
	urlOnGroupMeService = upload_image_to_groupme(imgURL)
	data = {
		'bot_id'		: bot_id,
		'text'			: msg,
		'picture_url'		: urlOnGroupMeService
	}
	request = Request(url, urlencode(data).encode())
	json = urlopen(request).read().decode()
	
# Uploads image to GroupMe's services and returns the new URL
def upload_image_to_groupme(imgURL):
	imgRequest = requests.get(imgURL, stream=True)
	filename = 'temp.png'
	postImage = None
	if imgRequest.status_code == 200:
		# Save Image
		with open(filename, 'wb') as image:
			for chunk in imgRequest:
				image.write(chunk)
		# Send Image
		headers = {'content-type': 'application/json'}
		url = 'https://image.groupme.com/pictures'
		files = {'file': open(filename, 'rb')}
		payload = {'access_token': 'eo7JS8SGD49rKodcvUHPyFRnSWH1IVeZyOqUMrxU'}
		r = requests.post(url, files=files, params=payload)
		imageurl = r.json()['payload']['url']
		os.remove(filename)
		return imageurl

# Checks whether the message sender is a bot
def sender_is_bot(message):
        return message['sender_type'] == "bot"

reply('hello there from port 5000')
