import tweepy
import pandas as pd
import datetime as dt
import re
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from datetime import timezone
from secrets import twitter_Bearer_Token

# Authentication using the twitter bearer token.
bearerToken = twitter_Bearer_Token
client = tweepy.Client(bearer_token = bearerToken)
# The search term used when searching tweets "lang:en" ensures the language is english.
search = "AMD  lang:en"

# Used to determine the time period in which to retrive tweets
start =dt.datetime.now(timezone.utc) - dt.timedelta(days=1)
end = dt.datetime.now(timezone.utc) - dt.timedelta(seconds=15)

# Retrives tweet data using the query terms.
tweets = client.search_recent_tweets(
    query = search,
    start_time = start,
    end_time = end,
    # Only takes relivant feilds from tweet_fields and user_fields.
    tweet_fields = ["created_at", "text", "source"],
    user_fields = ["name", "username", "location", "verified", "description"],
    max_results = 100,
    expansions = "author_id"
)

tweetsInfoLS = []
# Sorts through the data retrived data to format it into dictionaries and append that to a list
for tweet, user in zip(tweets.data, tweets.includes["users"]):
    tweetInfo = {
        'created_at': tweet.created_at,
        'text': tweet.text,
        'source': tweet.source,
        'name': user.name,
        'username': user.username,
        'location': user.location,
        'verified': user.verified,
        'description': user.description
    }

    tweetsInfoLS.append(tweetInfo)
#Craetes a pandas data frame of the data
tweetDF = pd.DataFrame(tweetsInfoLS)

# Function that cleans the tweet body as to make sentiment analysis better.
def cleanText(text):
    #Specifies the unicode for emojies.
    emojiPatterns = re.compile("[" u"\U0001F600-\U0001F64F" u"\U0001F300-\U0001F5FF" u"\U0001F680-\U0001F6FF" u"\U0001F1E0-\U0001F1FF" "]+", flags=re.UNICODE)
    # Removes @mentions, '#' symbols, RTs and, hyperlinks from the text given and returns it.
    text = re.sub(r'@[A-Za-z0-9]+', '', text)
    text = re.sub(r'#', '', text)
    text = re.sub(r'RT[\s]+', '', text)
    text = re.sub(r'https?:\/\/\S+', '', text)
    text = emojiPatterns.sub(r'', text)

    return text
# initialises the sentiment analysis tool and the function that uses text given to return compound sentiment score.
vader = SentimentIntensityAnalyzer()
f = lambda text: vader.polarity_scores(text)["compound"]
# Iterates through the rows in the database and runs the functions on the text column.
compound = []
for index, row in tweetDF.iterrows():
    cleanedText = cleanText(row["text"])
    # sets the cleaned text to the main text before getting text sentiment.
    tweetDF.at[index, "text"] = cleanedText
    compound.append(f(cleanedText))

# Adds the new sentiment column
tweetDF["Compound"] = compound

print(tweetDF)