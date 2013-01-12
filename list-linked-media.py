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

validDownloadFolders = set(['images', 'downloads', 'wp-content/uploads', 'presentations', 'swfs', 'code', 'demos', 'flas'])

links = set()
images = set()

allLinks = set()

# Shorthand reference to the namespace.
wp = parse_wordpress_export

wp.parse()

print '\nExamining local images and links in posts…\n'

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
            print u'\tError with link in post with id ' + post['id'] + ': ' + unicode(linkSoup)

        if link.startswith(u'http://' + domain) or link.startswith(u'http://www.' + domain) or (not link.startswith(u'http')):

            if not regularPostLinkRegex.match(link):

                for validDownloadFolder in validDownloadFolders:
                    if link.startswith(validDownloadFolder) or link.startswith('/' + validDownloadFolder) or link.startswith(u'http://' + domain + '/' + validDownloadFolder):
                        links.add(link)

                # Catch‐all
                allLinks.add(link)

    imagesInPost = soup.findAll('img')
    for linkSoup in imagesInPost:
        try:
            link = unicode(linkSoup['src']).lower()
        except Exception:
            print u'\tError with image source in post with id ' + post['id'] + ': ' + unicode(linkSoup)
        if link.startswith(u'http://' + domain) or link.startswith(u'http://www.' + domain) or (not link.startswith(u'http')):

                images.add(link)

numImages = len(images)
numLinks = len(links)

print '\nFound %d local images and %d links to local assets.\n' % (numImages, numLinks)

# Get links from any static content files
# TODO

# print u"Images (<img src='…'>)"
# print u"====================\n"

# print images

# print "\n===\n"


# print u"Links (<a href='…'>)"
# print u"====================\n"

# print links

# print "\n===\n"

# print "\n============\n"

# for link in allLinks:
#     print link
