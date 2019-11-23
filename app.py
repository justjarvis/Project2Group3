############
import os
import pymongo
import json
from bson import json_util, ObjectId
from bson.json_util import dumps
from flask import Flask, render_template, Markup, request, redirect, jsonify
import requests
############
import zipfile
import pathlib
from pathlib import Path
############
from collections import defaultdict
import re
import string
############
import pandas as pd
from datetime import datetime
############
import heapq


# Create an instance of Flask
app = Flask(__name__)
MONGO_URL = os.environ.get('MONGO_URL')

myclient = pymongo.MongoClient(MONGO_URL, maxPoolSize=50, connect=True)

stuff = {'text':'BLANK','count':0}
data_path = 'static/data/'
unzip_path = 'static/data/unzip/'





@app.route('/', methods=['GET', 'POST', 'OPTIONS'])
def home():
    """Landing page."""
    return render_template("index.html", stuff=stuff)





@app.route("/setup")
def setup():
    if not os.path.exists(f'{data_path}/_dir.csv'):
        with zipfile.ZipFile(f'{data_path}/data.zip', 'r') as zip_ref:
            zip_ref.extract('_dir.csv',data_path)
    
    with open(f'{data_path}/_dir.csv', 'r', encoding='utf8') as docpath:
        df = pd.read_csv(docpath, header=0)
    
    # temp_list = []
    # temp_dict = {}
    # for colname in df.columns:
    #     temp_dict[colname] = df[colname]
    # temp_list.append(temp_dict)
    # print(temp_list)
    
    return df.to_json(orient='records')
    





@app.route("/barchart/<search_word>")
def findbar(search_word):
    
    print(search_word)

    print('Starting query...')
    mydb = myclient["example_db"]
    mycol = mydb["example_coll"]

    ###### QUERIES ############
    #myquery = {'word_counts.word': 'country' }
    #myquery =  {"word_counts.word" : { "$in" : ['constituent', 'illegally'] } } # has specific value (faster than above)
    myquery =  {"word_counts.word" : { "$in" : [search_word] } } # has specific value
    #myquery =  {"word_counts.word" : { "$all" : ['war', 'terrorism'] } } # has both values
    #myquery = {"president" : { "$in" : ['George Washington', 'John F. Kennedy'] } }
    ############################

    cursor = json.loads(dumps(mycol.find(myquery)))
    myclient.close()
    
    print('...Finished query.')
    print(len(cursor))

    results_list = []
    #init_d = {'George Washington' : 0,'John Adams':0,'Thomas Jefferson':0,'James Madison':0,'James Monroe':0,'John Quincy Adams':0,'Andrew Jackson':0,'Martin Van Buren':0,'William Henry Harrison':0,'John Tyler':0,'James K. Polk':0,'Zachary Taylor':0,'Millard Fillmore':0,'Franklin Pierce':0,'James Buchanan':0,'Abraham Lincoln':0,'Andrew Johnson':0,'Ulysses S. Grant':0,'Rutherford B. Hayes':0,'James Garfield':0,'Chester Arthur':0,'Grover Cleveland':0,'Benjamin Harrison':0,'Grover Cleveland':0,'William McKinley':0,'Theodore Roosevelt':0,'William Howard Taft':0,'Woodrow Wilson':0,'Warren G. Harding':0,'Calvin Coolidge':0,'Herbert Hoover':0,'Franklin D. Roosevelt':0,'Harry S. Truman':0,'Dwight Eisenhower':0,'John F. Kennedy':0,'Lyndon B. Johnson':0,'Richard Nixon':0,'Gerald Ford':0,'Jimmy Carter':0,'Ronald Reagan':0,'George Bush':0,'Bill Clinton':0,'George W. Bush':0,'Barack Obama':0,'Donald Trump':0}
    
    pc_dict = defaultdict(int)
    results_list = []

    for x in cursor:
        for i in x['word_counts']:
            if i['word'] == search_word:
                c = i['count']
                p = x['president']
        pc_dict[p] += c

    for k in pc_dict:
        temp_d = {}
        temp_d['president'] = k
        temp_d['count'] = pc_dict[k]
        results_list.append(temp_d)
    
    print(results_list)

    #return jsonify(list(cursor))
    return jsonify(list(results_list))



@app.route("/wordcloud/<search_word>")
def findwc(search_word):
    
    print('Starting query...')
    print(search_word)
    mydb = myclient["example_db"]
    mycol = mydb["example_coll"]
    
    ###### QUERY #####
    myquery =  {"president" : { "$in" : [search_word] } } # has specific value
    ####################

    cursor = json.loads(dumps(mycol.find(myquery)))
    myclient.close()
    
    print('...Finished query.')
    #print(len(cursor))
    
    results_list = []
    wc_dict = defaultdict(int)
    for x in cursor:
        for i in x['word_counts']:
            w = i['word']
            c = i['count']
            wc_dict[w] += c
    #print(wc_dict)
    temp_list = heapq.nlargest(20, wc_dict, key=wc_dict.get)
    for val in temp_list:
        temp_d = {"word": val, "count": wc_dict.get(val)}
        results_list.append(temp_d)

    print(results_list)
    return jsonify(list(results_list))




