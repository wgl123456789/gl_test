from django.urls import path
from . import views

app_name = 'zlauth'
urlpatterns = [
    path('',views.View.as_view(),name=''),
    path('user',views.UserView.as_view(),name='user'),
    path('avatar',views.AvatarUploadView.as_view(),name='avatar')
]