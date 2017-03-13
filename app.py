from flask import Flask, flash, render_template, request, redirect,jsonify
from werkzeug import generate_password_hash, check_password_hash
import yaml,requests,json
import datetime

"""This File uses MySQL ONLY"""

app = Flask(__name__)
app.secret_key = "KEY"
searched_name = ''
global_data = ''

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search',methods=['POST', 'GET'])
def search():
    global global_data
    try:
        if request.method == 'POST':
            result = request.form
            print result['search']
            searched_name = result['search']
            r=requests.get('http://goflo.in/search?q='+result['search'])
            r = json.loads(r.text)
            data = r.values()[0]['value']
            global_data = data
            for i in data:
                i['searched_term'] = result['search']
            #print data[0]
    except:
        return jsonify({"error":"error"})
            
    return render_template('search2.html',data = data)

@app.route('/details',methods=['POST', 'GET'])
def details():
    global global_data
    try:
        if request.method == 'POST':
            """
            data = request.form
            print data['app_no']
            results = ''
            for i in global_data:
                for j in i:
                    if j['application_no'] == data['app_no']:
                        print "ya"
                        results=j
                        print type(results)
            """
            print global_data
            results = global_data[0]
    except:
        return jsonify({"error":"error"})
            
    return render_template('details.html',results =results)


# _______________________________________________________ #

if __name__ == "__main__":
    app.run(debug=True, port=8080)

