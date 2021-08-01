"""dcs1 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from dcs1.DCS1 import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('uploader/<str:section>/<str:file>',views.DataReceiver.as_view(),name="uploader"),
    path('reader/',views.FileParser.as_view(),name="reader"),
    path('',views.SearchDB.as_view(),name="index"),
    path('uploader2/',views.DataReciever_viewable.as_view(),name="uploader2"),
    path('search/',views.SearchDB.as_view(),name="search"),
]
