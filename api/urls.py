from django.urls import path
from . import views


urlpatterns = [
    path('posts/', views.PostsView.as_view()),
    path('profile/<str:username>',views.ProfileView.as_view()),
    path('connections/',views.ConnectionsView.as_view()),
    path('user/',views.UserView.as_view()),
    path('feed/', views.FeedView.as_view()),
    path('search/<str:term>',views.SearchView.as_view()),
    path('search/',views.SearchView.as_view()),
    path('requests/',views.ConnectionRequests.as_view()),
]
