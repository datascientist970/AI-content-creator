from django.contrib import admin
from .models import ContentIdea, GeneratedContent, ContentCalendar, QualityCheck

@admin.register(ContentIdea)
class ContentIdeaAdmin(admin.ModelAdmin):
    list_display = ('title', 'topic', 'category', 'platform', 'created_at', 'is_used')
    list_filter = ('category', 'platform', 'tone', 'created_at')
    search_fields = ('title', 'topic', 'angle')
    date_hierarchy = 'created_at'
    actions = ['mark_as_used']

    def mark_as_used(self, request, queryset):
        queryset.update(is_used=True)
    mark_as_used.short_description = "Mark selected ideas as used"

@admin.register(GeneratedContent)
class GeneratedContentAdmin(admin.ModelAdmin):
    list_display = ('idea', 'word_count', 'quality_score', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('caption', 'idea__title')
    date_hierarchy = 'created_at'
    actions = ['approve_content', 'reject_content']

    def approve_content(self, request, queryset):
        queryset.update(status='approved')
    approve_content.short_description = "Approve selected content"

    def reject_content(self, request, queryset):
        queryset.update(status='rejected')
    reject_content.short_description = "Reject selected content"

@admin.register(ContentCalendar)
class ContentCalendarAdmin(admin.ModelAdmin):
    list_display = ('content', 'scheduled_date', 'scheduled_time', 'platform', 'is_posted')
    list_filter = ('platform', 'is_posted', 'scheduled_date')
    date_hierarchy = 'scheduled_date'

@admin.register(QualityCheck)
class QualityCheckAdmin(admin.ModelAdmin):
    list_display = ('content', 'check_type', 'score', 'checked_at')
    list_filter = ('check_type', 'checked_at')
    date_hierarchy = 'checked_at'