from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('user/profile/', views.user_profile, name='user_profile'),
    path('user/contributions/', views.user_contributions, name='user_contributions'),
    path('wiki/search/', views.wiki_search, name='wiki_search'),
    path('wiki/statistics/', views.wiki_statistics, name='wiki_statistics'),
]
