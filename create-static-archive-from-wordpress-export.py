# -*- coding: utf-8 -*-
import argparse

import parse_wordpress_export

# Shorthand reference to the namespace.
wp = parse_wordpress_export

parser = argparse.ArgumentParser(
    description='Creates a static archive from a wordpress export file.',
    epilog='Made with love by Aral Balkan (http://aralbalkan.com)')

parser.add_argument('wordpressExportFile')
parser.add_argument('--verbose')
args = parser.parse_args()

print '\nCreating static archive from WordPress export file:' \
    '\n➤ %s\n' % args.wordpressExportFile


# Generate a static pages

wp.parse()

post = wp.postsPublished[0]

html = """
<html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width">
        <link rel="icon" href="/favicon.ico">
        <link rel="license" href="http://creativecommons.org/licenses/by-nc-sa/3.0/">
        <title>Aral Balkan: Historic Archive&#8202;—&#8202;%s</title>
    </head>
    <h1>%s</h1>
    <body>%s</body>
</html>
""" % (post['title'], post['title'], post['content'])

print html
