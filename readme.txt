1) This script makes an output in the form of a json.
    To run the script in terminal:
    python3 main.py <path to xml file> <name of output file>

    Example:
    python3 main.py hiwiki.bz2 out_up.json

3) Other files are modularised functions for enabling better reuse.
4) The sample_pages folder has sample xml files, the current output.json generated was tested for sample_page.xml
5) Certain urls were observed to be unscrapable while testing (such urls probably don't exist) hence will return type 'na'.
6) Script has been written such that it can scape html pages as well as pdf files from the url given directly.

Note: Only the relevant sections of the page are scraped (using the relevant_sections method for filtering relevant methods)