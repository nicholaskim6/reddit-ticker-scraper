import copy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import time
import datetime as dt
import ahocorasick

#checks a string for a given ticker, ignoring instances where non-alphanumeric characters border it
def checkTicker(text, ticker):
    text = text.lower()
    ticker = ticker.lower()
    inText = False
    n = len(text) - (len(ticker)-1)
    for i in range(0, n):
        for j in range(i, i+len(ticker)):
            if (text[j] != ticker[j-i]):
                break
            if (j == i+len(ticker)-1): #found substring. Now check edges
                if (i > 0): #check char left of substring is non-alphabetical
                    if (text[i-1].isalpha()):
                        break
                if (i < n-1): #check char right of substring is non-alphabetical
                    if (text[i+len(ticker)].isalpha()):
                        break
                inText = True
                return inText
    return inText

#Creates generalized summaries for a set of submissions - two modes: non-bucketed and bucketed
def generic_summary(df, location, filename, titlecomment, after, before, bucketDuration):

    tickerList = list(pd.read_csv("Tickers.csv")["Tickers"])

    #Words that are technically tickers but have high false positive rates - eg stopwords, "good", "know", etc.
    detritusWords = list(pd.read_csv('detrituswords.csv')['DetritusWords'])

    tickerList = [x for x in tickerList if x not in detritusWords]
    tickerCounts = {}
    for ticker in tickerList:
        tickerCounts[ticker] = [0,0,0] #titles, upvotes (score), and no. of comments

    buckets = []
    bucketedTickerCounts = []
    currentBucket = 0

    #Create time buckets
    if (bucketDuration is not None):
        bucketStart = after
        bucketEnd = after
        while (bucketEnd < before):
            bucketEnd = bucketEnd + bucketDuration
            if (bucketEnd > before):
                bucketEnd = before
            buckets.append((bucketStart, bucketEnd))
            bucketStart = bucketEnd

        for i in range(len(buckets)):
            bucketedTickerCounts.append(copy.deepcopy(tickerCounts))

    #Initialize string searcher
    A = ahocorasick.Automaton()
    for idx, key in enumerate(tickerList):
        A.add_word(key, (idx, key))
    A.make_automaton()

    # Loops through threads
    if (titlecomment == "title"):
        for i, title in enumerate(df['Title']):
            if df['Author'][i] == "[deleted]":
                continue
            #checks current date and adjusts the currentBucket counter
            if (bucketDuration is not None):
                date = dt.datetime.strptime(df["Publish Date"][i], "%Y-%m-%d %H:%M:%S")
                while (date > buckets[currentBucket][1]):
                    currentBucket += 1
            #gets rid of mysterious nan titles
            if (type(title) != str):
                title = str(title)


            initialSearch = A.iter(title.upper())
            tmpTickers = set({})
            for val in initialSearch:
                tmpTickers.add(val[1][1])
            for ticker in tmpTickers:
                if (checkTicker(title, ticker)):
                    if (bucketDuration is not None):
                        bucketedTickerCounts[currentBucket][ticker][0] += 1
                        bucketedTickerCounts[currentBucket][ticker][1] += df['Score'][i]
                        bucketedTickerCounts[currentBucket][ticker][2] += df['Total No. of Comments'][i]
                    else:
                        tickerCounts[ticker][0] += 1
                        tickerCounts[ticker][1] += df['Score'][i]
                        tickerCounts[ticker][2] += df['Total No. of Comments'][i]

    if (titlecomment == "comment"): #comment-mode ticker search
        for i, comment in enumerate(df['Comment']):
            initialSearch = A.iter(comment.upper())
            tmpTickers = set({})
            for val in initialSearch:
                tmpTickers.add(val[1][1])
            for ticker in tmpTickers:
                if (checkTicker(comment, ticker)):
                    tickerCounts[ticker][0] += 1
                    tickerCounts[ticker][1] += df['Score'][i]

    dfMentions = pd.DataFrame()

    dfMentionsTitles = pd.DataFrame()
    dfMentionsScores = pd.DataFrame()
    dfMentionsComments = pd.DataFrame()

    if (bucketDuration is None or titlecomment == "comment"): #dataframe creation
        x = tickerCounts
        mentions = {k: v for k, v in sorted(x.items(), key=lambda item: item[1][0], reverse = True)}
        dfMentions['Ticker'] = mentions.keys()
        titleNum = []
        scoreNum = []
        commentNum = []
        for val in mentions.values():
            titleNum.append(val[0])
            scoreNum.append(val[1])
            if (titlecomment == "title"):
                commentNum.append(val[2])
        if (titlecomment == "title"):
            dfMentions['Titles In'] = titleNum
        if (titlecomment == "comment"):
            dfMentions['Comments In'] = titleNum
        dfMentions['Score Weighted'] = scoreNum
        if (titlecomment == "title"):
            dfMentions['Comment Weighted'] = commentNum

        dfMentions.index = dfMentions['Ticker']
        dfMentions = dfMentions.drop(columns=['Ticker'])

    if (bucketDuration is not None): #dataframe creation
        dfMentions['Ticker'] = list(bucketedTickerCounts[0].keys())
        totalCount = {}
        for ticker in tickerList:
            totalCount[ticker] = 0

        for i in range(len(buckets)):
            tmpList = []
            for key in bucketedTickerCounts[0].keys():
                if (key in detritusWords):
                    tmpList.append([0,0,0])
                    continue
                tmpList.append(bucketedTickerCounts[i][key])
                totalCount[key] += bucketedTickerCounts[i][key][0]
            dfMentions[buckets[i][1]] = tmpList

        #If bucketed -> 3 separate dataframes for titles, scores, comments
        dfMentionsTitles = dfMentions.applymap(lambda x: x if type(x) == str else x[0])
        dfMentionsScores = dfMentions.applymap(lambda x: x if type(x) == str else x[1])
        dfMentionsComments = dfMentions.applymap(lambda x: x if type(x) == str else x[2])

        dfMentionsTitles['Total'] = list(totalCount.values())
        dfMentionsTitles.sort_values(by=['Total'], ascending = False, inplace = True)
        dfMentionsTitles = dfMentionsTitles.drop(columns = ['Total'])
        dfMentionsScores['Total'] = list(totalCount.values())
        dfMentionsScores.sort_values(by=['Total'], ascending = False, inplace = True)
        dfMentionsScores = dfMentionsScores.drop(columns = ['Total'])
        dfMentionsComments['Total'] = list(totalCount.values())
        dfMentionsComments.sort_values(by=['Total'], ascending = False, inplace = True)
        dfMentionsComments = dfMentionsComments.drop(columns = ['Total'])

        dfMentionsTitles.index = dfMentionsTitles['Ticker']
        dfMentionsTitles = dfMentionsTitles.drop(columns=['Ticker'])
        dfMentionsScores.index = dfMentionsScores['Ticker']
        dfMentionsScores = dfMentionsScores.drop(columns=['Ticker'])
        dfMentionsComments.index = dfMentionsComments['Ticker']
        dfMentionsComments = dfMentionsComments.drop(columns=['Ticker'])

    if (bucketDuration is not None):
        dfMentionsTitles.to_csv(location + "Titles_BucketedSummary_" + filename)
        dfMentionsScores.to_csv(location + "Scores_BucketedSummary_" + filename)
        dfMentionsComments.to_csv(location + "Comments_BucketedSummary_" + filename)
        return (dfMentionsTitles, dfMentionsScores, dfMentionesComments)
    else:
        dfMentions.to_csv(location + "Summary_" + filename)
        return dfMentions
    print("summary created")
