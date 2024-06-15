# News_Sentiment_Analysis_coding_club

The website is live at :
```http://shadow09.pythonanywhere.com/```


The project is based on using nltk library to do sentiment analysis on news articles and classify them as positive, negative or neutral. 
It involves using Beautiful Soup and Request libraries for web scraping of the latest news articles from news.google.com 

The web framework is built using Django. The user can create and account and request for classified news, and also bookmark specific news articles. 

Website Usage :
1) Create an account if user doesnt have one or login if it already exist
2) Enter keywords of the items the user is interested in. 
3) Let the website load... (the wait is about 20-30 seconds)
4) You will see a listing of news articles in classified sense, clicking on add bookmark saves the article in the database and can be viewed in "My Bookmarks".


To run the project locally:
1) Clone the repository
2) install requirements using pip install -r requirements.txt
3) install the nltk requirements commented in /final_project/views.py
4) Finally run the command :
```py  manage.py runserver```
