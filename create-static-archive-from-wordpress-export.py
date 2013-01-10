# -*- coding: utf-8 -*-
import argparse
import os
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


#
# Write out comments for the post.
#

commentsUL = u"""
    <!-- Comments -->
    <ul>
"""

for comment in post['comments']:
    # Only include approved comments.
    if comment['approved'] == '1':
        li = u'<li>';
        li += comment['content']
        li += u' <em>by ' + comment['author'] + u' on ' + comment['date'] + u'</em>'
        li += u'</li>'
        commentsUL += '\n\t\t' + li
    else:
        print 'Skipping unapproved comment.'

#
# Write out the post.
#

html = u"""
<html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width">
        <link rel="icon" href="/favicon.ico">
        <link rel="license" href="http://creativecommons.org/licenses/by-nc-sa/3.0/">
        <link rel="stylesheet" href="/css/reset.css">
        <link rel="stylesheet" href="/css/stylus/styles.css">
        <link rel="stylesheet" href="/css/stylus/archive/styles.css">
        <title>Aral Balkan: Historic Archive&#8202;—&#8202;%s</title>
    </head>
    <body>
        <header>
            <h1>Aral Balkan</h1>
        </header>

        <nav>
            <ul>
                <li><a href="/">Home</a></li>
                <li><a href="/archive">Archive</a></li>
                <li><span class="current-page">%s</span></li>
            </ul>
        </nav>

        <section id="archiveDisclaimer">
            <p><strong>Historic content:</strong> This article was written on %s. You are viewing an archived post written from the old WordPress blog I had at this site. The archive has over 1,500 articles that I wrote over a ten year period. The formatting and contents of the posts may not display perfectly.</p>
        </section>

        <div role="content">

            <h2>%s</h2>
            <section id="post">
            %s
            </section>
            <section id="comments">
            %s
            </section>
        </div>
        <footer>
            <section>
                <h2>Contact</h2>
                <ul>
                    <li>Twitter: <a rel="me" href="http://twitter.com/aral">@aral</a></li>
                    <li>Email: <a href="mailto:aral@aralbalkan.com">aral@aralbalkan.com</a></li>
                </ul>
            </section>

            <section id="copyright">
                <nav>
                <ul>
                    <li><a href="/">Home</a></li>
                    <li><a href="/archive">Archive</a></li>
                    <li><span class="current-page">%s</span></li>
                </ul>
            </nav>
                    <small>Copyright © 2012–2013 Aral Balkan. <a href="http://www.flickr.com/photos/cvonposer/6401515437" title="Aral Balkan">Photo</a> courtesy of <a href="http://www.flickr.com/photos/cvonposer/" title="Christina von Poser Photostream">Christina von Poser</a></small>
            </section>
        </footer>

        <script type="text/javascript">
            //
            // Hack: Safari has a rendering bug and doesn’t render -webkit-font-smoothing
            // ===== correctly. So, it’s set to subpixel-antialiased by default and I
            //       turn it off for Chrome as a progressive enhancement. Firefox doesn’t
            //       support any font smoothing options but Firefox users probably don’t
            //       have much aesthetic taste to begin with so I doubt they’ll notice.
            //
            if (navigator.userAgent.indexOf("Chrome/") != -1) {
                var timeTags = document.getElementsByTagName("time");
                  for (var i=0; i<timeTags.length; i++) {
                    timeTags[i].style.webkitFontSmoothing = 'none';
                }
            }

            // Hack: Firefox is an ass.
            if (navigator.userAgent.indexOf("Firefox/") != -1) {
                var timeTags = document.getElementsByTagName("time");
                  for (var i=0; i<timeTags.length; i++) {
                    timeTags[i].style.paddingTop = '0.125rem';
                }
            }

            // Gaug.es analytics.
            var _gauges = _gauges || [];
            (function() {
                var t   = document.createElement('script');
                t.type  = 'text/javascript';
                t.async = true;
                t.id    = 'gauges-tracker';
                t.setAttribute('data-site-id', '4f0f72dbcb25bc4e6d000009');
                t.src = '//secure.gaug.es/track.js';
                var s = document.getElementsByTagName('script')[0];
                s.parentNode.insertBefore(t, s);
            })();

        </script>
    </body>
</html>
""" % (post['title'], post['title'], post['date'], post['title'], post['content'], commentsUL, post['title'])

# print html

#
# Create a folder based on the ID and save the HTML in an index.html file.
#
postFolder = 'build/' + post['id']
if not os.path.exists(postFolder):
    os.makedirs(postFolder)

postFilePath = postFolder + '/index.html'
file = open(postFilePath, 'w')
file.write(html.encode('utf8', 'replace'))
file.close()









