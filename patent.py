import json,re
import string,requests,time,datetime
import urllib2,urllib,sys,base64,json,time
import pydocumentdb.document_client as document_client
from collections import Counter,defaultdict

HOST = "https://patent.documents.azure.com:443/"
MASTER_KEY = "mNPHraFUF7h5KI2JID0l7ocwvGbPdFRWDlDRoh8Dy3hqW6ipm2PNZOY7gPewq14EzwSRflfHLBNljwmCzG1eIg=="
DB = 'dbs/patents/colls/patents'
COUNT_DB = 'dbs/patents/colls/count'
client = document_client.DocumentClient(HOST, {'masterKey':MASTER_KEY})
json_list = []

entity_count = Counter() 
dates_dict = defaultdict(list)

def update_count_db():
    global entity_count,dates_dict
    for i in entity_count:
        count_json = {"entity_name":i.lower(),"count":entity_count[i.lower()],"dates": dates_dict[i.lower()]}    
        document = client.CreateDocument(COUNT_DB,count_json)
    print 'done'    
    

class Patent():
    def __init__(self):
        self.application_no = 'failed'
        self.publication_date = 'failed'
        self.filing_date = 'failed'
        self.title = 'failed'
        self.applicants = []
        self.inventors = 'failed'
        self.abstract = 'failed'
        self.no_pages = 'failed'
        self.no_claims = 'failed'

    def update_db(self):

            global json_list,MASTER_HOST,KEY,client,entity_count,dates_dict


            base_url = 'https://westus.api.cognitive.microsoft.com/'
            account_key = "24044655068b484f90818d28bf43e9ff"
            headers = {'Content-Type':'application/json', 'Ocp-Apim-Subscription-Key':account_key}

            """Key phrase """
            input_texts = {'documents':[{"id":"1","text":self.abstract}]}
            input_texts = json.dumps(input_texts)
    
            batch_keyphrase_url = base_url + 'text/analytics/v2.0/keyPhrases'
            try:
                req = urllib2.Request(batch_keyphrase_url, input_texts, headers) 
                response = urllib2.urlopen(req)
                result = response.read()
            except:
                return True
            obj = json.loads(result)
            keyphrases = obj['documents'][0]['keyPhrases']

            """Entities extraction"""
            entities = []

            d = {'text':self.abstract.strip('" "\n[]'),"model":"en"}
            d = json.dumps(d)
            r=requests.post('http://34.249.102.117:8000/ent',data=d)

            res = r.json()
            for i in res:
                if i['type'] in ['ORG','PERSON','PRODUCT','WORK_OF_ART']:
                    e = (self.abstract[i['start']:i['end']].lower(),i['type'])
                    k = re.sub(r'[\W_]+','',self.application_no)
                    entities.append((k,e[0]))
                    entity_count.update([k])

            pub_date =  datetime.datetime.strptime(self.publication_date.strip('" "\n[]'),'%d/%m/%Y')
            pub_date =  int(time.mktime(pub_date.timetuple()))
                    
            file_date =  datetime.datetime.strptime(self.filing_date.strip('" "\n[]'),'%d/%m/%Y')
            file_date =  int(time.mktime(file_date.timetuple()))

            self.application_no = re.sub(r'[\W_]+','',self.application_no)

            res = {
                'application_no':self.application_no.strip('" "\n[]'),
                'publication_date':pub_date,
                'date_of_filing':file_date,
                'title':self.title.strip('" "\n[]')  ,
                'applicants':" ".join(re.findall("[a-zA-Z]+",str(self.applicants))),
                'inventors':" ".join(re.findall("[a-zA-Z]+",str(self.inventors))),
                'abstract':self.abstract.strip('" "\n[]'),
                'no_of_pages':self.no_pages.strip('" "\n[]'),
                'no_of_claims':self.no_claims.strip('" "\n[]'),
                "entities":entities,
                "keyphrases":keyphrases
                }
            print res 
            """    
            for i in entities:
                if dates_dict.has_key(i[0]):
                    dd = dates_dict.get(i[0])
                    dd.append(file_date)
                else:
                    dd = []
                    dd.append(file_date)    
                dates_dict[i[0]] = dd      
                #print count_json,entity_count
            """
            for i in entities:
                dates_dict[i[0]].append(pub_date)
            try:
                #document = client.CreateDocument(DB,res)
                print 'hi,'
            except:
                print 'no'
                return True    
            
            return True
