"""yasblog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
import django.contrib.sitemaps.views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include

from blog import views
from blog.sitemaps import PostSitemap
from blog.views import PostDetailView

sitemaps = {'posts': PostSitemap, }


urlpatterns = [
    path("admin/", admin.site.urls),
    path('blog/', include('blog.urls', namespace='blog')),
    path('account/', include('account.urls', namespace='account')),
    # path(r'^hitcount-detail-view-count-hit/(?P<pk>\d+)/$', views.PostCountHitDetailView.as_view(), name="detail-with-count"),
    path('<slug:slug>/', PostDetailView.as_view(), name='detail'),
    path('hitcount/', include(('hitcount.urls', 'hitcount'), namespace='hitcount')),
    path('sitemaps.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap')
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
