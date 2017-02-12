#!/usr/bin/env python

import os
import string
import sys
import time

pfc_markdown_template = """
#### **#{next_pfc}** {song}
![](/{image_dir}/{next_pfc}_{song}.jpg)
"""

def process_songs(songs_file, image_dir):
    markdown = ""
    with open(songs_file) as fh:
        for song in fh.readlines():
            song = song.strip('\n')
            print "processing %s" % song
            next_pfc, image_name = wait_for_image(image_dir)
            os.rename("%s/%s" % (image_dir, image_name), "%s/%s_%s.jpg" % (image_dir, next_pfc, song))
            print "processed #%s: %s" % (next_pfc, song)
            markdown = pfc_markdown_template.format(**locals()) + markdown

    print markdown

def wait_for_image(image_dir):
    next_pfc = int(sorted([ s.split('_')[0] for s in os.listdir(image_dir) if s[0] in string.digits ], key=int)[-1]) + 1
    while 1:
        try:
            return next_pfc, [ f for f in os.listdir(image_dir) if f.startswith("IMG") ][0]
        except IndexError:
            print "Waiting for IMGXXX.JPG to show up in %s..." % image_dir
            time.sleep(1)

def main():
    try:
        songs_file, image_dir = sys.argv[1:]
    except ValueError:
        print "Usage: %s path/to/song-list.txt path/to/images" % sys.argv[0]
        sys.exit(1)

    process_songs(songs_file, image_dir)

if __name__ == "__main__":
    sys.exit(main())
