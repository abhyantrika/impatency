import pymongo,json

conn = pymongo.MongoClient('localhost',27017)    
conn.admin.authenticate('root','')

db = conn.patents
collection = db.patents

