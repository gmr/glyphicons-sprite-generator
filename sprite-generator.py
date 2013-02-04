#!/usr/bin/env python
"""
GLYPHICONS Sprite Generator for Bootstrap

The GLYPHICONS Sprite Generator allows you to change the size and colors of the
Bootstap icons using the Free or Pro versions of GLYPHICONS. When using the Pro
files, all the extra icons will be available to your Bootstrap project.

New CSS and PNG sprites are generated that can override Bootstrap's
default icon before or mixed into a Bootstrap LESS project.

Dependencies
------------
The only required non-standard-library package that is needed is the Python
Imaging Library. To install this simply run "easy_install pil" or
"pip install pil"

How to use sprite-generator.py
------------------------------

 1. Download the type of GLYPICONS distribution and extract the zip file
 2. Copy sprite-generator.py into the extracted glypicons_free or glyphicons pro folder
 3. Check to see if you want to change any of the constants at the top of the
    script (size, preview background, etc)
 4. Run sprite-generator.py, if everything worked property, sprite-generator.py will
    have generated the following files in the "sprites" directory:

    - glyphicons.css         CSS Overrides
    - glyphicons.html        Preview HTML
    - glyphicons.png         Black Icons
    - glyphicons-white.png   White (or colorized) icons

 5. Open sprites/glyphicons.html in your browser (if you're on a Mac, it will try and do so itself)

How to use in your Bootstrap project
------------------------------------
1. Copy the glyphicons.png and glyphicons-white.png to the project img directory.
2. Include the glyphicons.css file *after* the bootstrap CSS files or include in
   your bootstrap.less files after the sprites.less entry.
3. Edit glyphicons.css, fixing the paths to the image files in the background-image directives.

"""
# If you want to change the color of the icon-white sprite, change this (R,G,B) value
WHITE = (255, 255, 255)

# Change this to see white against a different preview background
PREVIEW_BACKGROUND = '444'

# Icon Size
ICON_SIZE = 14,14

# Only use 2x (For use with PRO, script *should* detect this with default directory names)
PRO = False

# You shouldn't have to change anything below here for normal usage

import glob
import os
import re
import subprocess
import sys

try:
    from PIL import Image
except ImportError:
    print "Error: Python Imaging Library (http://www.pythonware.com/library/pil) not found"
    print 'Please install before running. You most likely can install by running easy_install pil" or "pip install pil"'
    sys.exit(-1)

COLUMNS = 50
CELL_SIZE = ICON_SIZE[0] + 10, ICON_SIZE[1] + 10
CELL_OFFSET = 5

ICON_NAME = re.compile(r'glyphicons/png/glyphicons_\d{3}_([\w_@\+\-]+)\.png')

SPRITE_CSS = 'sprites/glyphicons.css'
SPRITE_FILE = 'sprites/glyphicons.png'
SPRITE_WHITE_FILE = 'sprites/glyphicons-white.png'
SPRITE_HTML = 'sprites/glyphicons.html'

CSS_TEMPLATE = """[class^="icon-"],
[class*=" icon-"] {
  display: inline-block;
  width: %spx;
  height: %spx;
  margin-top: 1px;
  *margin-right: .3em;
  line-height: %spx;
  vertical-align: text-top;
  background-image: url("glyphicons.png");
  background-position: %spx %spx;
  background-repeat: no-repeat;
}

/* White icons with optional class, or on hover/active states of certain elements */

.icon-white,
.nav-pills > .active > a > [class^="icon-"],
.nav-pills > .active > a > [class*=" icon-"],
.nav-list > .active > a > [class^="icon-"],
.nav-list > .active > a > [class*=" icon-"],
.navbar-inverse .nav > .active > a > [class^="icon-"],
.navbar-inverse .nav > .active > a > [class*=" icon-"],
.dropdown-menu > li > a:hover > [class^="icon-"],
.dropdown-menu > li > a:hover > [class*=" icon-"],
.dropdown-menu > .active > a > [class^="icon-"],
.dropdown-menu > .active > a > [class*=" icon-"],
.dropdown-submenu:hover > a > [class^="icon-"],
.dropdown-submenu:hover > a > [class*=" icon-"] {
  background-image: url("glyphicons-white.png");
}

""" % (ICON_SIZE[0], ICON_SIZE[1], ICON_SIZE[1], ICON_SIZE[0], ICON_SIZE[1])

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>GLYPHICONS Sprite Generator</title>
    <link href="http://twitter.github.com/bootstrap/assets/css/bootstrap.css" rel="stylesheet">
    <link href="glyphicons.css" rel="stylesheet">
  </head>
  <body>
    <div class="container">
      <p class="lead" style="margin-top: 1em;">
        The <a href="http://glyphicons.com/">GLYPHICONS</a> Sprite Generator for <a href="https://twitter.github.com/bootstrap">Bootstrap</a>.
      </p>
      <hr>
      <p>Here are the results of the generated sprite:</p>
      <table class="table" style="width: 350px; margin-left: 25px;">
        <thead>
          <th style="width: 200px;">Class</th>
          <th style="text-align: center; width: 75px;">Preview</th>
          <th style="text-align: center; width: 75px;">White Preview</th>
        </thead>
        <tbody>
          %s
        </tbody>
      </table>
      <hr>
      <p>
        <strong>GLYPHICONS FREE</strong> are released under the Creative Commons Attribution 3.0 Unported (CC BY 3.0). The GLYPHICONS FREE can be used both commercially and for personal use, but you must always add a link to glyphicons.com in a prominent place (e.g. the footer of a website), include the CC-BY license and the reference to glyphicons.com on every page using GLYPHICONS.
      </p>
      <footer><p>Sprite Generator created by <a href="https://github.com/gmr">Gavin M. Roy</a> (<a href="https://twitter.com/crad">@Crad</a>)</p></footer>
    </div>
  </body>
