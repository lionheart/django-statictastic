from django import template
from lxml import html
import re
import requests

register = template.Library()

# Pull out urls
# Compile them
# Download them
# Combine them
# Upload them
# Return URL

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
        root = html.fragments_fromstring(output)
        elements_to_remove = []
        css_urls = []
        for element in root:
            if element.tag == "link" and 'rel' in element.attrib and element.attrib['rel'] == "stylesheet":
                elements_to_remove.append(element)
                if settings.DEBUG:
                    css_urls.append("{}{}".format(settings.BASE_URL, element.attrib['href']))

        css = ""
        for url in css_urls:
            response = requests.get(url)
            css += response.body

        print css

        return output.upper()

