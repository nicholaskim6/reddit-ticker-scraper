# reddit-ticker-scraper
Flexible scraper for stock ticker mentions on reddit. Outputs summary data on frequency of mentions for stock tickers. Also outputs raw submission data from the API call. All output is directed to a "data" folder made locally by the script.

Some of the more active stock-market related subreddits you might want to try this on would include r/wallstreetbets, r/pennystocks, r/robinhood, and r/stocks.

Uses Aho-Corasick string search to optimize ticker frequency counting, and ticker appearances in a title when surrounding by alphabetical characters are ignored (to avoid extraneous ticker appearances that may show up as part of other words).

# Basic Functionality
Given a time window and subreddit, collects data on all stock ticker mentions <br>

 Fields:<br>
   -"Titles" - number of thread titles a given ticker appeared in<br>
   -"Score" - cumulative upvotes for all threads where a given ticker appeared in the title<br>
   -"Comments" - cumulative number of comments for all threads where a given ticker appeared in the title<br>
   
Two main modes: "general" and "bucketed"<br>
 -general: returns data for each ticker summarizing the entire time window<br>
 -bucketed: returns data in buckets of a desired time length. (outputs three separate csvs for titles, scores, comments)<br>
 
Comment Scraping:<br>
  -separate "comment module" for scraping comment text from a given url and summarizing data<br>

Other: <br>
-"query" input allows filtering at the API level, which can improve runtime dramatically. Common use-case is if interested only in a particular ticker.<br>

# How to use
Use manually from the main of "pushcraft_scraper.py"<br>
-input desired fields<br>
-leave "query" as an empty string if no filtering is desired<br>
-leave bucketDuration as "None" if no bucketing is desired<br>
-"main()" function returns the summary data and also automatically writes them to csvs<br>
-"comment_module()" currently is run separately from the main() function<br>

If wanting to aggregate data from multiple subreddits:<br>
  -make a list of your subreddits<br>
  -loop through and run main(), saving each output<br>
  -sort the outputs by ticker<br>
  -combine all the dataframes<br>
  
 To integrate comment scraping:<br>
  -access the raw submission files in the "data" folder<br>
  -loop through the desired submissions and call the comment_module() on each url field<br>
  
  
# Other
-This scraper uses the PushShift API, not the official reddit API. PushShift is not updated live and may lag by several hours, though it compensates this with much better historical data, rate limits, and ease of time window querying.<br>
-There are many tickers matching common words (eg, stopwords, "GOOD", "KNOW") that commonly show up as false positives. I've filtered a bunch via the "detrituswords.csv" file but didn't want to go overboard filtering every possibility should there actually be interest in some of those tickers, so there will likely be some (easily identifiable) false positives when run.
 
