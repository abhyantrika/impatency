from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from cStringIO import StringIO
from patent import Patent
import re
from patent import update_count_db

def plain(string_val):
    return re.sub('\W+','', string_val )

def get_value(s, delim):
    return s.partition(delim)[2]

def convert_pdf_to_txt(path,maxpno=0,pnos=set()):
    #initialise PDFMiner Parameters
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = file(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = maxpno
    caching = True
    pagenos=pnos
    # Extract and interpret each page of the Patent Journal
    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)
    
    #Clean up and Return extracted text
    fp.close()
    device.close()
    resstr = retstr.getvalue()
    retstr.close()
    return resstr

def convert_and_parse(pdfpath,outpath,verbose = True):
    fname = outpath

    ## Convert PDF in parts to text
    
    s = convert_pdf_to_txt(pdfpath,11,[8,27,26]) ##FOR TESTING PURPOSES    
    #s = convert_pdf_to_txt(pdfpath)

    ## Save converted text to a file
    with open(fname, "w") as outfile:
        outfile.write(s)

    ## Read content into list    
    lines = [line for line in open(fname, "r").read().splitlines() if line]

    patents = []
    
    i = 0
    no_lines = len(lines)
    ## Separate Patent Sections
    while i < no_lines :        
        ## Identify the starting of an application
        if plain("PATENT APPLICATION PUBLICATION") in plain(lines[i]):
            patent = []
            ## Add lines pertaining to the current patent to the patent list
            while plain("The Patent Office Journal") not in plain(lines[i]):
                patent.append(lines[i].strip())
                i = i + 1
            ## Append the patent to the patents list
            patents.append(patent)
        else:
            i = i + 1
    if(verbose == True):
        print("No of Patents: ",len(patents))
        with open("raw_"+fname, "w") as outfile:            
            for patent in patents:
                outfile.write("####Patent Begin#####\n")
                print("####Patent Begin#####")
                process_patent(patent)
                outfile.write(str(patent))                
                outfile.write("\n####Patent End#####\n")
                print("####Patent End#####")

def process_patent(data):
    pobj = Patent()
    i = 0
    no_lines = len(data)
    
    ## define search strings for fields
    s_application_no = '(21) Application No.'
    s_publication_date = '(43) Publication Date : '
    s_filing_date = '(22) Date of filing of Application :'
    s_title = '(54) Title of the invention : '
    s_applicants = '(71)Name of Applicant :'
    s_inventors = '(72)Name of Inventor :'
    s_abstract = '(57) Abstract :'
    s_no_pages = 'No. of Pages : '
    s_no_claims = ' No. of Claims : '
 



    ## Separate Patent Sections
    while i < no_lines :   
        if len(data[i]) == 0:
            i += 1
        if plain(s_application_no) in plain(data[i]):
            pobj.application_no = get_value(data[i],s_application_no)            
        
        elif plain(s_publication_date) in plain(data[i]):
            pobj.publication_date = get_value(data[i],s_publication_date)
        
        elif plain(s_filing_date) in plain(data[i]):
            pobj.filing_date = get_value(data[i],s_filing_date)

        elif plain(s_title) in plain(data[i]):
            tmp_title = []
            tmp_title.append(get_value(data[i],s_title))
            i += 1
            while plain("(51) International") not in plain(data[i]) and ":" not in data[i]:
                tmp_title.append(data[i])
                i += 1            
            pobj.title = ''.join(tmp_title[:-2])
            if plain(s_applicants) in plain(data[i]):
                i -= 1
        
        elif plain(s_applicants) in plain(data[i]):
            tmp_applicant = []            
            i += 1
            while plain("Address of") not in plain(data[i]):
                tmp_applicant.append(data[i])
                i += 1            
            pobj.applicants = tmp_applicant

        elif plain(s_inventors) in plain(data[i]):
            tmp_inventors = []            
            i += 1
            while ":" not in data[i] and plain(s_abstract) not in plain(data[i]): 
                tmp_inventors.append(data[i])
                i += 1            
            pobj.inventors = tmp_inventors
            if plain(s_abstract) in plain(data[i]):
                i -= 1
                            
        ## Identify the starting of abstract and save it to patent object
        elif plain(s_abstract) in plain(data[i]):
            abstract = ''.join(data[i+1:-1])
            pobj.abstract = abstract
            i = len(data)-1  
            tmp_pages = get_value(data[i],s_no_pages)
            tmp_pages = tmp_pages.partition(s_no_claims)
            pobj.no_pages = tmp_pages[0]
            pobj.no_claims = tmp_pages[2]              
        
        ##increment
        i = i + 1
    pobj.update_db()
    update_count_db()



if __name__ == "__main__":
    convert_and_parse("Part1.pdf","out.txt",verbose = True)   
