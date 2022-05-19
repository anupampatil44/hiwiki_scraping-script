import mwparserfromhell
import re


def ref_links(section_text):
    query = "(?<=<ref>)(.*?)(?=</ref>)"

    s = list(x.group() for x in re.finditer(query, str(section_text)))
    # print(s)
    finallist=[]
    for i in s:
        wikicode = mwparserfromhell.parse(i)
        listoflinks = list(wikicode.filter_external_links())
        for i in listoflinks:
            # print(re.findall(r'(https?://[^\s]+)|(http?://[^\s]+)', str(i)))
            finallist.append(re.findall(r'(https?://[^\s]+)', str(i))[0]) #regex cleans url properly to send clean url

    print("finalist:",finallist)
    return finallist



