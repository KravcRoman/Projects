from django.urls import path
from . import views

urlpatterns = [
    path('', views.article_list, name='article_list'),
    path('create/', views.create_article, name='create_article'),
    path('<int:pk>/', views.article_detail, name='article_detail'),
]

# http://127.0.0.1:8000/
# http://127.0.0.1:8000/create/
# http://127.0.0.1:8000/1/