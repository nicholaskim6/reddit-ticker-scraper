# reddit-ticker-scraper
Flexible scraper for stock ticker mentions on reddit (for if you've ever been curious about what the folks on r/wallstreetbets were/are talking about at sometime)
Outputs summary data on frequency of mentions for stock tickers. Also outputs raw submission data from the API call. All output is directed to a "data" folder made locally by the script.

# Basic Functionality
Given a time window and subreddit, collects data on all stock ticker mentions <br>
 -Fields:
   -"Titles" - number of thread titles a given ticker appeared in
   -"Score" - cumulative upvotes for all threads where a given ticker appeared in the title
   -"Comments" - cumulative number of comments for all threads where a given ticker appeared in the title
Two main modes: "general" and "bucketed"
 -general: returns data for each ticker summarizing the entire time window
 -bucketed: returns data in buckets of a desired time length. (outputs three separate csvs for titles, scores, comments)
Comment Scraping:
  -separate "comment module" for scraping comment text from a given url and summarizing data

-"query" input allows filtering at the API level, which can improve runtime dramatically. Common use-case is if interested only in a particular ticker.

# How to use
-Use manually from the main of "pushcraft_scraper.py"
-input desired fields
  -leave "query" as an empty string if no filtering is desired
  -leave bucketDuration as "None" if no bucketing is desired
-"main()" function returns the summary data and also automatically writes them to csvs
-"comment_module()" currently is run separately from the main() function

-If wanting to aggregate data from multiple subreddits:
  -make a list of your subreddits
  -loop through and run main(), saving each output
  -sort the outputs by ticker
  -combine all the dataframes
  
 -To integrate comment scraping:
  -access the raw submission files in the "data" folder
  -loop through the desired submissions and call the comment_module() on each url field
  
  
# Other
This scraper uses the PushShift API, not the official reddit API. PushShift is not updated live and may lag by several hours, though it compensates this with much better historical data, rate limits, and ease of time window querying.
 
