'''
See documentation for get_statuses.py
'''
from os import listdir
from os.path import isfile, join
import sys
import json
import re
from nltk.corpus import stopwords
from nltk.tokenize import WordPunctTokenizer
import csv

sys.path.append('external')
import twokenize

#dev_set = []
#f = open("dev.txt", "r")
#for line in f:
#    dev_set.append(line.strip())
#dev_set = set(dev_set)
#f.close()

set_file = None
if len(sys.argv) > 4:
    set_file = sys.argv[4]

dev_set = []
if set_file:
    sfile = open(set_file)
    for line in sfile:
        dev_set.append(line.strip())
dev_set = set(dev_set)

mypath = sys.argv[1]
onlyfiles = [ f for f in listdir(mypath) if isfile(join(mypath,f)) ]

#outfile = open(sys.argv[2], 'ab')
label = sys.argv[3]
#csvwriter = csv.writer(outfile, quoting=csv.QUOTE_MINIMAL)
csvwriter1 = csv.writer(open(sys.argv[2]+'_label.csv', 'ab'), quoting=csv.QUOTE_MINIMAL, delimiter='\t')
csvwriter2 = csv.writer(open(sys.argv[2]+'_text.csv', 'ab'), quoting=csv.QUOTE_MINIMAL, delimiter='\t')
all_tweets = []
#t = WordPunctTokenizer()
count = 0
r = re.compile("(^|[^A-Za-z0-9_])@[A-Za-z0-9_]{1,16}($|[^A-Za-z0-9_])")
r2 = re.compile("^\w+$")
#csvwriter.writerow(["userid", "avg", "text"])
for fname in onlyfiles:
    if len(dev_set) > 0 and not fname in dev_set:
        continue
    f = open(mypath + "/" + fname, "r")
    tweets = ""
    tweet_count = 0
    for line in f.readlines():
        text = line #json.loads(line)["text"] + " "
        text = text.lower()
        #if "http" in text:
        #    continue
        #text = r.sub(r"\1@\2", text) #remove twitter id's
        #text = r.sub(r"\1@\2", text) #do it twice b/c won't catch consecutive
        tweets += text.strip() + " "
        tweet_count += 1
        #if tweet_count > 25:
        #    break
        try:
            pp_tweets = twokenize.tokenizeRawTweetText(text)
        except:
            continue
        pp_tweets = [w for w in pp_tweets if r2.match(w)]
        if len(pp_tweets) < 15:
            continue
        f_tweets = " ".join(pp_tweets)
        fid = fname.split(".")[0] + "_" + str(tweet_count)
        tmpFile = open(sys.argv[2] + "/" + fid, "w")
        tmpFile.write(f_tweets)
        tmpFile.close()
        csvwriter1.writerow([fid, label])
        csvwriter2.writerow([fid, f_tweets])


#    if tweet_count <= 25: #skip users with < 25 tweets
#        continue
#    try:
#        pp_tweets = twokenize.tokenizeRawTweetText(tweets)
#    except:
#        continue

    #pp_tweets = filter(lambda w: w not in stopwords.words('english'), pp_tweets)
#    pp_tweets = [w for w in pp_tweets if r2.match(w)]
    #f_tweets = tweets
#    f_tweets = " ".join(pp_tweets)
#    try:
#        f_tweets = f_tweets.encode("ascii", "ignore")
#    except:
#        continue
    #print fname.split(".")[0] + ",-," + tweets"
    #csvwriter.writerow([fname.split(".")[0] , label,f_tweets])
#    csvwriter1.writerow([fname.split(".")[0], label])
#    csvwriter2.writerow([fname.split(".")[0], f_tweets])
    #all_tweets.append((fname.split(".")[0], f_tweets))
    count += 1
    #if count == 100:
    #    break
    print count

#print count
   
