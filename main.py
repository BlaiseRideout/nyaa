#!/usr/bin/env python2.7
import sys
import os.path
import os
import tornado.escape
import tornado.httpserver
from tornado.httpclient import AsyncHTTPClient
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.web import asynchronous
import tornado.template
import unicodedata
import requests
import re
from xml.dom.minidom import parseString

from tornado.options import define, options
define("port", default=5000, type=int)


class Searcher(tornado.web.RequestHandler):
	current_search = ""
	current_filter = "0"
	current_category = "0_0"

	def search(self, q, filter, category):
		link = "http://www.nyaa.se/?page=rss"

		if q != None:
			link += "&term=" + q
			self.current_search = q

		if filter != None:
			link += "&filter=" + filter
			self.current_filter = filter

		if category != None:
			link += "&cats=" + category
			self.current_category = category

		http_client = AsyncHTTPClient()
		http_client.fetch(link, self.handle_request)

	def handle_request(self, response):
		results = []
		if response.error:
			page_heading = title = "Error: " + response.error
		else:
			if str(response.headers).find('charset') != -1:
				charset = re.search("^Content-Type: text/xml; charset=(?P<charset>.*?)\r\n",str(response.headers))
				if charset != None:
					charset = charset.group('charset')
			if charset == None:
				charset = 'utf-8'

			xml = parseString(response.body.decode(charset).encode('utf-8')).getElementsByTagName('channel')[0]

			page_heading = title = xml.getElementsByTagName('title')[0].firstChild.nodeValue

			for item in xml.getElementsByTagName('item'):
				ititle = item.getElementsByTagName('title')[0].firstChild.nodeValue
				if ititle == None:
					break

				link = item.getElementsByTagName('link')[0].firstChild.nodeValue
				if link == None:
					break
				link += "&magnet=1"

                                req = requests.get(link, allow_redirects=False)
                                if req.status_code == 303:
                                    link = req.headers['location']

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

		self.render(
			"index.html",
			title = title,
			page_heading = page_heading,
			results = results,
			current_search = self.current_search,
			current_filter = self.current_filter,
			current_category = self.current_category
		)

#the main page
class MainHandler(Searcher):
	@asynchronous
	def get(self):
		self.search(None, None, None)

# the search page
class PlainSearchHandler(Searcher):
	@asynchronous
	def get(self, q):
		self.search(q, None, None)

# the advanced search page
class SearchHandler(Searcher):
	@asynchronous
	def get(self, filter, category, q):
		self.search(q, filter, category)

#description for a torrent
class DescriptionHandler(tornado.web.RequestHandler):
	@asynchronous
	def get(self, q):
		link = "http://www.nyaa.se/?page=view"

		if q != None:
			link += "&tid=" + q

		http_client = AsyncHTTPClient()
		http_client.fetch(link, self.handle_request)

	def handle_request(self, response):
		if response.error:
			description = "No description"
		else:
			if str(response.headers).find('charset') != -1:
				charset = re.search("^Content-Type: text/xml; charset=(?P<charset>.*?)\r\n",str(response.headers))
				if charset != None:
					charset = charset.group('charset')
				else:
					charset = 'utf-8'
			else:
				charset = 'utf-8'

			description = response.body.decode(charset).encode('utf-8')

		self.finish(description)

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

def main():
	if len(sys.argv) > 1:
		try:
			port = int(sys.argv[1])
		except:
			port = 5000
	else:
		port = 5000
	tornado.options.parse_command_line()
	AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
	http_server = tornado.httpserver.HTTPServer(Application())
	http_server.listen(os.environ.get("PORT", port))

	# start it up
	tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
	main()
