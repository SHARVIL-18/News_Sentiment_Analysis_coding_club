import requests
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import pandas as pd
from newspaper import Article
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from django.shortcuts import render


# Run these once
# nltk.download('punkt')
# nltk.download('stopwords')
# nltk.download('wordnet')
# nltk.download('vader_lexicon')

def home(request):
    query = request.GET.get('query')
    results = []
    if query:
        query = query.replace(" ", "+")
        link = f"https://www.google.com/search?q={query}&sca_esv=7b1f93cccdc9738a&sca_upv=1&rlz=1C1UEAD_enIN1066IN1066&biw=1536&bih=398&tbm=nws&sxsrf=ADLYWILa2YTPLYepGsgLG385nFveSa_kmQ%3A1716828649665&ei=6blUZoWfKM2gseMP7qqZgAc&ved=0ahUKEwjFt7aOpa6GAxVNUGwGHW5VBnAQ4dUDCA0&uact=5&oq=bjp&gs_lp=Egxnd3Mtd2l6LW5ld3MiA2JqcDIREAAYgAQYkQIYsQMYgwEYigUyCxAAGIAEGLEDGIMBMggQABiABBixAzIKEAAYgAQYQxiKBTIKEAAYgAQYQxiKBTILEAAYgAQYsQMYgwEyCxAAGIAEGLEDGIMBMgoQABiABBhDGIoFMggQABiABBixAzIIEAAYgAQYsQNI8YgBUNOAAVj1hQFwAHgAkAEAmAH1AaAB3wWqAQUwLjIuMrgBA8gBAPgBAZgCBKAChgbCAgQQABgDwgIOEAAYgAQYkQIYsQMYigXCAg4QABiABBixAxiDARiKBcICEBAAGIAEGLEDGEMYgwEYigWYAwCIBgGSBwUwLjIuMqAHuhU&sclient=gws-wiz-news"
        req = Request(link, headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()
        soup = BeautifulSoup(webpage, 'html5lib')

        articles = []

        for link in soup.find_all('a'):
            link_str = str(link.get('href'))
            link_split = (link_str.split("/url?q="))
            if len(link_split) == 2:
                link_str = link_split[1].split('&sa=U&')[0]

            try:
                if link_str.startswith(
                        "https://") and 'google.com' not in link_str and 'youtube.com' not in link_str and 'blogger.com' not in link_str:
                    article = Article(link_str)
                    article.download()
                    article.parse()

                    new_article = {
                        "link": link_str,
                        "title": article.title,
                        "text": article.text
                    }

                    articles.append(new_article)
            except Exception as e:
                print(f"Error processing article at {link_str}: {e}")
                continue

        df = pd.DataFrame(articles)

        def preprocess_text(text):
            tokens = word_tokenize(text.lower())
            filtered_tokens = [token for token in tokens if token not in stopwords.words('english')]
            lemmatizer = WordNetLemmatizer()
            lemmatized_tokens = [lemmatizer.lemmatize(token) for token in filtered_tokens]
            processed_text = ' '.join(lemmatized_tokens)
            return processed_text

        df['processed_title'] = df['title'].apply(preprocess_text)

        analyzer = SentimentIntensityAnalyzer()

        def get_sentiment(text):
            
            scores = analyzer.polarity_scores(text)
            compound = scores['compound']
            if compound >= 0.05:
                sentiment = 'positive'
            elif compound <= -0.05:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            return sentiment, compound

# In your view, update the code to use the new get_sentiment function
#        df['sentiment_title'], df['sentiment_score'] = zip(*df['processed_title'].apply(get_sentiment))
 #       df['sentiment_text'], _ = zip(*df['text'].apply(get_sentiment))

        df['sentiment_title'], df['sentiment_score_title'] = zip(*df['processed_title'].apply(get_sentiment))
       # df['sentiment_text'], df['sentiment_score_text'] = zip(*df['text'].apply(get_sentiment))
        _, df['sentiment_score_text'] = zip(*df['text'].apply(get_sentiment))

     #   df['sentiment_title'] = df['processed_title'].apply(get_sentiment)
    #    df['sentiment_text'] = df['text'].apply(get_sentiment)

        # Convert DataFrame to list of dictionaries
        results = df.to_dict('records')

    # Pass the data to the template
    return render(request, 'core/home.html', {'results': results})
