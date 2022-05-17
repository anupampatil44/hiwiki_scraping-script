import re
import mwparserfromhell


def section_extraction(wikicode):
  # get all section names:

  regex_for_section_names="(?<===)(.*?)((?= \/==)|(?===))"
  sections=list(x.group() for x in re.finditer(regex_for_section_names,str(wikicode)))
  print(sections)
  print("No. of sections and subsections:",len(sections))

  main_sections=[]
  subsections=[]
  for i in sections:
    if '=' not in i:
      main_sections.append(i)
    elif '=' in i and i.count('=')==1:
      subsections.append(i)

  print("Main sections:\n",main_sections)
  print()

  section_text=[]
  for i in range(1,len(main_sections)-1):
    x = re.findall('=={}==(.*?)=={}=='.format(main_sections[i-1],main_sections[i]),str(wikicode),re.DOTALL)
    section_text.append(x)

  # for the last section heading which may extend till the end of the text:
  x = re.findall('=={}==(.*?){}'.format(main_sections[-1],'</text>'),str(wikicode),re.DOTALL)
  section_text.append(x)

  # sectionwise extracted text
  print("Extracted sections:\n\n")
  return section_text,main_sections


def relevant_sections(section_text):
  # getting length of sections first:
  indice_list=[]
  denom=len(section_text)
  lenlist=[]
  for i in section_text:
    temp = mwparserfromhell.parse(i[0])
    # print(temp.strip_code().strip())
    lenlist.append(len(temp.strip_code().strip()))

  print('List of lengths:\n',lenlist)
  avglen=sum(lenlist)//denom
  print("Average length of sections:",avglen)

# only consider those sections with character-count>= average
  relevant_sections=[]
  for i in range(denom):
    temp = mwparserfromhell.parse(section_text[i][0])
    temp=temp.strip_code().strip()
    if len(temp)>=int(avglen):
      relevant_sections.append(section_text[i][0])
      indice_list.append(i)

  print('No. of relevant sections:',len(relevant_sections),'\n-------------------------------\n')
  return relevant_sections,indice_list

