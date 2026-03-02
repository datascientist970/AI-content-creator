from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('generate-ideas/', views.generate_ideas, name='generate_ideas'),
    path('generate-caption/', views.generate_caption, name='generate_caption_no_idea'),
    path('generate-caption/<int:idea_id>/', views.generate_caption, name='generate_caption'),
    path('content/<int:content_id>/', views.content_detail, name='content_detail'),
    path('calendar/', views.calendar_view, name='calendar_view'),
    path('schedule/<int:content_id>/', views.schedule_content, name='schedule_content'),
    path('saved-content/', views.saved_content, name='saved_content'),
    path('api/generate-caption/', views.api_generate_caption, name='api_generate_caption'),
]