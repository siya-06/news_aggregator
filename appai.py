import requests
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from textblob import TextBlob
from flask import Flask, render_template, request

import nltk
nltk.download('stopwords')
nltk.download('punkt')

# Fetch news articles from a given URL
def fetch_news(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    articles = soup.find_all('article')

    news_data = []
    for article in articles:
        title = article.find('h2').get_text() if article.find('h2') else 'No title'
        summary = article.find('p').get_text() if article.find('p') else 'No summary'
        link = article.find('a')['href'] if article.find('a') else '#'
        news_data.append({'title': title, 'summary': summary, 'link': link})

    return news_data

# Summarize the text
def summarize_text(text):
    stop_words = set(stopwords.words('english'))
    word_tokens = word_tokenize(text)
    filtered_sentence = [w for w in word_tokens if not w.lower() in stop_words]

    blob = TextBlob(" ".join(filtered_sentence))
    summary = " ".join(blob.words[:50])  # Simple summary by taking the first 50 words
    return summary

# Analyze sentiment of the text
def analyze_sentiment(text):
    blob = TextBlob(text)
    sentiment_score = blob.sentiment.polarity
    if sentiment_score > 0:
        return 'Positive'
    elif sentiment_score < 0:
        return 'Negative'
    else:
        return 'Neutral'

# Categorize the news based on keywords
def categorize_news(text):
    text_lower = text.lower()
    if 'stock' in text_lower:
        return 'Stock Market'
    elif 'economy' in text_lower:
        return 'Economy'
    elif 'crypto' in text_lower:
        return 'Cryptocurrency'
    else:
        return 'General'

# Determine the overall market mood based on the sentiment analysis
def market_mood(news_data):
    sentiment_counts = {'Positive': 0, 'Neutral': 0, 'Negative': 0}

    for news in news_data:
        sentiment = analyze_sentiment(news['summary'])
        sentiment_counts[sentiment] += 1

    if sentiment_counts['Positive'] > sentiment_counts['Negative']:
        return 'Market Mood: Positive'
    elif sentiment_counts['Negative'] > sentiment_counts['Positive']:
        return 'Market Mood: Negative'
    else:
        return 'Market Mood: Neutral'

# Initialize Flask app
app = Flask(name)

@app.route('/')
def home():
    news_url = 'https://www.example.com/financial-news'  # Replace with an actual news URL
    news_data = fetch_news(news_url)

    for news in news_data:
        news['summary'] = summarize_text(news['summary'])
        news['sentiment'] = analyze_sentiment(news['summary'])
        news['category'] = categorize_news(news['summary'])

    mood = market_mood(news_data)

    return render_template('index.html', news_data=news_data, mood=mood)

@app.route('/command', methods=['POST'])
def command():
    command = request.form['command']
    response = f"Command '{command}' received and processed."
    return render_template('index.html', response=response)

if name == 'main':
    app.run(debug=True)