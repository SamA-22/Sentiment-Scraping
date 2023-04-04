import datetime as dt
import requests
import pandas as pd
import time
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from secrets import X_RapidAPI_Key

# Creates the correct url for the finviz website depending on the stock you want.
finvizUrl = 'https://finviz.com/quote.ashx?t='
stock = "AMD"
url = finvizUrl + stock

# Initialises a request object and opens it.
req = Request(url = url, headers = {"user-agent": "my-app"})
response = urlopen(req)

# Initialises a beautiful soup so that certain feilds can be found ie: the news table
html = BeautifulSoup(response, features = "html.parser")
newsTable = html.find(id = "news-table")

parsedData = []
# Sorts through the table rows, and grabs the nessicary data, appending it to a list variable
for row in newsTable.findAll("tr"):
    title = row.a.text
    dateData = row.td.text.split(" ")
    url = row.a["href"]

    if len(dateData) == 1:
        articleTime = dateData[0]
    else:
        date = dateData[0]
        articleTime = dateData[1]
    # None field is added so sentiemnt will later overwrite it.
    parsedData.append([title, date, articleTime, url, None])

# Creates the pandas dataframe using the acumulated data and the correct column names.
df = pd.DataFrame(parsedData, columns = ["Title", "Date", "Time", "URL", "Compound"])
df["Date"] = pd.to_datetime(df["Date"])

# Iterates through the data frame to filter out any news articles that were made more than two days ago.
for index, row in df.iterrows():
    if(row["Date"] < dt.datetime.today() - dt.timedelta(days=2)):
        df = df.drop(index, axis=0)

# Initialises the sentiment analysis tool and the function that uses text given to return compound sentiment score.
vader = SentimentIntensityAnalyzer()
f = lambda text: vader.polarity_scores(text)["compound"]

# Sets up correct url and headers for the web search api that will be used to get the news text from the links on finviz.
webSearchAPI = "https://rapidapi.p.rapidapi.com/api/Search/WebSearchAPI"

headerData = {
    "X-RapidAPI-Key": X_RapidAPI_Key,
    "X-RapidAPI-Host": "contextualwebsearch-websearch-v1.p.rapidapi.com"
}

# Iterates through each of the urls in the dataframe and uses the api to query the link.
for index, row in df.iterrows():
    querystring = {
        "q": row["URL"],
        "pageNumber":"1",
        "pageSize":"1",
        "autoCorrect":"false",
        "safeSearch": "false",
    }

    response = requests.get(webSearchAPI, headers = headerData, params = querystring).json()
    # Lots of data can be obtained by the api call however only the body is being used as that is where the text is.
    for webPage in response["value"]:
        url = webPage["url"]
        title = webPage["title"]
        description = webPage["description"]
        body = webPage["body"]
        datePublished = webPage["datePublished"]
        language = webPage["language"]
        isSafe = webPage["isSafe"]
        provider = webPage["provider"]["name"]

    # Sentiment analysis is conducted on the body text and the sentiment score for that row is updated
    df.at[index, "Compound"] = f(body)
    # One sceond intervals are needed between each loop as the api can only handle a certain number of calls per second.
    time.sleep(1)

print(df) 