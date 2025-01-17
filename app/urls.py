from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='home'), 
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('add_article/', views.add_article, name='add_article'),
    path('delete_article/<int:article_id>/', views.delete_article, name='delete_article'),
]
