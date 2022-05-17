import re
import mwparserfromhell

def page_extract(xml_input):
    query="<page>(.*?)</page>"
    pages = re.findall(query, str(xml_input), re.DOTALL)
    print("No. of pages:", len(pages))

    return pages

def intro_extract(page_text):
    query = "<text [^>]+>(.*?)==[^>]+=="
    x = re.findall(query, str(page_text), re.DOTALL)[0]
    return x

# intro_extract(mwparserfromhell.parse(open('sample_pages/sample_page.xml','r').read()))
#
# print(mwparserfromhell.parse(open('sample_pages/sample_page.xml','r').read()))