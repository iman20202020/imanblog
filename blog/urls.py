from django.urls import path

from blog import views

app_name = 'blog'

urlpatterns = [
    # get post_list without tag filter
    path('', views.post_list, name='post_list'),
    # get post_list filtered by tag
    path('tag/<slug:tag_slug>/', views.post_list, name='post_list_by_tag'),
    # post detail
    # path('<int:year>/<int:month>/<int:day>/<slug:post>/', views.post_detail, name='post_detail'),
    # create a new post
    path('create/', views.post_create, name='post_create'),
    path('comment/<int:post_id>/<int:comment_id>/', views.comment_comment, name='comment_comment'),
    path('search/', views.post_search, name='post_search'),
    path('like/', views.post_like, name='post_like'),



]
