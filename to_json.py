import json,re
import string
import urllib2,urllib,sys,base64,json,time
import polyglot
#from polyglot.text import Text, Word
import spacy

nlp = spacy.load('en')

def get_json(filename):

	global nlp
	f = open(filename).readlines()
	f.pop()
	f.pop(0)
	f.pop(0)
	
	k = string.find(f[0],':')
	app_no = f[0][k+1:].strip('" "\n[]')	

	k = string.find(f[1],':')
	pub_date = f[1][k+1:].strip('" "\n[]')	

	k = string.find(f[2],':')
	date_fil = f[2][k+1:].strip('" "\n[]')	

	k = string.find(f[3],':')
	title = f[3][k+1:].strip('" "\n[]')	

	k = string.find(f[4],':')
	applicants= " ".join(re.findall("[a-zA-Z]+",f[4][k+1:]))

	k = string.find(f[5],':')
	inventors = " ".join(re.findall("[a-zA-Z]+",f[5][k+1:]))

	k = string.find(f[6],':')
	abstract = f[6][k+1:].strip('" "\n[]')	

	k = string.find(f[7],':')
	no_of_pages = f[7][k+1:].strip('" "\n[]')	

	k = string.find(f[8],':')
	no_of_claims = f[8][k+1:	].strip('" "\n[]')	


	"""Named entity recognition"""

	entities = []
	doc = nlp((abstract).decode('utf-8'))
	for ent in doc.ents:
		if ent.label_ in ['ORG','PERSON','PRODUCT','WORK_OF_ART']:
			entities.append((ent.label_,ent.text))
	print entities
	
	base_url = 'https://westus.api.cognitive.microsoft.com/'
	account_key = "24044655068b484f90818d28bf43e9ff"
	headers = {'Content-Type':'application/json', 'Ocp-Apim-Subscription-Key':account_key}

	"""Key phrase """
	input_texts = {'documents':[{"id":"1","text":abstract}]}
	input_texts = json.dumps(input_texts)
	
	batch_keyphrase_url = base_url + 'text/analytics/v2.0/keyPhrases'
	req = urllib2.Request(batch_keyphrase_url, input_texts, headers) 
	response = urllib2.urlopen(req)
	result = response.read()
	obj = json.loads(result)

	keyPhrases = obj['documents'][0]['keyPhrases']

	dick = {
		"application_number":app_no,
		"published_date":pub_date,
		"date_filed":date_fil,
		"title":title,
		"applicants":applicants,
		"inventors":inventors,
		"abstract":abstract,
		"no_of_pages":no_of_pages,
		"no_of_claims":no_of_claims,
		"entities":entities,
		"keyphrases":keyphrases
		}
	#print dick	


	return json.dumps(dick)

