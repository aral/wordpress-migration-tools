# -*- coding: utf-8 -*-

#
# Parse the Wordpress export file (WXF) and create
# easy to use data structures.
#
#   posts               (Array) All posts.
#
#   postsPublished      (Array) Posts with status set to 'publish'
#   postsDraft          (Array) Posts with status set to 'draft'
#   postsPrivate        (Array) Posts with status set to 'private'
#
#   pages               (Array) All pages.
#   attachments         (Array) All attachments.
#
#   Posts, pages, and attachments are all item dictionaries.
#
#
#   Item dictionary keys
#   --------------------
#
#   e.g., post = postsPublished[0]      <-- Returns an item dictionary.
#         postTitle = post['title']
#
#   All values are strings unless otherwise stated.
#
#   title               Title of item
#
#   link                Link to the item
#
#   pubDate             The publication date of the item in RFC 822/RFC 1123 format
#                       (e.g., Thu, 04 Dec 2003 03:54:19 +0000)
#
#   creator             The author of the item
#
#   description         Item description (may be None)
#
#   content             Content of the item (e.g., main content of the post)
#
#   id                  ID of the item
#
#   date                GMT date of the item in extended ISO 8601 format (sans time designator)
#                       (e.g., 2005-08-09 21:27:31)
#   name                Name of the item (for posts this is the slug)
#
#   status              Status of the post. One of 'publish', 'draft', or 'private'
#
#   type                Type of the item. One of 'post', 'page', or 'attachment'
#
#   category            (Dictionary; may be None.)
#
#                           'slug':   category slug
#                           'name':   category display name
#
#   comments            (Array) of Comment dictionaries.
#
#
#   Comment dictionary keys:
#   ------------------------
#
#   TODO

import xml.etree.ElementTree as ET
import cgi

#
# Options
# TODO: Make these into parameters.
#
verbose = False


channel = None
itemElements = None

#
# The global list of parsed items, organised by post type and status.
#
# e.g., items['post']['publish'] = All published posts
#       items['page']['draft'] = All draft pages
#
items = []

itemTypes = []

#
# Item namespaces (with alias names as set by ElementTree)
#
dc = "http://purl.org/dc/elements/1.1/"
ns1 = "http://purl.org/rss/1.0/modules/content/"
ns2 = "http://wordpress.org/export/1.2/excerpt/"
ns3 = "http://wordpress.org/export/1.2/"

#
# Item collections by type
#
posts = []
pages = []
attachments = []
unknown = []

#
# Posts by status type
#
postsPublished = []
postsDraft = []
postsPrivate = []

#
# Links in content
#
links = []
linksToImages = []
linksToDownloads = []
linksToUploadedMedia = []


#
# Tag shortcuts for easy use when searching
#

# Post
dcCreator = '{%s}creator' % dc
ns1Encoded = '{%s}encoded' % ns1
ns3PostID = '{%s}post_id' % ns3
ns3PostDateGMT = '{%s}post_date_gmt' % ns3
ns3PostName = '{%s}post_name' % ns3
ns3Status = '{%s}status' % ns3
ns3PostType = '{%s}post_type' % ns3
ns3Comment = '{%s}comment' % ns3

# Comment
ns3CommentID = '{%s}comment_id' % ns3
ns3CommentAuthor = '{%s}comment_author' % ns3
ns3CommentAuthorEmail = '{%s}comment_author_email' % ns3
ns3CommentAuthorURL = '{%s}comment_author_url' % ns3
ns3CommentAuthorIP = '{%s}comment_author_ip' % ns3
ns3CommentDateGMT = '{%s}comment_date_gmt' % ns3
ns3CommentContent = '{%s}comment_content' % ns3
ns3CommentApproved = '{%s}comment_approved' % ns3
ns3CommentType = '{%s}comment_type' % ns3
ns3CommentParent = '{%s}comment_parent' % ns3

# Attachments
ns3AttachmentURL = '{%s}attachment_url' % ns3

postStatusTypes = {}
postCounts = {'draft': 0, 'published': 0}

# numWords = 0


