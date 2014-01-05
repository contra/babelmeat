import os
import glob
import sys
import re
import random
import json
import base64 
import hashlib
from random import choice
from socketIO_client import SocketIO
import goslate

def get_gif (filename):
    """get a gif from the filesystem and base64 encode it"""

    with open (filename, "rb") as image_file:
        data =  base64.b64encode(image_file.read())
        gif = "data:image/gif;base64," + data
        return gif

def get_txt (filename):
    """create a collection from a text file"""

class Babelfish(object):

    def __init__(self):

        with open ('babelfish.json', 'r') as conf:
            self.config = json.load(conf)

        self.api_key = self.config["key"]
        self.address = self.config["address"]
        self.gif = get_gif("babelfish.gif")
        self.gs = goslate.Goslate()

    def get_post (self, data):
        """extract wanted information from meatspace post"""
        post = {}
        post["key"] = data["chat"]["key"]
        post["message"] = data["chat"]["value"]["message"]
        return post

    def get_message (self, reply, image, fingerprint):
        """given a reply string and an image, construct a response"""

        message = {}
        message ['apiKey'] = self.api_key
        message ['message'] = reply
        message ['fingerprint'] = fingerprint
        message ['picture'] = image
        return message

    def send_message (self, reply, image, fingerprint):
        """send a message to meatspace"""

        SocketIO(self.address).emit('message', self.get_message(reply, image, fingerprint))

    def on_message(self, *args):
        """handles incoming messages from meatspace"""
        post = self.get_post (args[0])
        match = re.search(r'(!tr)-(\w+) (.+) ', post['message'])
        if match:
            self.send_message(self.gs.translate(match.group(3), match.group(2)), self.gif, "babelfish")

    def run (self):
        """start the bot"""

        with SocketIO(self.address) as socketIO_listen:
            socketIO_listen.on('message', self.on_message)
            socketIO_listen.wait()

if __name__ == '__main__':
    bot = Babelfish()
    bot.run()
