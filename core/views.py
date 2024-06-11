import requests
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import pandas as pd
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from newspaper import Article
from core.models import NewsCard
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import SignUpForm


# Run these once
# nltk.download('punkt')
# nltk.download('stopwords')
# nltk.download('wordnet')
# nltk.download('vader_lexicon')

def home(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        # Authenticate
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You Have Been Logged In!")
            return redirect('home')
        else:
            messages.success(request, "There Was An Error Logging In, Please Try Again...")
            return redirect('home')

    else:

        query = request.GET.get('query')
        results = []
        if query:
            query = query.replace(" ", "+")
            link = f"https://news.google.com/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
            # link = f"https://www.google.com/search?lr=lang_en&q={query}&sca_esv=7b1f93cccdc9738a&sca_upv=1&rlz=1C1UEAD_enIN1066IN1066&biw=1536&bih=398&tbm=nws&sxsrf=ADLYWILa2YTPLYepGsgLG385nFveSa_kmQ%3A1716828649665&ei=6blUZoWfKM2gseMP7qqZgAc&ved=0ahUKEwjFt7aOpa6GAxVNUGwGHW5VBnAQ4dUDCA0&uact=5&oq=bjp&gs_lp=Egxnd3Mtd2l6LW5ld3MiA2JqcDIREAAYgAQYkQIYsQMYgwEYigUyCxAAGIAEGLEDGIMBMggQABiABBixAzIKEAAYgAQYQxiKBTIKEAAYgAQYQxiKBTILEAAYgAQYsQMYgwEyCxAAGIAEGLEDGIMBMgoQABiABBhDGIoFMggQABiABBixAzIIEAAYgAQYsQNI8YgBUNOAAVj1hQFwAHgAkAEAmAH1AaAB3wWqAQUwLjIuMrgBA8gBAPgBAZgCBKAChgbCAgQQABgDwgIOEAAYgAQYkQIYsQMYigXCAg4QABiABBixAxiDARiKBcICEBAAGIAEGLEDGEMYgwEYigWYAwCIBgGSBwUwLjIuMqAHuhU&sclient=gws-wiz-news"
            req = Request(link, headers={'User-Agent': 'Mozilla/5.0'})
            webpage = urlopen(req).read()
            soup = BeautifulSoup(webpage, 'html5lib')

            articles = []
            cnt = 15
            for link in soup.find_all('a', limit=25):
                link_str = str(link.get('href'))
                # link_split = (link_str.split("/url?q="))
                # if len(link_split) == 2:
                #     link_str = link_split[1].split('&sa=U&')[0]
                if cnt == 0:
                    break
                try:
                    # if link_str.startswith(
                    #         "https://") and 'google.com' not in link_str and 'youtube.com' not in link_str and 'blogger.com' not in link_str:
                    if link_str.startswith("./articles"):
                        article = Article("https://news.google.com/" + link_str)
                        article.download()
                        article.parse()

                        if not article.title or not article.text:
                            continue
                        new_article = {
                            "link": "https://news.google.com/" + link_str,
                            "title": article.title,
                            "text": article.text
                        }

                        articles.append(new_article)
                        cnt = cnt - 1
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

            analyzer = SentimentIntensityAnalyzer()

            def get_sentiment(text):

                scores = analyzer.polarity_scores(text)
                compound = scores['compound']
                return compound

            df['processed_title'] = df['title'].apply(preprocess_text)
            df['processed_text'] = df['text'].apply(preprocess_text)

            df['sentiment_score_title'] = df['processed_title'].apply(get_sentiment)
            df['sentiment_score_text'] = df['processed_text'].apply(get_sentiment)

            df['average_sentiment_score'] = (df['sentiment_score_title'] + df['sentiment_score_text']) / 2
            # In your view, update the code to use the new get_sentiment function
            #        df['sentiment_title'], df['sentiment_score'] = zip(*df['processed_title'].apply(get_sentiment))
            #       df['sentiment_text'], _ = zip(*df['text'].apply(get_sentiment))

            #     df['sentiment_title'], df['sentiment_score_title'] = zip(*df['processed_title'].apply(get_sentiment))
            #    # df['sentiment_text'], df['sentiment_score_text'] = zip(*df['text'].apply(get_sentiment))
            #     _, df['sentiment_score_text'] = zip(*df['text'].apply(get_sentiment))

            #   df['sentiment_title'] = df['processed_title'].apply(get_sentiment)
            #    df['sentiment_text'] = df['text'].apply(get_sentiment)

            # Convert DataFrame to list of dictionaries
            results = df.to_dict('records')
            print(results)
        # Pass the data to the template
        return render(request, 'core/home.html', {'results': results})


def login_user(request):
    pass


def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out..")
    return redirect('home')
    pass


def register_user(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            # Authenticate and login
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, "You Have Successfully Registered! Welcome!")
            return redirect('home')
    else:
        form = SignUpForm()
        return render(request, 'core/register.html', {'form': form})

    return render(request, 'core/register.html', {'form': form})


@login_required
def addbookmark(request):
    if request.method == 'GET':
        title = request.GET.get('title')
        text = request.GET.get('text')
        link = request.GET.get('link')
        user = request.user

        if title and text and link:
            newscard = NewsCard(title=title, text=text, link=link, user=user)
            newscard.save()
            return JsonResponse({'message': 'Bookmark Added!'}, status=200)
        else:
            return JsonResponse({'message': 'Failed to add bookmark. Missing data.'}, status=400)
    return JsonResponse({'message': 'Invalid request.'}, status=400)


@login_required
def bookmarks(request):
    user_bookmarks = NewsCard.objects.filter(user=request.user)
    return render(request, 'core/bookmarks.html', {'bookmarks': user_bookmarks})