def publishedPostIndexForPostID(postID):
    for post in postsPublished:
        if post['id'] == postID:
            publishedPostIndex = postsPublished.index(post)
            return publishedPostIndex
    return None


def publishedPostWithID(postID):
    publishedPostIndex = publishedPostIndexForPostID(postID)
    return postsPublished[publishedPostIndex]


def parse(fileToParse):
    # global numWords

    print 'Parsing the Wordpress export…'

    wordpressExportTree = ET.parse(fileToParse)
    root = wordpressExportTree.getroot()

    print 'Done.\n'

    channel = root.find('channel')
    itemElements = channel.findall('item')

    # Separate the posts by type for further processing

    for itemElement in itemElements:
        itemType = itemElement.find(ns3PostType)

        if itemType.text == 'post':
            posts.append(itemElement)
        elif itemType.text == 'page':
            pages.append(itemElement)
        elif itemType.text == 'attachment':
            attachments.append(itemElement)
        else:
            unknown.append(itemElement)

    print 'There are %d posts, %d pages, and %d attachments.' % (len(posts), len(pages), len(attachments))

    if len(unknown) != 0:
        print 'Warning: there are %d items with an unknown post type.'

    # Parse the post
    for postElement in posts:

        post = {}

        post['title'] = postElement.find('title').text

        if post['title'] == None:
            post['title'] = 'Untitled'

        post['title'] = cgi.escape(post['title'])

        post['link'] = postElement.find('link').text
        post['pubDate'] = postElement.find('pubDate').text
        post['creator'] = postElement.find(dcCreator).text
        post['description'] = postElement.find('description').text
        post['content'] = postElement.find(ns1Encoded).text
        post['id'] = postElement.find(ns3PostID).text
        post['date'] = postElement.find(ns3PostDateGMT).text
        post['name'] = postElement.find(ns3PostName).text
        post['status'] = postElement.find(ns3Status).text
        post['type'] = postElement.find(ns3PostType).text

        categoryElement = postElement.find('category')

        if categoryElement != None:
            post['category'] = {}
            post['category']['slug'] = categoryElement.get('nicename')
            post['category']['name'] = categoryElement.text
        else:
            post['category'] = None

        # Comments
        commentElements = postElement.findall(ns3Comment)

        comments = []

        for commentElement in commentElements:
            comment = {}

            comment['id'] = commentElement.find(ns3CommentID).text
            comment['author'] = commentElement.find(ns3CommentAuthor).text
            comment['authorEmail'] = commentElement.find(ns3CommentAuthorEmail).text
            comment['authorURL'] = commentElement.find(ns3CommentAuthorURL).text
            # Author IP may be None. TODO: Handle this.
            # comment['authorIP'] = commentElement.find(ns3CommentAuthorIP).text
            comment['date'] = commentElement.find(ns3CommentDateGMT).text
            comment['content'] = commentElement.find(ns3CommentContent).text

            words = comment['content'].split(' ')
            # numWords += len(words)

            comment['approved'] = commentElement.find(ns3CommentApproved).text
            comment['type'] = commentElement.find(ns3CommentType).text
            comment['parent'] = commentElement.find(ns3CommentType).text

            comments.append(comment)

        post['comments'] = comments

        # To see what status types we have (good for the future and for other people
        # who might use this script if new ones crop up)…
        postStatusTypes[post['status']] = True

        # …and group by the status types that we do know:
        if post['status'] == 'publish':
            postsPublished.append(post)
        elif post['status'] == 'draft':
            postsDraft.append(post)
        elif post['status'] == 'private':
            postsPrivate.append(post)

    # Info - verbose: post status types - might come in handy for other sites.
    if (verbose):
        postStatusTypesInfo = 'Post status types: '
        for postStatusType in postStatusTypes.keys():
            postStatusTypesInfo += postStatusType + ', '
        postStatusTypesInfo = postStatusTypesInfo[:-2] + '.'
        print postStatusTypesInfo

    # Info: number of posts in each status type
    print 'There are %d published, %d draft, and %d private posts.' % (len(postsPublished), len(postsDraft), len(postsPrivate))
    # print 'Total words in posts: %d' % numWords