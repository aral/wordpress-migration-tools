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

linksToImages = set()
linksToDownloads = set()
linksToUploadedMedia = set()

imagesInImages = set()
imagesInDownloads = set()
imagesInUploadedMedia = set()

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
                    linksToImages.add(link)

                if link.startswith(downloadsFolder) or link.startswith('/' + downloadsFolder) or link.startswith(u'http://' + domain + '/' + downloadsFolder):
                    # download
                    linksToDownloads.add(link)

                if link.startswith(uploadedMediaFolder) or link.startswith('/' + uploadedMediaFolder) or link.startswith(u'http://' + domain + '/' + uploadedMediaFolder):
                    # uploaded media
                    linksToUploadedMedia.add(link)

                linksLocal.append(link)

    imagesInPost = soup.findAll('img')
    for linkSoup in imagesInPost:
        try:
            link = unicode(linkSoup['src']).lower()
        except Exception:
            print u'Error with image source in post with id ' + post['id'] + ': ' + unicode(linkSoup)
        if link.startswith(imagesFolder) or link.startswith('/' + imagesFolder) or link.startswith(u'http://' + domain + '/' + imagesFolder):
            # image
            imagesInImages.add(link)

        if link.startswith(downloadsFolder) or link.startswith('/' + downloadsFolder) or link.startswith(u'http://' + domain + '/' + downloadsFolder):
            # download
            imagesInDownloads.add(link)

        if link.startswith(uploadedMediaFolder) or link.startswith('/' + uploadedMediaFolder) or link.startswith(u'http://' + domain + '/' + uploadedMediaFolder):
            # uploaded media
            imagesInUploadedMedia.add(link)

# Get links from any static content files
# TODO

print u"Images (<img src='…'>)"
print u"====================\n"

print imagesFolder + "\n"
print imagesInImages
print "\n===\n"

print downloadsFolder + "\n"
print imagesInDownloads
print "\n===\n"

print uploadedMediaFolder + "\n"
print imagesInUploadedMedia
print "\n===\n"


print u"Links (<a href='…'>)"
print u"====================\n"

print imagesFolder + "\n"
print linksToImages
print "\n===\n"

print downloadsFolder + "\n"
print linksToDownloads
print "\n===\n"

print uploadedMediaFolder + "\n"
print linksToUploadedMedia
print "\n===\n"

# print "\n============\n"

# for link in linksLocal:
#     print link
