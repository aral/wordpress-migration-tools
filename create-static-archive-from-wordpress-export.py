# -*- coding: utf-8 -*-

#
# This is the script that actually generates my archive. I intend to make it a bit
# more generic in the future but right now it is mostly hard‐coded for my own needs.
#
# Content tests:
#
#   1269                            <pre> tags, <p> wrapping
#   2                               <br><br> tag stripping
#   1951    publishedPosts[1000]    Extra space at the top of <pre>, lack of <p> after pre
#   880                             [as]…[/as] short‐codes to <pre>
#   1030    publishedPosts[838]     <pre> with multiple \n’s that can get erroneously
#                                   stripped out by code to strip out first \n <pre>s

import argparse
import os
import parse_wordpress_export
import StringIO
from time_since import timesince
from datetime import datetime

# Shorthand reference to the namespace.
wp = parse_wordpress_export

parser = argparse.ArgumentParser(
    description='Creates a static archive from a wordpress export file.',
    epilog='Made with love by Aral Balkan (http://aralbalkan.com)')

parser.add_argument('wordpressExportFile')
parser.add_argument('--verbose')
args = parser.parse_args()

print '\nCreate static archive from WordPress export file:' \
    '\n➤ %s\n' % args.wordpressExportFile


# Generate a static pages

wp.parse()

print '\nCreating the posts…\n'

indexPostListHTML = ''

# post = wp.postsPublished[0]

counter = 0

for post in wp.postsPublished:

    # Limit to three for initial testing.
    # if counter == 3:
    #     break
    # counter += 1

    #
    # Write out comments for the post.
    #
    commentsUL = u''

    # Only create comments section if there are comments.
    if len(post['comments']) > 0:
        commentsUL = u"""
            <section id="comments">
            <h3>Comments</h3>
            <ul>
        """

        for comment in post['comments']:
            # Only include approved comments.
            if comment['approved'] == '1':
                li = u'<li>'
                li += comment['content']

                commentAuthor = 'Anonymous'
                if comment['author'] != None:
                    commentAuthor = comment['author']
                else:
                    print '\tInfo: Unknown author in comment on post with id: %s.' % post['id']

                # commentDate = 'an unknown date'
                # if comment['date'] != None:
                #     commentDate = comment['date']
                # else:
                #     print 'Unknown date in comment on post with id: ' + post['id']

                li += u'\n<p class="byline">by ' + commentAuthor + u' on ' + comment['date'] + u'</p>'
                li += u'</li>'
                commentsUL += '\n\t\t' + li
            # else:
            #     print 'Skipping unapproved comment.'

        commentsUL += '\n</ul>\n</section>\n'

    #
    # Massage the post contents. Apparently, at various times in my
    # blogging career (yeah, right), WordPress alternated between using
    # <br><br> (*shudder*) and nothing at all between paragraphs. Look at
    # how I place the blame entirely with WordPress. I’m sure I had nothing
    # to do with it whatsoever. :)
    #

    # * Remove any occurances of <br><br>. Seriously, there’s never a need for that.

    # * Read through the content line by line and wrap <p> tags around
    #   all the paragraphs. (Reading line by line makes it easier to avoid
    #   adding <p> tags within <pre>formatted text, etc.)

    massagedContent = '<p>'
    lastLine = ''
    inPreformattedText = False
    buffer = StringIO.StringIO(post['content'])
    line = buffer.readline()
    while line:
        if '</pre' in line or '[/as]' in line:
            inPreformattedText = False

            if '[/as]' in line:
                # Replace the [/as] shortcode with a </pre>
                line = line.replace('[/as]', '</pre>')

            # Debug: Using post 1269 to test the escaping of angular tags in
            # ====== preformatted text.
            # if post['id'] == '1269':
            #     print 'Exiting preformatted text in line: ' + line
        if inPreformattedText:
            # The crappy exported data doesn’t even escape angular brackets!
            line = line.replace('<', '&lt;')
            line = line.replace('>', '&gt;')

            # Replace tabs with two spaces to make code look neater
            line = line.replace('\t', '  ')

        if '<pre' in line or '[as]' in line:
            inPreformattedText = True

            if '[as]' in line:
                # Replace the [as] shortcode with a <pre>
                # Test with post 880.
                line = line.replace('[as]', '<pre>')

            # If the preformatted text starts with an empty line,
            # remove it so that there isn’t too much whitespace at the top.
            # Test with post 1269 (postsPublished[1000])
            # and post 1030 (postsPublished[838])
            if line[-2:] == '>\n':
                line = line[:-1]

            # Debug: Using post 1269 to test the escaping of angular tags in
            # ====== preformatted text.
            # if post['id'] == '1269':
            #     print 'Entering preformatted text in line: ' + line

        if not inPreformattedText:
            if line == '<br />\n':
                # Remove  <br> tag and wrap the last line in a paragraph
                lastLine = '<p>' + lastLine.replace('<br />\n', '') + '</p>'
                # And remove the current <br> tag too.
                line = ''
            if line == '\n':
                if len(lastLine) > 0 and lastLine[-1] == '\n':
                    lastLine += '</p><p>'
        massagedContent += lastLine
        lastLine = line
        line = buffer.readline()

    massagedContent += lastLine + '</p>'

    # Remove any single <br> tags that we might have missed.
    massagedContent = massagedContent.replace('<br />', '')

    post['content'] = massagedContent

    #
    # Write out the post.
    #

    # Time since the post was written
    dateOfPost = datetime.strptime(post['date'], '%Y-%m-%d %H:%M:%S')
    ageOfPost = timesince(dateOfPost)

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
            <title>Aral Balkan: Historical Archive&#8202;—&#8202;%s</title>
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
                <strong>Historical content:</strong> I wrote this article over %s on %s. You are viewing an archived post from my old WordPress blog. The archive contains over 1,500 articles written over a ten year period. The formatting and contents of the posts may not display perfectly.
            </section>

            <div role="content">

                <h2>%s</h2>
                <section id="post">
                %s
                </section>
                <!-- Comments -->
                %s
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
    """ % (post['title'], post['title'], ageOfPost, post['date'].split(' ')[0], post['title'], post['content'], commentsUL, post['title'])

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

    #
    # Add this post to the index post list for the archive’s index.
    #
    indexListItem = u'\t\t\t\t<li><a href="/' + post['id'] + u'/">'

    if post['title'] != None:
        indexListItem += post['title']
    else:
        indexListItem += 'Untitled'
        print '\tWarning: post with id %s is missing post title.' % post['id']

    indexListItem += u'</a>'

    # Post date may be None, check for this.
    if post['date'] != None:
        indexListItem += u'&#8202;—&#8202;' + post['date']
    else:
        print '\tWarning: post with id %s is missing post date.' % post['id']

    indexListItem += u'</li>\n'

    indexPostListHTML += indexListItem

#
# Create and write out the index file
#

print '\nCreating the index…\n'

# Load the index template.
indexTemplateFile = open('index-template.html', 'r')
indexTemplate = unicode(indexTemplateFile.read(), 'utf_8')
indexTemplateFile.close()

archiveIndexHTML = indexTemplate.replace(u'{{POST_LIST}}', indexPostListHTML)

archiveFolder = 'build/archive'
if not os.path.exists(archiveFolder):
    os.makedirs(archiveFolder)

archiveFilePath = archiveFolder + '/index.html'
file = open(archiveFilePath, 'w')
file.write(archiveIndexHTML.encode('utf8', 'replace'))
file.close()

print 'Ready.'

