import mwparserfromhell
import re


def ref_links(section_text):
    query = "(?<=&lt;ref&gt;)(.*?)(?=&lt;/ref&gt;)"
    s = list(x.group() for x in re.finditer(query, str(section_text)))
    print(s)
    finallist=[]
    for i in s:
        wikicode = mwparserfromhell.parse(i)
        listoflinks = list(wikicode.filter_external_links())
        for i in listoflinks:
            finallist.append(re.findall(r'(https?://[^\s]+)', str(i))[0]) #regex cleans url properly to send clean url

    # print("No. of cite links:", len(s))
    # print(finallist)
    # print((len(finallist)))
    return finallist

