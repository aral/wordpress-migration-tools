WordPress Migration Tools
=========================

These are the scripts I wrote to migrate my Wordpress blog to a static site and create an archive of the old posts (so I don’t break the Interwebs by orphaning URLs).

You can [see the generated archive and posts](http://aralbalkan.com/archive) on my site, [aralbalkan.com](http://aralbalkan.com).

You might find this useful to refer to if you want to do the same thing.

The scripts are not entirely generic (I wrote them to scratch my own itch) although it is not difficult to modify them for your own purposes.


WordPress Export Parser
-----------------------

The bit that you will probably find most useful is the WordPress export file parser (parse_wordpress_export.py). It’s just a generic parser for the WXR (WordPress eXtended Rss) format that creates easy‐to‐use dictionaries for the posts.


Create Static Archive
---------------------

create-static-archive-from-wordpress-export.py takes the name of your WordPress export file as an argument and creates a static archive of it, with each post saved out in a separate index file in a folder with the post’s ID (this was the pretty URL scheme I was using for my blog).

If you want to use this script, you can configure its behaviour by using the following folders:

* **/templates** - index-template.html is used for the archive index and post-template.html is used for each of the posts

* **/static** - any files you put in here will be used to replace the post content in the export file. Name the files with the ID of the post you want to replace and give it a .html extension. e.g., the contents of a file called 4901.html will be used instead of the contents of post with ID 4901 when generating the static page for that post.

* **/fixes** - any files you put in here will be used to substitute content within posts as they are being generated. Put the content to search for on one line and the content to replace it with on the next line (rinse, repeat). So, for example, to replace the typo <a hrf in post with ID 2340, create a file called 2340.html in the fixes folder, put ```<a hrf``` on the first line, by itself, and ```<a href``` on the second line and the substitution will be made as your content is being generated:

        <a hrf
        <a href

* **/spam** - You can have certain comments (or all comments) for a post removed as the static site is being generated. Just create a file named with the ID of the post you want to affect (e.g., 601.html) and put the comment IDs that you want to remove in the file, each on its own line. Or, alternatively, put 'all' (without quotes) in the file to remove all comments (including the Comments section and its header).

You can see the files I used for my migration in the /templates, /static, and /fixes folders in the repository.

The Create Static Archive script isn’t very generic (e.g., doesn’t support different pretty URL types, etc.) and is probably the most hard‐coded bit to my needs but it should still be easy to customise it for your own needs.


List (& download) Local Linked Media
------------------------------------

I had accumulated lots of files on my old host and I wanted to download only those files (images, downloads, old SWFs, etc.) that were being linked or used in the posts. If you turn ```dryRun``` on, the list-linked-media.py script will list local images (in ```<img>``` tags), and local media that is linked to via the href attribute in ```<a>``` tags.

If dryRun is False, then the script will actually download the local media.


Hope this helps
---------------

When I first embarked on migrating my WordPress blog to a static site, I couldn’t find any useful code to build on. I hope this will help someone else out there. I’m sorry it’s not too generic at the moment (and I’m not sure I’ll have the time to make it so), but if you’re a hacker, you should have little trouble in customising it for your own needs.

Have fun + here’s to the #indieweb