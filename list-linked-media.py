# -*- coding: utf-8 -*-

#
# Used to compile lists of links to local media
# which you might want to download and move to your static archive.
# This is useful when weeding out which media files to keep. (e.g.,
# maybe you had files uploaded for temporary use like I did.)
#

import parse_wordpress_export
from StringIO import StringIO
from bs4 import BeautifulSoup

domain = 'aralbalkan.com'
imagesFolder = '/images'
downloadsFolder = '/downloads'
uploadedMediaFolder = '/wp-content/uploads'

# Shorthand reference to the namespace.
wp = parse_wordpress_export

wp.parse()

linksLocal = []

# Get links from the WordPress export files
for post in wp.postsPublished:
	content = post['content']
	soup = BeautifulSoup(content, 'html5lib')
	linksInPost = soup.findAll('a')
	for linkSoup in linksInPost:
		try:
			link = unicode(linkSoup['href']).lower()
		except Exception:
			print u'Error with link in post ID ' + post['id'] + ': ' + unicode(linkSoup)
		if link.startswith('http://' + domain) or (not link.startswith('http')):
			linksLocal.append(link)

# Get links from any static content files
# TODO

for link in linksLocal:
	print link