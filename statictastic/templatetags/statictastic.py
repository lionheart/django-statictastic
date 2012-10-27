import re
from hashlib import md5

from django.core.cache import cache
from django import template
from django.conf import settings
from django.contrib.staticfiles import finders, storage
from django.core.files.base import ContentFile
from lxml import etree
from lxml import html
import cssmin
import requests

register = template.Library()

@register.tag
def statictastic(parser, token):
    nodelist = parser.parse(('endstatictastic',))
    parser.delete_first_token()
    return CompressNode(nodelist)

class CompressNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        r = re.compile(r'[\n\r]')
        output = re.sub(r, '', self.nodelist.render(context)).strip()
        html_checksum = md5(output).hexdigest()

        cache_key = "statictastic:{}".format(html_checksum)
        pipelined_html = cache.get(cache_key)
        if not pipelined_html:
            input_elements = html.fragments_fromstring(output)
            output_elements = []
            compiled_css_content = ""
            for element in input_elements:
                if element.tag == "link" and 'rel' in element.attrib and element.attrib['rel'] == "stylesheet":
                    element.make_links_absolute(settings.BASE_URL)
                    response = requests.get(element.attrib['href'])
                    compiled_css_content += response.content
                elif element.tag == 'style' and 'type' in element.attrib and element.attrib['type'] == 'text/css':
                    compiled_css_content += element.text_content()
                else:
                    output_elements.append(element)

            compiled_css_content = cssmin.cssmin(compiled_css_content)
            staticstorage = storage.staticfiles_storage
            checksum = md5(compiled_css_content).hexdigest()
            filename = "bundled/css/{}.css".format(checksum)
            staticstorage.save(filename, ContentFile(compiled_css_content))
            output_elements.append(etree.Element("link", attrib={'rel': 'stylesheet', 'href': staticstorage.url(filename)}))

            pipelined_html = "".join(html.tostring(element) for element in output_elements)
            cache.set(cache_key, pipelined_html, 86400)

        return pipelined_html

