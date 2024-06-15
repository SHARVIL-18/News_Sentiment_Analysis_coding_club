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
            messages.error(request, "There Was An Error Logging In, Please Try Again...")
            return redirect('home')

    else:
        query = request.GET.get('query')
        results = []
        if query:
            query = query.replace(" ", "+")
            link = f"https://news.google.com/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
            req = Request(link, headers={'User-Agent': 'Mozilla/5.0'})
            webpage = urlopen(req).read()
            soup = BeautifulSoup(webpage, 'html5lib')

            articles = []
            linkset = set()
            for link in soup.find_all('a'):
                link_str = str(link.get('href'))
                if len(linkset) >= 10:
                    break
                try:
                    if link_str.startswith("./articles"):
                        if link_str in linkset:
                            continue
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
                        linkset.add(link_str)
                except Exception as e:
                    print(f"Error processing article at {link_str}: {e}")
                    continue

            if articles:
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

                results = df.to_dict('records')
                print(results)
            else:
                print("No articles found.")
                messages.warning(request, "No articles found for the query.")
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
