import math
import markdown
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.utils.html import strip_tags


class PublishedManager(models.Manager):
    """Custom manager to get published articles"""
    def get_queryset(self):
        return super().get_queryset().filter(
            status=Article.Status.PUBLISHED
        ).order_by('-published_at')


class Article(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DF", "Draft"
        PUBLISHED = "PB", "Published"
    
    title = models.CharField(max_length=256)
    slug = models.SlugField(max_length=256, unique=True)
    body = models.TextField(help_text="Markdown supported")
    status = models.CharField(
        max_length=2,
        choices=Status,
        default=Status.DRAFT
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    objects = models.Manager()
    published = PublishedManager()
    
    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Article"
        verbose_name_plural = "Articles"
        indexes = [
            models.Index(fields=["-published_at"]),
            models.Index(fields=["slug"]),
            models.Index(fields=["status"]),
            models.Index(fields=["status", "-published_at"]),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # generate slug from title if not provided
        if not self.slug:
            self.slug = slugify(self.title)
        
        # set published_at when status changes to published
        if self.status == self.Status.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    def get_body_html(self):
        """Convert markdown body to HTML"""
        clean_body = self.body.strip()
        return markdown.markdown(
            clean_body,
            extensions=['extra', 'codehilite', 'fenced_code', 'nl2br']
        )
    
    def get_word_count(self):
        """Calculate word count from body"""
        html_content = markdown.markdown(self.body)
        plain_text = strip_tags(html_content)
        words = plain_text.split()

        return len(words)
    
    def get_reading_time(self, words_per_minute=200):
        """Estimate reading time in minutes"""
        word_count = self.get_word_count()
        reading_time = math.ceil(word_count / words_per_minute)

        return max(reading_time, 1)


class Comment(models.Model):
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    nickname = models.CharField(max_length=64)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
        indexes = [
            models.Index(fields=["article", "created_at"])
        ]

    def __str__(self):
        return f"Comment by {self.nickname} on {self.article.title}"
