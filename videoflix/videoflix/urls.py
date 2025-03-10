"""
URL configuration for videoflix project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import include
from django.conf import settings
from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


from movie.api.views import ConnectionTestView, MovieView, MovieConvertablesView, SingleMovieConvertablesView, MovieProgressView
from userprofile.api.views import LoginOrSignupView, LoginView, RegisterView, VerificationView, PasswordResetInquiryView, PasswordReset

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/login-signup/', LoginOrSignupView.as_view(), name='login-signup'),
    path('api/login/', LoginView.as_view(), name='login'),

    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/verification/', VerificationView.as_view(), name='verification'),
    path('api/password-reset-inquiry/', PasswordResetInquiryView.as_view(), name='password-reset-inquiry'),
    path('api/password-reset/', PasswordReset.as_view(), name='password-reset'),


    path('api/movies/', MovieView.as_view(), name='movies'),
    path('api/connection/', ConnectionTestView.as_view(), name='connection'),
    path('api/movies-convert/', MovieConvertablesView.as_view(), name='movies-convert'),
    path('api/movie-convert/<int:pk>', SingleMovieConvertablesView.as_view(), name='movie-convert'),

    path('api/movie-progress/<int:pk>', MovieProgressView.as_view(), name='movie-progress')

] + debug_toolbar_urls()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()

