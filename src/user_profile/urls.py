from django.urls import path, include
from user_profile import views

urlpatterns = [
    path('profile', views.profile, name='profile'),
    path('search', views.search, name='search'),
    path('statistics', views.statistics, name='statistics'),
    path('set-language', views.set_language, name='set_language'),
    path('accounts/login', views.login_oauth, name='login'),
    path('oauth/', include('social_django.urls', namespace='social')),
    path('', views.index),
]
