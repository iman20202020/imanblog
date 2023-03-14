from django.contrib import admin
from django_unique_slugify import unique_slugify

from blog.models import Post, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'author', 'publish', 'status']
    list_filter = ['status', 'created', 'publish', 'author']
    search_fields = ['title', 'body']
    # prepopulated_fields = {'slug': unique_slugify('title',)}
    raw_id_fields = ['author']
    date_hierarchy = 'publish'
    ordering = ['status', 'publish']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['post_id', 'user_id', 'updated', 'active']
    list_filter = [ 'active', 'updated']
    ordering = ['-updated']