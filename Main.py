#!/usr/bin/python
#  -*- coding: utf-8 -*-
import json
from httplib2 import Http
from oauth2client.client import SignedJwtAssertionCredentials
from apiclient import discovery
from flask import Flask, abort, jsonify, request
import dateutil.parser
import sys
from pymongo import MongoClient

app = Flask(__name__)
client_email = '361097538251-buo76d3ktk5v3unlabn97ge9s8qh9h8n@developer.gserviceaccount.com'
calID = '473qbnl747l0ihede5901ukqfc@group.calendar.google.com'
dbClient = MongoClient('localhost', 27017)
db = dbClient.GoogleCalenderPoster
postedBooks = db.postedBooks


@app.route('/book', methods=['POST'])
def index():
    jsondata = request.get_json()
    if 'bookname' not in jsondata or 'publish_date' not in jsondata:
        abort(400, "Bookname and publish date is required.")

    publish_date = dateutil.parser.parse(jsondata['publish_date'])
    desc = str()
    if 'subbookname' in jsondata:
        jsondata['bookname'] += " %s" % jsondata['subbookname']
    if 'author' in jsondata:
        desc += "%s\n" % jsondata['author']
    if 'cover_image' in jsondata:
        desc += "封面圖片: %s\n" % jsondata['cover_image']
    if 'link' in jsondata:
        desc += "詳細資料: %s\n" % jsondata['link']
    if 'price' in jsondata:
        desc += "定價: %s\n" % jsondata['price']
    if 'publish_date' in jsondata:
        desc += "發售日期: %s\n" % jsondata['publish_date']

    if postedBooks.find_one({u"bookname": jsondata['bookname']}) is not None:
        abort(400, "Content already exists.")

    with open("My Project-c50dae1a95a3-notasecret.p12") as f:
        private_key = f.read()

    credentials = SignedJwtAssertionCredentials(client_email, private_key,
    'https://www.googleapis.com/auth/calendar')

    http = Http()
    credentials.authorize(http)

    service = discovery.build('calendar', 'v3', http=http)

    event = {
      'summary': jsondata['bookname'],
      'description': desc,
      'start': {
        'date': publish_date.strftime('%Y-%m-%d'),
        'timeZone': 'Asia/Taipei',
      },
      'end': {
        'date': publish_date.strftime('%Y-%m-%d'),
        'timeZone': 'Asia/Taipei',
      }
    }

    event = service.events().insert(calendarId=calID, body=event).execute()
    postedBooks.insert({'bookname': jsondata['bookname']})
    return jsonify({'message': 'Event created: %s' % (event.get('htmlLink'))})

if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf-8')
    app.run(host='0.0.0.0', debug=True, port=1864)