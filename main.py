# Where the real magic happens:

import mwparserfromhell
import json
from document_type import content_type
from extract_sections import section_extraction, relevant_sections
from preprocessing import remove_templates
from link_extraction import ref_links
from webscrape import convert_pdf_to_txt, remove_tags


def pipeline(path=None):

    path='sample_pages/sample_page.xml'
    page_txt=open(path,'r').read()
    page_txt=mwparserfromhell.parse(page_txt)
    # print(page_txt)
    sections,main_section_names=section_extraction(page_txt)
    print("Sections:\n",sections)

    # lets scrape only the relevant sections, i.e. having word count>=avg of all sections:
    relevant,relevant_indice=relevant_sections(sections)
    print("Relevant Sections:",relevant)
    clean=remove_templates(relevant)
    print("Cleaned text sectionwise:\n",clean)

    # getting links:
    link_list=[]
    for i in range(len(relevant)):
        temp_link_list=ref_links(relevant[i])
        link_list.append(temp_link_list)

    output={}

    for i in range(len(link_list)):
        temp=[]
        print("i:",i)
        if(len(clean[i])==0): # nothing left to process
            continue
        for j in range(len(link_list[i])):
            contentt=content_type(link_list[i][j])
            # print("type:",contentt)
            scraped_text=""
            if contentt=='pdf':
                scraped_text+=convert_pdf_to_txt(link_list[i][j])
            elif contentt=='html':
                scraped_text +=remove_tags(link_list[i][j])
            else:
                print("Unable to scrape this url.")
                continue

        # if i>=1:
        #     break

            temp.append(scraped_text)

        output[i]={'title':main_section_names[relevant_indice[i]].strip(),'content':clean[i],'references':temp}

    out_file = open("output.json", "w")

    json.dump(output, out_file, indent=6)

    out_file.close()

pipeline()