import pandas as pd
import requests
import json
import csv
import time
import datetime
import generic_module
from urllib.parse import urlparse

def comment_module(url):
    idCode = urlparse(url).path.split('/')[4]
    commentIDsCall = "https://api.pushshift.io/reddit/submission/comment_ids/" + idCode

    def getPushshiftData(url): #grabs comment ids from pushshift api
        retry = True
        while(retry == True):
            counter = 0
            r = requests.get(url)
            if (r.text[0] != "{"):
                print("last request failed. Retrying")
                retry = True
                counter += 1
                if (counter > 3):
                    print("Failed request 3 times. Aborting")
                    return None
            else:
                retry = False

        data = json.loads(r.text)
        return data['data']

    commentIDs = getPushshiftData(commentIDsCall)
    print("Number of comments: " + str(len(commentIDs)))

    commentDataCall = "https://api.pushshift.io/reddit/comment/search?ids="
    commentData = []
    for i, commentID in enumerate(commentIDs): #converting comment ids into comment data
        commentDataCall += commentID + ","
        if ((i+1)%1000 == 0 or i == (len(commentIDs)-1)):
            print(i)
            commentDataCall = commentDataCall[:-1]
            newData = getPushshiftData(commentDataCall)
            commentData.append(newData)
            commentDataCall = "https://api.pushshift.io/reddit/comment/search?ids="

    newDf = pd.DataFrame()
    comments = []
    scores = []
    for call in commentData: #dataframe creation
        for val in call:
            comments.append(val['body'])
            scores.append(val['score'])

    newDf['Comment'] = comments
    newDf['Score'] = scores

    filename = urlparse(url).path.split('/')[5] + ".csv"
    summaryData = generic_module.generic_summary(newDf, ".\\data\\", filename, "comment", None, None, None)
    return summaryData
