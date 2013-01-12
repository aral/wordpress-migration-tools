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
import re

domain = 'aralbalkan.com'
imagesFolder = 'images'
downloadsFolder = 'downloads'
uploadedMediaFolder = 'wp-content/uploads'

images = set()
downloads = set()
uploadedMedia = set()

# Shorthand reference to the namespace.
wp = parse_wordpress_export

wp.parse()

linksLocal = []

regularPostLinkPattern = u'http://' + domain.replace('.', '\\.') + '/\d{1,4}'

regularPostLinkRegex = re.compile(regularPostLinkPattern)

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
        if link.startswith(u'http://' + domain) or link.startswith(u'http://www.' + domain) or (not link.startswith(u'http')):

            if not regularPostLinkRegex.match(link):

                if link.startswith(imagesFolder) or link.startswith('/' + imagesFolder) or link.startswith(u'http://' + domain + '/' + imagesFolder):
                    # image
                    images.add(link)

                if link.startswith(downloadsFolder) or link.startswith('/' + downloadsFolder) or link.startswith(u'http://' + domain + '/' + downloadsFolder):
                    # download
                    downloads.add(link)

                if link.startswith(uploadedMediaFolder) or link.startswith('/' + uploadedMediaFolder) or link.startswith(u'http://' + domain + '/' + uploadedMediaFolder):
                    # uploaded media
                    uploadedMedia.add(link)

                linksLocal.append(link)

# Get links from any static content files
# TODO


print "Images:\n"
print images
print "\n===\n"

print "Downloads:\n"
print downloads
print "\n===\n"

print "Uploaded media:\n"
print uploadedMedia
print "\n===\n"

# print "\n============\n"

# for link in linksLocal:
#     print link
