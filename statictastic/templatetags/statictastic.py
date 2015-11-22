"""
This module is currently under development. Do not use!
"""

import re
from hashlib import md5
from urllib.parse import urljoin

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
        linebreaks = re.compile(r'[\n\r]')
        urls = re.compile(r'url\([\'"]?([^\(\)\'"]*)[\'"]?\)')
        output = re.sub(linebreaks, '', self.nodelist.render(context)).strip()
        html_checksum = md5(output).hexdigest()

        cache_key = "statictastic:{}".format(html_checksum)
        pipelined_html = cache.get(cache_key)
        if not pipelined_html:
            input_elements = html.fragments_fromstring(output)
            output_elements = []
            compiled_css_content = ""
            for element in input_elements:
                element.make_links_absolute(settings.BASE_URL)
                if element.tag == "link" and 'rel' in element.attrib and element.attrib['rel'] == "stylesheet":
                    css_url = element.attrib['href']
                    response = requests.get(css_url)
                    content = response.content
                    for match in urls.finditer(content):
                        if match:
                            relative_url = match.group(1)
                            content = content.replace(relative_url, urljoin(css_url, relative_url))

                    compiled_css_content += content
                elif element.tag == 'style' and 'type' in element.attrib and element.attrib['type'] == 'text/css':
                    compiled_css_content += element.text_content()
                else:
                    output_elements.append(element)

            compiled_css_content = cssmin.cssmin(compiled_css_content)
            staticstorage = storage.staticfiles_storage
            checksum = md5(compiled_css_content).hexdigest()

            # TODO: This breaks relative links. Figure out a way to rewrite those appropriately.
            filename = "bundled/css/{}.css".format(checksum)
            staticstorage.save(filename, ContentFile(compiled_css_content))
            output_elements.append(etree.Element("link", attrib={'rel': 'stylesheet', 'href': staticstorage.url(filename)}))

            pipelined_html = "".join(html.tostring(element) for element in output_elements)
            cache.set(cache_key, pipelined_html, 86400)

        return pipelined_html

