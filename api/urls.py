from django.urls import path
from . import views


urlpatterns = [
    path('posts/', views.PostsView.as_view()),
    path('profile/',views.ProfileView.as_view()),
    path('connections/',views.ConnectionsView.as_view()),
    path('user/',views.UserView.as_view()),
]
