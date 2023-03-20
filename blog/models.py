from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django_unique_slugify import unique_slugify
from hitcount.models import HitCount
from hitcount.settings import MODEL_HITCOUNT
from taggit.managers import TaggableManager
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
from hitcount.models import HitCountMixin


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Post.Status.PUBLISHED)


class Post(models.Model, HitCountMixin):
    class Status(models.TextChoices):
        DRAFT = 'DF', 'Draft'
        PUBLISHED = 'PB', 'Published'

    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=300, unique_for_date='publish',  blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='blog_posts', on_delete=models.CASCADE)
    author_name = models.CharField(max_length=100,)
    body = models.TextField()
    image = ProcessedImageField(upload_to='blog/%Y/%m/%d/', blank=True, null=True, processors=[ResizeToFill(300, 225)],
                                format='JPEG', options={'quality': 60})
    publish = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.DRAFT)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    objects = models.Manager()
    published = PublishedManager()
    tags = TaggableManager()
    hit_count_generic = GenericRelation(
        MODEL_HITCOUNT, object_id_field='object_pk',
        related_query_name='hit_count_generic_relation')
    users_like = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='posts_liked', blank=True)

    class Meta:
        ordering = ['-publish', 'hit_count_generic__hits']
        indexes = [models.Index(fields=['-publish']), ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post_detail', args=[self.slug])

    def save(self, *args, **kwargs):
        unique_slugify(self, self.title)
        super().save(*args, **kwargs)


class Comment(models.Model):
    user = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=80)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=False)
    contact = models.ManyToManyField('self', through='CommentContact', related_name='comment_comments', symmetrical=False)

    class Meta:
        ordering = ['created']

    indexes = [
        models.Index(fields=['created']),
    ]

    def __str__(self):
        return f'Comment by {self.name} on {self.post}'


class CommentContact(models.Model):
    comment_from = models.ForeignKey(Comment, related_name='rel_from', on_delete=models.CASCADE)
    comment_to = models.ForeignKey(Comment, related_name='rel_to', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['-created']),
        ]
    ordering = ['-created']


