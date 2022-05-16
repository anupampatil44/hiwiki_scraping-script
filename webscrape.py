import urllib
from urllib.request import Request, urlopen
import wikipedia
import json
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
# from PyPDF2 import PdfFileReader
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO
import io

def remove_tags(url):
    html_page = requests.get(url)
    soup = BeautifulSoup(html_page.content, "html.parser")
    text = []
    # for data in soup(['style', 'script']):
    for data in soup.find_all('p'):
        text.append(data.get_text())

    return ' '.join(text)


def convert_pdf_to_txt(path):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, laparams=laparams)

    # with open(path, 'rb') as fp:
    # fp=open(path, 'rb')

    req = Request(
        path,
        headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()
    # f = urllib.request.urlopen(path).read()
    fp = io.BytesIO(webpage)

    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    caching = True
    pagenos = set()

    for page in PDFPage.get_pages(fp, pagenos, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue()

    device.close()
    retstr.close()
    return text

# testing by passing a url:

#1) for pdf text:
# print(convert_pdf_to_txt('http://www.africau.edu/images/default/sample.pdf'))

#2) for html text:
# print(remove_tags('https://web.archive.org/web/20190215050340/https://hindi.timesnownews.com/world/article/hindi-to-become-third-language-used-in-abu-dhabi-dubai-court-system/363296'))