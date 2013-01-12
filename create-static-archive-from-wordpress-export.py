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
#
#   26      publishedPosts[23]      Paragraphs not being created properly.
#
#   23                              Comments showing although there are no comments.
#   2760    publishedPosts[1410]    HTML/pre parsing not correct.

import argparse
import os
import parse_wordpress_export
import StringIO
import re
from time_since import timesince
from datetime import datetime

def massagePreformattedText(line):
    # The crappy exported data doesn’t even escape angular brackets!
    line = line.replace('<', '&lt;')
    line = line.replace('>', '&gt;')

    # Replace tabs with two spaces to make code look neater
    line = line.replace('\t', '  ')

    return line


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

# Store the lines for the index in an array
indexYears = []

# Points to the current index year
currentIndexYear = 0

# Keep track of covered years
coveredYears=[]

# Load the post template
postTemplateFile = open('templates/post-template.html', 'r')
postTemplate = unicode(postTemplateFile.read(), 'utf_8')
postTemplateFile.close()

for post in wp.postsPublished:

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

    # Check if the is static content to substitute for this post (if so, we will )
    staticContentFilePath = 'static/%s.html' % post['id'];
    if os.path.exists(staticContentFilePath):
        staticContentFile = open(staticContentFilePath, 'r')
        staticContent = unicode(staticContentFile.read(), 'utf_8')
        post['content'] = staticContent
    else:
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
            singleLinePre = False
            if '[gist' in line:
                # Gist embed shorttag support
                # Test with post id 3950 (publishedPosts[1550])
                match = re.search('\[gist id=(\d{1,20}).*?\]', line)
                if match:
                    gistID = match.groups()[0]
                    scriptEmdedCode = '<script src="https://gist.github.com/%s.js"></script>' % gistID
                    line = line.replace(match.string[match.start():match.end()], scriptEmdedCode)
            if '<pre>' in line and '</pre>' in line:
                # Pre tag is on a single line
                # Test with post id = 2760 (postsPublished[1410])
                singleLinePre = True
                match = re.match(r'<pre>(.*?)</pre>', line)
                if match:
                    matchedGroups = match.groups()
                    preformattedText = matchedGroups[0]
                    massagedPreformattedText = massagePreformattedText(preformattedText)
                    line.replace(preformattedText, massagedPreformattedText)

            if ('</pre' in line or '[/as]' in line) and not singleLinePre:
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

            if ('<pre' in line or '[as]' in line) and not singleLinePre:
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
                if line[:12] == '<br /><br />':
                    lastLine = '<p>' + lastLine + '</p>'
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

    # Time since the post was written
    dateOfPost = datetime.strptime(post['date'], '%Y-%m-%d %H:%M:%S')
    ageOfPost = timesince(dateOfPost)

    #
    # Create and write out the post.
    #

    postTitle = post['title']
    if postTitle == None:
        postTitle = 'Untitled'
        print '\tWarning: post with id %s is missing post title.' % post['id']

    postHTML = postTemplate
    postHTML = postHTML.replace(u'{{POST_TITLE}}', postTitle)
    postHTML = postHTML.replace(u'{{POST_AGE}}', ageOfPost)
    postHTML = postHTML.replace(u'{{POST_DATE}}', post['date'].split(' ')[0])
    postHTML = postHTML.replace(u'{{POST_CONTENT}}', post['content'])
    postHTML = postHTML.replace(u'{{COMMENTS}}', commentsUL)

    #
    # Create a folder based on the ID and save the HTML in an index.html file.
    #
    postFolder = 'build/' + post['id']
    if not os.path.exists(postFolder):
        os.makedirs(postFolder)

    postFilePath = postFolder + '/index.html'
    file = open(postFilePath, 'w')
    file.write(postHTML.encode('utf8', 'replace'))
    file.close()

    #
    # Add this post to the index post list for the archive’s index.
    #

    # Check if we’ve reached a new year (and if so, create a heading for it)
    year = post['date'].split(' ')[0].split('-')[0]
    if year not in coveredYears:
        # New year
        coveredYears.append(year)

        currentIndexYear = len(indexYears)

        currentYearDictionary = {}
        currentYearDictionary['header'] = u'<h3 id="%s">%s<a href="#year-nav"><span class="return-link">↩</span></a></h3>' % (year, year)
        currentYearDictionary['posts'] = []

        indexYears.append(currentYearDictionary)

    indexListItem = u'\t\t\t\t<li><a href="/%s/">%s</a>' % (post['id'], postTitle)

    # Post date may be None, check for this.
    if post['date'] != None:
        indexListItem += u'<small>&#8202;—&#8202;' + post['date'].split(' ')[0] + '</small>'
    else:
        print '\tWarning: post with id %s is missing post date.' % post['id']

    indexListItem += u'</li>\n'

    indexYears[currentIndexYear]['posts'].append(indexListItem)


#
# Create and write out the index file
#

print '\nCreating the index…\n'

# Reverse the years and the posts within the years
# to create the index in reverse chronological order.

indexPostListHTML = '<div id="year-nav">Years: <small>|</small> '

# Add links to the year anchors

coveredYears.reverse()
for year in coveredYears:
    indexPostListHTML += '<a href="#%s">%s</a> <small>|</small> ' % (year, year)

indexPostListHTML += '</div>\n'

indexYears.reverse()
for indexYear in indexYears:
    indexPostListHTML += indexYear['header'] + '\n'
    indexPostListHTML += '<ul>\n'
    indexYear['posts'].reverse()
    reversedPostsForYear = indexYear['posts']
    for post in reversedPostsForYear:
        indexPostListHTML += '\t' + post
    indexPostListHTML += '</ul>\n'

# Load the index template.
indexTemplateFile = open('templates/index-template.html', 'r')
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

