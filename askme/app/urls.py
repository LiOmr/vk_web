from django.urls import path

from app import views

urlpatterns = [
    path('', views.index, name='index'),
    path('hot/', views.hot, name='hot'),
    path('questions/<int:question_id>/', views.question, name='question'),
    path('login/', views.log_in, name='login'),
    path('signup/', views.signup, name='signup'),
    path('ask/', views.ask, name='ask'),
    path('logout/', views.log_out, name='logout'),
    path('tag/<str:tag_name>/', views.tag, name='tag'),
    path('vote/', views.vote, name='vote'),
    path('answer/correct', views.correct, name='correct'),
    path('settings/', views.settings, name='settings')

]
