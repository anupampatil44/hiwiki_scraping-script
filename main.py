# Where the real magic happens:
import re
import sys
import mwparserfromhell
import json
from document_type import content_type
from extract_sections import section_extraction, relevant_sections
from page_extract import page_extract, intro_extract
from preprocessing import remove_templates, cleaning
from link_extraction import ref_links
from webscrape import convert_pdf_to_txt, remove_tags

class IteratorAsList(list):
    def __init__(self, it):
        self.it = it
    def __iter__(self):
        return iter(self.it)
    def __len__(self):
        return 1

def pipeline(page_txt=None):

    page_txt=mwparserfromhell.parse(page_txt)

    sections,main_section_names=section_extraction(page_txt)
    # print("Sections:\n",sections)

    # lets scrape only the relevant sections, i.e. having word count>=avg of all sections:
    relevant,relevant_indice=relevant_sections(sections)
    print("Relevant Sections:",relevant)
    clean=remove_templates(relevant)
    # print("Cleaned text sectionwise:\n",clean)

    # getting links:
    link_list=[]
    for i in range(len(relevant)):
        temp_link_list=ref_links(relevant[i])
        link_list.append(temp_link_list)

    output=[]

    for i in range(len(link_list)):
        temp=[]
        print("Section:",i)
        if(len(clean[i])==0): # nothing left to process
            continue
        for j in range(len(link_list[i])):
            contentt=content_type(link_list[i][j])
            print("Link "+str(j)+" of type:",contentt)
            scraped_text=""
            if contentt=='pdf':
                scraped_text+=convert_pdf_to_txt(link_list[i][j])
            elif contentt=='html':
                scraped_text +=remove_tags(link_list[i][j])
            else:
                print("Unable to scrape this url.")
                continue

            scraped_text = scraped_text.replace('\n', ' ')
            scraped_text = scraped_text.replace('\r', ' ')
            scraped_text = scraped_text.replace('\b', ' ')
            # remove excess spacings also:
            scraped_text = re.sub(r'\s\s+', ' ', scraped_text)

            temp.append(scraped_text)

        output.append({'title':main_section_names[relevant_indice[i]].strip(),'content':clean[i],'references':temp})



    return output



# pipeline() #pass xml filepath as argument here

def intro_data(page):
    intro = intro_extract(str(page))
    # intro=page  #temporary
    parsed_text=mwparserfromhell.parse(intro)

    refs=ref_links(parsed_text)
    clean_intro=cleaning(parsed_text)

    references=[]
    for i in range(len(refs)):
        contentt = content_type(refs[i])
        scraped_text = ""
        if contentt == 'pdf':
            scraped_text += convert_pdf_to_txt(refs[i])
        elif contentt == 'html':
            scraped_text += remove_tags(refs[i])
        else:
            print("Unable to scrape this url.")
            continue

        scraped_text = scraped_text.replace('\n', ' ')
        scraped_text = scraped_text.replace('\r', ' ')
        scraped_text = scraped_text.replace('\b', ' ')
        # remove excess spacings also:
        scraped_text = re.sub(r'\s\s+', ' ', scraped_text)

        references.append(scraped_text)

    out={
            "title":"Introduction",
            "content":clean_intro,
            "references":references
        }

    return out





def main_script(xml_path=sys.argv[1]):
    # xml_path = 'sample_pages/sample_page.xml'
    page_txt = open(xml_path, 'r').read()

    pages=page_extract(mwparserfromhell.parse(page_txt))

    output=[]

    print("Total no. of pages:",len(pages))
    for i in range(len(pages)):
        intro=intro_data(pages[i])

        title=re.findall("<title>(.*?)</title>", str(pages[i]), re.DOTALL)[0]
        print("Page no.:",str(i))
        op=pipeline(pages[i])
        op.append(intro)
        output.append({"title":title,"sections":op})



    with open(str(sys.argv[2]), 'w') as out_file:
        json.dump(IteratorAsList(output), out_file,indent=4,ensure_ascii=False)




main_script()
