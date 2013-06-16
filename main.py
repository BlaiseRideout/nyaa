#	Sample main.py Tornado file
# 
#	Author: Mike Dory
#		11.12.11
#

#!/usr/bin/env python3
import os.path
import os
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.template
import unicodedata
import urllib
import re
from xml.dom.minidom import parseString

# import and define tornado-y things
from tornado.options import define, options
define("port", default=5000, help="run on the given port", type=int)

def search(self, q, filter, category):
	link = "http://www.nyaa.eu/?page=rss"

	if q != None:
		link += "&term=" + q
		current_search = q
	else:
		current_search = ""

	if filter != None:
		link += "&filter=" + filter
		current_filter = filter
	else:
		current_filter = "0"

	if category != None:
		link += "&cats=" + category
		current_category = category
	else:
		current_category = "0_0"

	linkopen = urllib.urlopen(link)

	if linkopen != None:
		if str(linkopen.headers).find('charset') != -1:
			charset = re.search("^Content-Type: text/xml; charset=(?P<charset>.*?)\r\n",str(linkopen.headers))
			if charset != None:
				charset = charset.group('charset')
		if charset == None:
			charset = 'utf-8'

		xml = parseString(linkopen.read().decode(charset).encode('utf-8')).getElementsByTagName('channel')[0]

		page_heading = title = xml.getElementsByTagName('title')[0].firstChild.nodeValue

		content = '<h3>Results:</h3>'

		results = []

		for item in xml.getElementsByTagName('item'):
			ititle = item.getElementsByTagName('title')[0].firstChild.nodeValue
			if ititle == None:
				break

#			id = re.search("http://www\.nyaa\.eu/\?page=download&tid=(?P<id>\d*)", item.getElementsByTagName('link')[0].firstChild.nodeValue)
#			if id != None:
#				id = id.group('id')
#			else:
#				break

			link = item.getElementsByTagName('link')[0].firstChild.nodeValue
			if link == None:
				break

			description = item.getElementsByTagName('description')[0].firstChild.nodeValue
			trusted = ""
			desc = re.search(r'(?P<A> - A\+)? - (?P<trusted>Remake|Trusted)', description)
			if desc != None:
				if desc.group('trusted') == "Remake":
					trusted = "remake"
				elif desc.group('trusted') == "Trusted":
					trusted = "trusted"
					if desc.group('A') != None:
						trusted = "aplus"
				description = re.sub(r'( - A\+)? - (Remake|Trusted)', "", description)

			if description == None:
				break

			result = {"title": ititle,
			          "link": link,
			          "description": description,
			          "trusted":  trusted }
			results.append(result)

	else:
		page_heading = title = "Error"

	self.render(
		"index.html",
		title = title,
		page_heading = page_heading,
		results = results,
		current_search = current_search,
		current_filter = current_filter,
		current_category = current_category
	)

			
#the main page
class MainHandler(tornado.web.RequestHandler):
	def get(self):
		search(self, None, None, None)

# the search page
class PlainSearchHandler(tornado.web.RequestHandler):
	def get(self, q):
		search(self, q, None, None)

class SearchHandler(tornado.web.RequestHandler):
	def get(self, filter, category, q):
		search(self, q, filter, category)

#description for a torrent
class DescriptionHandler(tornado.web.RequestHandler):
	def get(self, q):
		link = "http://www.nyaa.eu/?page=view"

		if q != None:
			link += "&tid=" + q

		linkopen = urllib.urlopen(link)

		if linkopen != None:
			if str(linkopen.headers).find('charset') != -1:
				charset = re.search("^Content-Type: text/xml; charset=(?P<charset>.*?)\r\n",str(linkopen.headers))
				if charset != None:
					charset = charset.group('charset')
				else:
					charset = 'utf-8'
			else:
				charset = 'utf-8'

			#for e in parseString(linkopen.read().decode(charset).encode('utf-8')).getElementsByTagName('div'):
			#	if e.attributes['class'] == 'viewdescription':
			#		description = e.firstChild.nodeValue

			description = linkopen.read().decode(charset).encode('utf-8')
		else:
			description = "No description"

		self.write(description)

# application settings and handle mapping info
class Application(tornado.web.Application):
	def __init__(self):
		handlers = [
			(r"/", MainHandler),
			(r"/search/(\d)/(\d_\d{1,2})/(.*)", SearchHandler),
			(r"/search/(.*)", PlainSearchHandler),
			(r"/description/(.*)", DescriptionHandler)
		]
		settings = dict(
			template_path = os.path.join(os.path.dirname(__file__), "templates"),
			static_path = os.path.join(os.path.dirname(__file__), "static"),
			debug = False,
		)
		tornado.web.Application.__init__(self, handlers, **settings)

# RAMMING SPEEEEEEED!
def main():
	tornado.options.parse_command_line()
	http_server = tornado.httpserver.HTTPServer(Application())
	http_server.listen(os.environ.get("PORT", 5000))

	# start it up
	tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
	main()
