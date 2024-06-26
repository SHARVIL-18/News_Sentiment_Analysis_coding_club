from django.urls import path
from core import views

urlpatterns = [
    path('', views.home, name='home'),
   # path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),
    path('addbookmark/', views.addbookmark, name='addbookmark'),
    path('bookmarks/', views.bookmarks, name='bookmarks'),
]
