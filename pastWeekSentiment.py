import requests
import datetime as dt
import pandas as pd
from secrets import Alpha_Vantage_Key

# Sets and formattes the correct date to use for the url.
timeFrom = dt.datetime.now() - dt.timedelta(days=7)
formattedDate = timeFrom.strftime("%Y%m%dT%H%M")

symbol = "EVFM"

url = f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={symbol}&time_from={formattedDate}&apikey={Alpha_Vantage_Key}'
# Requests the data from the alphavantage api
response = requests.get(url)
data = response.json()
tickerInfoList = []
#  Loops through the feed in the recived data and correctly formattes it into a list
for feed in data["feed"]:
    title = feed["title"]
    url = feed["url"]
    publishDate = feed["time_published"]
    # The data hold sentiment for all tickers in the article this retrives only the sentiment for the wanted ticker.
    for ticker in feed["ticker_sentiment"]:
        if(ticker["ticker"] == symbol):
            tickerSentiment = ticker

    tickerInfo = {
        "Title": title,
        "URL": url,
        "Publish Date": publishDate,
        "Ticker Sentiment": tickerSentiment
    }
    
    tickerInfoList.append(tickerInfo)

# Creates the data frame using the list of dictionaries
df = pd.DataFrame(tickerInfoList)

# Relevance score is also held with the ticker sentiment. This loops through all the indexes and removes articles that your ticker relevence score is below 0.1.
for index, row in df.iterrows():
    if(float(row["Ticker Sentiment"]["relevance_score"]) < 0.1):
        df = df.drop(index = index)

dateLst = []
timeLst = []
sentimentLst = []
# Loops thorugh all the items in the data frame taking the date variable and formatting it as alphavantage returns a differently formatted date to the datetime library.
for index, row in df.iterrows():
    datetime = row["Publish Date"]
    # Takes a certain number of char's in the publish date column and sets it to the right variable name. Then formates both the date and the time.
    year, month, day, hour, minute, second = datetime[0:4], datetime[4:6], datetime[6:8], datetime[9:11], datetime[11:13], datetime[13:15]
    date = f"{year}-{month}-{day}"
    time = f"{hour}:{minute}:{second}"

    sentiment = row["Ticker Sentiment"]["ticker_sentiment_score"]

    dateLst.append(date)
    timeLst.append(time)
    sentimentLst.append(float(sentiment))

relevantData = {
    "Date": dateLst,
    #"Time": timeLst,
    "Sentiment": sentimentLst
}
# A new dictionary is created using only the formatted date and the sentiment scores to make it easier to view
newDF = pd.DataFrame(relevantData)
newDF["Date"] = pd.to_datetime(newDF.Date).dt.date
# The rows in the data frame are grouped by the date, and the mean of the sentiment score is calculated 
# as more then one article can be published for that day and we only care about the entire day sentiment.
formattedDF = newDF.groupby("Date").mean()
# Convertes the data frame to a json and uses the correct date format.
formattedDFJson = formattedDF.to_json(date_format="iso")
print(formattedDFJson)