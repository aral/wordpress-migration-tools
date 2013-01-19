# -*- coding: utf-8 -*-

#
# Used to compile lists of links to local media
# from the HTML in files in the static folder.
#

from bs4 import BeautifulSoup
import re
import os
import urllib2

#
# Options
#
# TODO: Make into a command‐line arguments.
dryRun = True

domain = 'aralbalkan.com'

validDownloadFolders = set(['images', 'downloads', 'wp-content/uploads', 'presentations', 'swfs', 'code', 'demos', 'flas'])


#
# Containers
#
links = set()
images = set()

allLinks = set()


#
# Helpers
#

def makeRelativeLink(link):
    #
    # Massage the link to remove possible domain
    #
    link = link.replace('http://' + domain + '/', '')
    if link[0] == '/':
        # Also replace trailing slashes, if any
        link = link[1:]
    return link


def download(relativePath):
    pathComponents = relativePath.split('/')
    path = '/'.join(pathComponents[:-1])
    path = 'build/' + path
    fileName = pathComponents[-1]

    if fileName == '':
        print 'Info: %s is a folder not a file. Skipping.' % relativePath
        return

    outputFilePath = path + '/' + fileName

    url = 'http://%s/%s' % (domain, relativePath)

    if dryRun:
        print '%s => %s (%s)' % (path, fileName, url)
    else:
        #
        # Not a dry run, actually download the files.
        #

        # Create the local folder to hold the file
        if not os.path.exists(path):
            os.makedirs(path)

        #
        # Courtesy http://stackoverflow.com/questions/22676/how-do-i-download-a-file-over-http-using-python
        #

        try:
            u = urllib2.urlopen(url)
        except urllib2.HTTPError, e:
            print 'Error downloading %s: %s' % (relativePath, e.code)
        except urllib2.URLError, e:
            print 'Error reaching %s: %s' % (relativePath, e.reason)
        else:
            f = open(outputFilePath, 'wb')
            meta = u.info()
            fileSize = int(meta.getheaders("Content-Length")[0])
            print "\t%s (%s bytes)" % (relativePath, fileSize)

            fileSizeDownloaded = 0
            blockSize = 8192
            while True:
                buffer = u.read(blockSize)
                if not buffer:
                    break

                fileSizeDownloaded += len(buffer)
                f.write(buffer)
                status = r"%10d  [%3.2f%%]" % (fileSizeDownloaded, fileSizeDownloaded * 100. / fileSize)
                status = status + chr(8) * (len(status) + 1)
                print status,

            f.close()


#
# Main
#

print '\nExamining local images and links in static content…\n'

regularPostLinkPattern = u'http://' + domain.replace('.', '\\.') + '/\d{1,4}'

regularPostLinkRegex = re.compile(regularPostLinkPattern)

files = os.listdir('static')

# Get links from the WordPress export files
for postFile in files:
    postFileHandle = file('static/' + postFile)
    content = unicode(postFileHandle.read(), 'utf_8')
    soup = BeautifulSoup(content, 'html5lib')

    linksInPost = soup.findAll('a')
    for linkSoup in linksInPost:

        try:
            link = unicode(linkSoup['href']).lower()
        except Exception:
            print u'\tError with link in static post in file ' + postFile + ': ' + unicode(linkSoup)

        if link.startswith(u'http://' + domain) or link.startswith(u'http://www.' + domain) or (not link.startswith(u'http')):

            if not regularPostLinkRegex.match(link):

                for validDownloadFolder in validDownloadFolders:
                    if link.startswith(validDownloadFolder) or link.startswith('/' + validDownloadFolder) or link.startswith(u'http://' + domain + '/' + validDownloadFolder):
                        link = makeRelativeLink(link)
                        links.add(link)

                # Catch‐all
                allLinks.add(link)

    imagesInPost = soup.findAll('img')
    for linkSoup in imagesInPost:
        try:
            link = unicode(linkSoup['src']).lower()
        except Exception:
            print u'\tError with image source in static post in file ' + postFile + ': ' + unicode(linkSoup)
        if link.startswith(u'http://' + domain) or link.startswith(u'http://www.' + domain) or (not link.startswith(u'http')):
                link = makeRelativeLink(link)
                images.add(link)


numImages = len(images)
numLinks = len(links)

print '\nFound %d local images and %d links to local assets in static files.\n' % (numImages, numLinks)


#
# Create the folders and download the files
#
if dryRun:
    print '\nDry run… no actual downloads will take place.\n'

print 'Downloading images…\n'

for image in images:
     download(image)

print '\nDownloading other local links…\n'

for link in links:
    download(link)
