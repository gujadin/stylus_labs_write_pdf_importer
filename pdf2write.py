import base64
import os
import sys
import PyPDF2

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

pdf_path = sys.argv[1]
pdf = PyPDF2.PdfFileReader(pdf_path, "rb")
img_width = 720
n_pages = pdf.getNumPages()

page = pdf.getPage(0)
width = page.mediaBox.getWidth()
height = page.mediaBox.getHeight()
aspect_ratio = height/width
img_height = int(aspect_ratio * img_width)

os.system('mkdir -p /tmp/pdf2write')

new_page_height = 0

for page in range(n_pages):

    print(f"Processing {page}/{n_pages}", end='\r')

    os.system(f'pdftoppm {pdf_path} /tmp/pdf2write/tmp{page} -png -f {page} -singlefile')
    with open(f'/tmp/pdf2write/tmp{page}.png', 'rb') as f:
        base64_data = base64.b64encode(f.read()).decode('utf-8')

    tmp_svg = f'''<svg class="write-page" color-interpolation="linearRGB" x="10" y="{new_page_height+10}" width="{img_width}px" height="{img_height}px" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
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

with open(f'{os.path.dirname(pdf_path)}/{os.path.basename(pdf_path).split(".")[0]}.svg', 'w') as f:
    f.write(svg)

os.system(f'gzip -S z {os.path.dirname(pdf_path)}/{os.path.basename(pdf_path).split(".")[0]}.svg')