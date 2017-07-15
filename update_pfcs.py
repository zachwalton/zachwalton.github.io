#!/usr/bin/env python

import datetime
import os
import string
import sys
import time

frontmatter_template = """---
layout: ddr
title: PFC {next_pfc}
date:   {post_time_str}
categories: ddr
---
"""

pfc_markdown_template = """
#### **#{next_pfc}** {song}<span class="pull-right">{{ page.date | date_to_long_string }}</span>
![](/{image_dir}/{next_pfc}_{song}.jpg)
"""

def process_songs(songs_file, image_dir, posts_dir):
    post_time = datetime.datetime.now()

    with open(songs_file) as fh:
        for song in fh.readlines():
            song = song.strip('\n')
            print "processing %s" % song

            next_pfc, image_name = wait_for_image(image_dir)
            os.rename("%s/%s" % (image_dir, image_name), "%s/%s_%s.jpg" % (image_dir, next_pfc, song))
            print "processed image %s/%s_%s.jpg" % (image_dir, next_pfc, song)

            post_time += datetime.timedelta(0, 1)
            post_time_str = post_time.strftime("%Y-%m-%d %H:%M:%S")
            markdown = frontmatter_template.format(**locals()) + pfc_markdown_template.format(**locals())

            with open("%s/%s-pfc-#%d.md" % (posts_dir, post_time_str.split(" ")[0], next_pfc), 'w+') as fh:
                fh.write(markdown)

            print "processed markdown file %s/%s-pfc-#%d.md" % (posts_dir, post_time_str.split(" ")[0], next_pfc)

def wait_for_image(image_dir):
    next_pfc = int(sorted([ s.split('_')[0] for s in os.listdir(image_dir) if s[0] in string.digits ], key=int)[-1]) + 1
    while 1:
        try:
            return next_pfc, sorted([ f for f in os.listdir(image_dir) if f.startswith("IMG") ])[0]
        except IndexError:
            print "Waiting for IMGXXX.JPG to show up in %s..." % image_dir
            time.sleep(1)

def main():
    try:
        songs_file, image_dir, posts_dir = sys.argv[1:]
    except ValueError:
        print "Usage: %s path/to/song-list.txt path/to/images _posts/ddr" % sys.argv[0]
        sys.exit(1)

    process_songs(songs_file, image_dir, posts_dir)

if __name__ == "__main__":
    sys.exit(main())
