import pandas as pd
import os
import requests
import json
import csv
import time
import datetime as dt
import generic_module
import comment_module

#calls the pushshift API for initial data grab
def getPushshiftData(query, after, before, sub):
    url = 'https://api.pushshift.io/reddit/search/submission/?title='+str(query)+'&size=1000&after='+str(after)+'&before='+str(before)+'&subreddit='+str(sub)
    print(url)
    retry = True
    while (retry == True):
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

#Collects data from a specific submission
def collectSubData(subm, subStats):
    subData = list() #list to store data points
    title = subm['title']
    url = subm['url']
    try:
        flair = subm['link_flair_text']
    except KeyError:
        flair = "NaN"
    author = subm['author']
    sub_id = subm['id']
    score = subm['score']
    created = dt.datetime.fromtimestamp(subm['created_utc']) #1520561700.0
    numComms = subm['num_comments']
    permalink = subm['permalink']

    subData.append((sub_id,title,url,author,score,created,numComms,permalink,flair))
    subStats[sub_id] = subData
    return subStats

#Creates the summary of the "raw" pulled submissions data
def updateSubs_file(subStats, sub, after, before, query, bucketDuration):
    upload_count = 0

    if not os.path.exists('.//data'):
        os.makedirs('.//data')
    location = ".//data//"

    print([sub, str(after.date()), str(before.date()), query + ".csv"])
    filename = '_'.join([sub, str(after.date()) + "_to_" + str(before.date()), query + ".csv"])
    file = location + filename
    with open(file, 'w', newline='', encoding='utf-8') as file:
        a = csv.writer(file, delimiter=',')
        headers = ["Post ID","Title","Url","Author","Score","Publish Date","Total No. of Comments","Permalink","Flair"]
        a.writerow(headers)
        for sub in subStats:
            a.writerow(subStats[sub][0])
            upload_count+=1

        print(str(upload_count) + " submissions have been uploaded")

    return (location, filename)

def main(sub, after, before, query, bucketDuration):

    subCount = 0
    subStats = {}

    afterOriginal = str(after.date())
    beforeOriginal = str(before.date())

    afterUnix = str(time.mktime(after.timetuple()))
    beforeUnix = str(time.mktime(before.timetuple()))

    dotIndex = beforeUnix.index('.')
    afterUnix = afterUnix[:dotIndex]
    beforeUnix = beforeUnix[:dotIndex]

    data = getPushshiftData(query, afterUnix, beforeUnix, sub)# Will run until all posts have been gathered
    dataProcessedCounter = 0
    # from the 'after' date up until before date
    while len(data) > 0:
        for submission in data:
            subStats = collectSubData(submission, subStats)
            subCount+=1
        # Calls getPushshiftData() with the created date of the last submission
        dataProcessedCounter += len(data)
        print(str(dataProcessedCounter))
        print(str(dt.datetime.fromtimestamp(data[-1]['created_utc'])))
        afterUnix = data[-1]['created_utc']
        data = getPushshiftData(query, afterUnix, beforeUnix, sub)

    print(len(data))
    print(str(len(subStats)) + " submissions have added to list")

    fileData = updateSubs_file(subStats, sub, after, before, query, bucketDuration)
    location = fileData[0]
    filename = fileData[1]
    dfScrape = pd.read_csv(location + filename)
    summaryData = generic_module.generic_summary(dfScrape, location, filename, "title", after, before, bucketDuration)

    return summaryData

if __name__ == "__main__":
    sub='pennystocks' #subreddit
    startTime = dt.datetime(2020,7,16,16) #Start date, EST
    endTime = dt.datetime(2020,7,17,12,30) #End date
    query = "" #Substring filter. Leave empty string for no filter.
    bucketDuration = None #Add timedelta equal to desired bucket length. Leave as "None" for general summary.
    main(sub, startTime, endTime, query, bucketDuration)

    #comment scraper (comment out if not wanted)
    #url = "https://www.reddit.com/r/wallstreetbets/comments/hgthpf/you_wouldnt_understand/"
    #comment_module.comment_module(url)
