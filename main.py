# Where the real magic happens:
import re
import sys
import mwparserfromhell
import json

import requests

from document_type import content_type
from extract_sections import section_extraction, relevant_sections
from page_extract import page_extract, intro_extract
from preprocessing import remove_templates, cleaning
from link_extraction import ref_links
from webscrape import convert_pdf_to_txt, remove_tags
from tqdm import tqdm


import subprocess
import xml.sax

class WikiXmlHandler(xml.sax.handler.ContentHandler):
    """Content handler for Wiki XML data using SAX"""
    def __init__(self):
        xml.sax.handler.ContentHandler.__init__(self)
        self._buffer = None
        self._values = {}
        self._current_tag = None
        self._pages = []

    def characters(self, content):
        """Characters between opening and closing tags"""
        if self._current_tag:
            self._buffer.append(content)

    def startElement(self, name, attrs):
        """Opening tag of element"""
        if name :
            self._current_tag = name
            self._buffer = []
            self._buffer.append("<"+str(self._current_tag)+">")

    def endElement(self, name):
        """Closing tag of element"""
        if name == self._current_tag:
            self._values[name] = ''.join(self._buffer)+"</"+str(self._current_tag)+">"

        if name == 'page':
            self._pages.append(self._values)


# Object for handling xml
handler = WikiXmlHandler()
# Parsing object
parser = xml.sax.make_parser()
parser.setContentHandler(handler)
# Iteratively process file
no_pages=0



def pipeline(page_txt=None):
    page_txt = mwparserfromhell.parse(page_txt)

    sections, main_section_names = section_extraction(page_txt)
    # print("Sections:\n",sections)

    # lets scrape only the relevant sections, i.e. having word count>=avg of all sections:
    relevant, relevant_indice = relevant_sections(sections)
    # print("Relevant Sections:",relevant)
    clean = remove_templates(relevant)
    # print("Cleaned text sectionwise:\n",clean)

    # getting links:
    link_list = []
    for i in range(len(relevant)):
        temp_link_list = ref_links(str(relevant[i]))
        # print(re.findall(r'(https?://[^\s]+)', str(relevant[i])))
        print("temp_link_list:",temp_link_list)
        link_list.append(temp_link_list)

    output = []

    print("no. of links:",len(link_list))
    print(link_list)
    for i in range(len(link_list)):
        temp = []
        # print("Section:",i)

        for j in range(len(link_list[i])):
            # print("link_list:",link_list)
            try:
                r = requests.get(link_list[i][j]).status_code
            except Exception as e:
                print(e)
                r=403
                pass

            print("link:", link_list[i][j])

            print("value of r:", type(r))

            if int(r)== 200:
                contentt = content_type(link_list[i][j])
                print("Link "+str(j)+" of type:",contentt)
                scraped_text = ""
                if contentt == 'pdf':
                    scraped_text += convert_pdf_to_txt(link_list[i][j])
                elif contentt == 'html':
                    scraped_text += remove_tags(link_list[i][j])
                else:
                    print("Unable to scrape this url.", link_list[i][j])
                    continue

                print("")


                scraped_text = scraped_text.replace('\n', ' ')
                scraped_text = scraped_text.replace('\r', ' ')
                scraped_text = scraped_text.replace('\b', ' ')
                # remove excess spacings also:
                scraped_text = re.sub(r'\s\s+', ' ', scraped_text)

                temp.append(scraped_text)

        output.append(
            {'title': main_section_names[relevant_indice[i]].strip(), 'content': clean[i], 'references': temp})

    return output


# pipeline() #pass xml filepath as argument here

def intro_data(page):
    intro = intro_extract(str(page))
    # intro=page  #temporary
    parsed_text = mwparserfromhell.parse(intro)

    refs = ref_links(parsed_text)
    clean_intro = cleaning(parsed_text)

    references = []
    for i in range(len(refs)):
        try:
            r = requests.get(refs[i]).status_code
        except Exception as e:
            print(e)
            r = 403

        # print("value of r:",type(r))

        if int(r) == 200:
            contentt = content_type(refs[i])
            scraped_text = ""
            if contentt == 'pdf':
                scraped_text += convert_pdf_to_txt(refs[i])
            elif contentt == 'html':
                scraped_text += remove_tags(refs[i])
            else:
                print("Unable to scrape this url.", refs[i])
                continue

            scraped_text = scraped_text.replace('\n', ' ')
            scraped_text = scraped_text.replace('\r', ' ')
            scraped_text = scraped_text.replace('\b', ' ')
            # remove excess spacings also:
            scraped_text = re.sub(r'\s\s+', ' ', scraped_text)
            print("scraped text:",scraped_text)
            references.append(scraped_text)

    out = {
        "title": "Introduction",
        "content": clean_intro,
        "references": references
    }

    return out


def main_script(xml_str):
    # xml_path = 'sample_pages/sample_page.xml'

    page_txt = xml_str

    pages = page_extract(mwparserfromhell.parse(page_txt))

    # output=[]
    f = open('final_titles.json', 'r')
    data = json.load(f)
    print("Total no. of pages:", len(pages))
    for domain, val in data.items():
        outfile = open(str(sys.argv[2]) + f'{domain}.json', 'a')
        title_list = data[domain]['hi']
        for i in tqdm(range(len(pages))):

            intro = intro_data(pages[i])

            title = re.findall("<title>(.*?)</title>", str(pages[i]), re.DOTALL)[0]
            # print("Page no.:",str(i))
            if title in title_list:
                op = pipeline(pages[i])
                op.append(intro)
                temp = {"title": title, "sections": op}
            # output.append({"title":title,"sections":op})

            outfile.write(json.dumps(temp, ensure_ascii=False))
            outfile.write('\n')

        outfile.close()



# iteratation:
no_pages=0
def iterative_run(bz2_path=str(sys.argv[1])):
    for line in subprocess.Popen(['bzcat'],
                                 stdin=open(bz2_path),
                                 stdout=subprocess.PIPE).stdout:
        parser.feed(line)

        global no_pages
        # Stop when 5 articles have been found

        if len(handler._pages)>no_pages:
            pagestr = ""
            no_pages+=1
            pagestr+=("<page>\n")
            for key in handler._pages[no_pages-1]:
                print(handler._pages[no_pages-1][key])
                pagestr+=(str(handler._pages[no_pages-1][key]) + '\n')
            pagestr+="</page>\n"

            main_script(pagestr)

        if len(handler._pages)==5:
            break

iterative_run(bz2_path=str(sys.argv[1]))