@app.route("/readfull/<search_word>")
def finddocs(search_word):

    print('Starting query...')
    print(search_word)
    mydb = myclient["example_db"]
    mycol = mydb["example_coll"]
    
    ############
    myquery =  {"word_counts.word" : search_word} # has specific value
    ############
    cursor = json.loads(dumps(mycol.find(myquery)))
    myclient.close()
    print(jsonify(list(cursor)))

    return jsonify(list(cursor))



@app.route("/fileup/<jspath>")
def fileup(jspath):
    print('hello')
    # with open(jspath, 'r') as file:
    #     filetext = file.read()
    #     filetext = re.sub('<.+>', '', filetext)
    #     print(filetext)

    return json.dumps(filetext)





@app.route("/injest")
def injest():
    ### unzip files
    pathlib.Path(unzip_path).mkdir(parents=False, exist_ok=True)
    with zipfile.ZipFile(f'{data_path}/data.zip', 'r') as zip_ref:
        zip_ref.extractall(unzip_path)
    ###
    mydb = myclient["example_db"]
    mycol = mydb["example_coll"]
    mycol.drop()

    #get directory/object structure from _dir.csv file
    with open(f'{unzip_path}/_dir.csv', 'r', encoding='utf8') as docpath:
        df = pd.read_csv(docpath, header=0)

    os.remove(f'{unzip_path}/_dir.csv') #delete _dir.csv
    #os.rename(f'{unzip_path}/_dir.csv', 'static/data/_dir.csv') #move _dir.csv
    
    entry_dict = {}
    print('begin db entries...')

    for (root,dirs,files) in os.walk(unzip_path, topdown=True):
        if files != [] :
            dirname = str(root.split("\\")[-1])
            
            #interpret info from _dir.csv for object keys
            for colname in df.columns:
                row = df.loc[df['_dir'] == dirname].index.values.astype(int)[0]
                entry_dict[colname] = str(df.at[row,colname])
            entry_dict['_dir'] = root
            #######
            for (file) in files:
                filename = str(Path(file).with_suffix(''))
                entry_dict['filename'] = filename
            
                docpath = open(f'{root}/{file}', 'r', encoding='utf8')
                fulltext = docpath.read()
            
                try:
                    doctitle = re.search('<title="(.*)">', fulltext).group(1)
                except:
                    doctitle = ''
                try:
                    docdate_long = re.search('<date="(.*)">', fulltext).group(1)
                    docdate = datetime.strftime(datetime.strptime(docdate_long,'%B %d, %Y'), '%Y/%m/%d')
                except:
                    docdate = ''
                entry_dict['title'] = doctitle
                entry_dict['date_ymd'] = docdate
                entry_dict['date'] = docdate_long

                #remove title, date, newlines, punctuation marks
                proc1 = re.sub('<.+>', '', fulltext).lower().strip('\n\r')
                bodytext = proc1.translate({ord(i): None for i in '.,;:?!-=+''"()[]''{''}$&'''})
                words_list = str.split(bodytext)
                
                freq_dict = defaultdict(int)
                stopwords = ['which','or','are','and', 'it', 'that', 'is', 'be', 'being', 'been', 'not', 'this', 'i', 'was', 'have', 'a','aboard','about','above','across','after','against','along','amid','among','an','anti','around','as','at','away','before','behind','below','beneath','beside','besides','between','beyond','but','by','concerning','considering','despite','down','during','except','excepting','excluding','following','for','from','in','inside','into','like','minus','near','next','of','off','on','onto','opposite','out','outside','over','past','per','plus','regarding','round','save','since','than','the','through','til','till','to','toward','towards','under','underneath','unlike','until','up','upon','versus','via','with','within','without']

                
                for word in words_list:
                    if word not in stopwords:
                        freq_dict[word] += 1
                
                freqs_list = []
                for key in freq_dict:
                    temp_d = {}
                    temp_d['word'] = key
                    temp_d['count'] = freq_dict[key]
                    freqs_list.append(temp_d)

                entry_dict['word_counts'] = freqs_list
                
                with open(f'{unzip_path}../temp.json', 'w') as fp:
                    json.dump(entry_dict, fp)
                with open(f'{unzip_path}../temp.json') as J:
                    file_data = json.load(J)
                mycol.insert_one(file_data)
                print(f"Inserted: {filename}")
    
    print('...db entries done')
    myclient.close()
    
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
