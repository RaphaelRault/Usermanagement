from typing import ValuesView
from django.urls import path 

from . import views

urlpatterns = [
    path('', views.index, name = 'home'),
    path('profile/<int:user_id>/', views.profile, name='profile'),
    path('login/', views.login_user, name = 'login'),
    path('register/', views.register_user, name = 'register'),
    path('logout/', views.logout_user, name = 'logout'),
    path('send_friend_request/<int:receiver_id>/', views.send_friend_request, name='send_friend_request'),    path('accept_friend_request/<int:request_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('accept_friend_request/<int:request_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('decline_friend_request/<int:request_id>/', views.decline_friend_request, name='decline_friend_request'),
    path('profile/', views.profile, name='profile'), 
]
