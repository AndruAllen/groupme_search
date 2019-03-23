#pip install GroupyAPI

from groupy import Client
client = Client.from_token("yrrudwbqjnb8BbrDqZ6oAhLMfqPfGBaGt5Y97WqV")

groups = list(client.groups.list_all())

group = groups[0]
message = group.post(text='hi there testing again')
