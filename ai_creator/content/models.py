from django.db import models
from django.utils import timezone
import json

class ContentIdea(models.Model):
    CATEGORY_CHOICES = [
        ('tips', 'Tips & Tricks'),
        ('case_study', 'Case Study'),
        ('news', 'Industry News'),
        ('how_to', 'How-To Guide'),
        ('inspirational', 'Inspirational'),
        ('trending', 'Trending Topic'),
    ]
    
    PLATFORM_CHOICES = [
        ('instagram', 'Instagram'),
        ('linkedin', 'LinkedIn'),
        ('twitter', 'Twitter'),
        ('facebook', 'Facebook'),
        ('tiktok', 'TikTok'),
    ]
    
    TONE_CHOICES = [
        ('professional', 'Professional'),
        ('casual', 'Casual'),
        ('witty', 'Witty'),
        ('inspirational', 'Inspirational'),
        ('educational', 'Educational'),
    ]
    
    title = models.CharField(max_length=200)
    topic = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    tone = models.CharField(max_length=20, choices=TONE_CHOICES, default='professional')
    angle = models.TextField()
    pain_point = models.TextField(blank=True)
    target_audience = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    is_used = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']

class GeneratedContent(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('review', 'Needs Review'),
        ('approved', 'Approved'),
        ('published', 'Published'),
        ('rejected', 'Rejected'),
    ]
    
    idea = models.ForeignKey(ContentIdea, on_delete=models.CASCADE, related_name='contents')
    caption = models.TextField()
    hashtags = models.TextField(blank=True, help_text="Comma-separated hashtags")
    quality_score = models.FloatField(default=0.0)
    word_count = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(default=timezone.now)
    published_at = models.DateTimeField(null=True, blank=True)
    engagement_notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Content for: {self.idea.title}"
    
    def save(self, *args, **kwargs):
        self.word_count = len(self.caption.split())
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-created_at']

class ContentCalendar(models.Model):
    content = models.ForeignKey(GeneratedContent, on_delete=models.CASCADE, related_name='calendar_entries')
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    platform = models.CharField(max_length=20, choices=ContentIdea.PLATFORM_CHOICES)
    is_posted = models.BooleanField(default=False)
    posted_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.platform} - {self.scheduled_date}"
    
    class Meta:
        ordering = ['scheduled_date', 'scheduled_time']
        unique_together = ['scheduled_date', 'scheduled_time', 'platform']

class QualityCheck(models.Model):
    content = models.ForeignKey(GeneratedContent, on_delete=models.CASCADE, related_name='quality_checks')
    check_type = models.CharField(max_length=50)
    score = models.FloatField()
    issues = models.TextField(blank=True)
    suggestions = models.TextField(blank=True)
    checked_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Quality check for {self.content.id} - {self.score}"