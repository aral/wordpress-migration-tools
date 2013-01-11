# -*- coding: utf-8 -*-

#
# Used to compile lists of links to local media
# which you might want to download and move to your static archive.
# This is useful when weeding out which media files to keep. (e.g.,
# maybe you had files uploaded for temporary use like I did.)
#

import parse_wordpress_export
from StringIO import StringIO

domain = 'aralbalkan.com'
imagesFolder = '/images'
downloadsFolder = '/downloads'
uploadedMediaFolder = '/wp-content/uploads'

# Shorthand reference to the namespace.
wp = parse_wordpress_export

wp.parse()

# Get links from the WordPress export files
for post in wp.posts:
	content = post['content']


# Get links from any static content files
# TODO