</html>"""

TR_TEMPLATE = '        <tr><td>%s</td><td style="text-align: center;"><i class="%s"></i></td><td style="background-color: #%s; text-align: center;"><i class="%s icon-white"></i></td></tr>'


def new_icon(filename, white=False):
    icon_in = Image.open(filename)
    if white:
        pixel_data = icon_in.load()
        size = icon_in.size
        for y in xrange(size[1]):
            for x in xrange(size[0]):
                if len(pixel_data[x, y]) == 4:
                    if pixel_data[x, y][3] > 0:
                        alpha = float(float(pixel_data[x, y][3]) / 255)
                        if pixel_data[x, y][0] < WHITE[0]:
                            pixel_data[x, y] = (WHITE[0], WHITE[1], WHITE[2],
                                                pixel_data[x, y][3])
                else:
                    pixel_data[x, y] = WHITE


    width, height = icon_in.size
    if width > height:
        new = Image.new('RGBA', (width, width), (255, 255, 255, 0))
        new.paste(icon_in, (0, int((width-height)/2)))
        new.thumbnail(ICON_SIZE, Image.ANTIALIAS)
        return new
    elif height > width:
        new = Image.new('RGBA', (height, height), (255, 255, 255, 0))
        new.paste(icon_in, (int((height-width)/2), 0))
        new.thumbnail(ICON_SIZE, Image.ANTIALIAS)
        return new
    icon_in.thumbnail(ICON_SIZE, Image.ANTIALIAS)
    return icon_in

def new_image(file_count):
    rows = int(file_count / COLUMNS) + 1
    return Image.new('RGBA', (CELL_SIZE[1] * COLUMNS, CELL_SIZE[1] * rows), (255, 255, 255, 0))

def main():
    global PRO

    # Try and guess if this is pro or free
    directory = os.path.realpath(__file__).split('/')[-2]
    if directory[-3:] == 'pro' and not PRO:
        print "GLYPHICONS PRO detected, using 2x icons for coloring and sizing"
        PRO = True

    files = glob.glob("glyphicons/png/*.png")
    if not files:
        print "ERROR: Did not find any PNG files, are you sure youre in glyphicons_free/glyphicons directory?"
        sys.exit(-1)

    # Count the number of files that will be used
    file_count = 0
    for filename in files:
        if PRO and '@2x' not in filename:
            continue
        file_count += 1

    # Create the new sprite images in memory
    sprite, sprite_white = new_image(file_count), new_image(file_count)
    icons = dict()
    row, column = 0, 0

    # Iterate through all of the files in the png directory making the sprite
    for filename in files:

        # For use with GLYPHICONS PRO for better quality icons
        if PRO and '@2x' not in filename:
            continue

        # Get the name of the icon from the file
        match = ICON_NAME.findall(filename)

        # Create the class name
        name = 'icon-%s' % match[0].replace('_', '-').replace('@2x', '')

        # Position in the sprite
        x = (column * CELL_SIZE[0]) + 5
        y = (row * CELL_SIZE[1]) + 5

        # Add this icon to the sprites
        sprite.paste(new_icon(filename), (x, y))
        sprite_white.paste(new_icon(filename, True), (x, y))

        # Create the CSS line
        icons[name] = ".%s { background-position: -%ipx -%ipx; }" % (name, (column * CELL_SIZE[0]) + 5, (row * CELL_SIZE[1]) + 5)

        # Keep track of where we are in the sprite
        column += 1
        if column == COLUMNS - 1:
            row += 1
            column = 0

    # Make the sprite directory
    if not os.path.exists('sprites'):
        os.mkdir('sprites')

    # Safe the sprite files
    sprite.save(SPRITE_FILE)
    sprite_white.save(SPRITE_WHITE_FILE)

    # Write out the CSS file and make the rows for the HTML file
    glyphicons = list()
    with open(SPRITE_CSS, "w") as handle:
        handle.write(CSS_TEMPLATE)
        for key in sorted(icons.keys()):
            handle.write('%s\n' % icons[key])
            glyphicons.append(TR_TEMPLATE % (key, key, PREVIEW_BACKGROUND, key))

    # Write out the HTML file
    with open(SPRITE_HTML, "w") as handle:
        tr = '\n'.join(glyphicons)
        handle.write(HTML_TEMPLATE % (tr))

    print 'Generation complete, files are in the sprites directory'

    # Open the HTML file for preview if on a mac
    if sys.platform == 'darwin':
        print 'Opening browser to preview %s' % SPRITE_HTML
        subprocess.call(['/usr/bin/open', SPRITE_HTML])

if __name__ == '__main__':
    main()
