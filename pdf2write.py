#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse, pathlib
import base64
import os
import sys
import PyPDF2

def set_args():
    parser = argparse.ArgumentParser(
        description="Generate a Write document from a PDF",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('file', type=pathlib.Path)
    parser.add_argument("-e", "--extend", action="store_false",
                        help="extend all pages to the right")
    return parser.parse_args()

svg = '''<svg id="write-document" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
<rect id="write-doc-background" width="100%" height="100%" fill="#808080"/>
<defs id="write-defs">
<script type="text/writeconfig">
  <int name="docFormatVersion" value="2" />
  <int name="pageColor" value="-1" />
  <int name="pageNum" value="0" />
  <int name="ruleColor" value="0" />
  <float name="marginLeft" value="0" />
  <float name="xOffset" value="-380.701752" />
  <float name="xRuling" value="0" />
  <float name="yOffset" value="1536.84216" />
  <float name="yRuling" value="0" />
</script>
</defs>
'''

args = set_args()
pdf = PyPDF2.PdfReader(args.file, "rb")
img_width = 720
n_pages = len(pdf.pages) + 1

page = pdf.pages[0]
width = page.mediabox.width
height = page.mediabox.height
aspect_ratio = height/width
img_height = int(aspect_ratio * img_width)

os.system('mkdir -p /tmp/pdf2write')

new_page_height = 0

for page in range(1, n_pages):
    print(f"Processing {page}/{n_pages}", end='\r')

    os.system("""pdftoppm "{0}" /tmp/pdf2write/tmp{1} -png -f {1} -singlefile""".format(args.file, page))
    with open(f'/tmp/pdf2write/tmp{page}.png', 'rb') as f:
        base64_data = base64.b64encode(f.read()).decode('utf-8')

    tmp_svg = f'''<svg class="write-page" color-interpolation="linearRGB" x="10" y="{new_page_height+10}" width="{img_width if args.extend else img_width*2}px" height="{img_height}px" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
  <g class="write-content write-v3" width="{img_width}" height="{img_height}" xruling="0" yruling="0" marginLeft="0" papercolor="#FFFFFF" rulecolor="#00000000">
    <g class="ruleline write-std-ruling write-scale-down" fill="none" stroke="none" stroke-width="1" shape-rendering="crispEdges" vector-effect="non-scaling-stroke">
      <rect class="pagerect" fill="#FFFFFF" stroke="none" x="0" y="0" width="{img_width}" height="{img_height}" />
    </g>
    <image x="0" y="0" width="{img_width}" height="{img_height}" xlink:href="data:image/png;base64,{base64_data}"/>
  </g>
</svg>'''
    new_page_height += (img_height+10)
    svg += tmp_svg

svg += '''</svg>'''

os.system('rm -rf /tmp/pdf2write')

folders = f'{os.path.dirname(args.file)}'
if folders == '':
    folders = '.'

final_path = str("{0}/{1}.svg".format(folders, os.path.basename(args.file).split(".")[0]))

with open(final_path, 'w') as f:
    f.write(svg)

os.system("""gzip -S z "{}" """.format(final_path))
