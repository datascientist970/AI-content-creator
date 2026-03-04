from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
import json

from .models import ContentIdea, GeneratedContent, ContentCalendar, QualityCheck
from .forms import ContentIdeaForm, CaptionForm, CalendarFilterForm
from .utils import GeminiContentGenerator

# Home View
def index(request):
    """Home page view"""
    context = {
        'total_ideas': ContentIdea.objects.count(),
        'total_captions': GeneratedContent.objects.count(),
        'published_count': GeneratedContent.objects.filter(status='published').count(),
        'recent_ideas': ContentIdea.objects.all()[:5],
        'upcoming_posts': ContentCalendar.objects.filter(
            scheduled_date__gte=timezone.now().date(),
            is_posted=False
        )[:5]
    }
    return render(request, 'content/index.html', context)

# Generate Ideas View
def generate_ideas(request):
    """Generate content ideas using Gemini"""
    if request.method == 'POST':
        form = ContentIdeaForm(request.POST)
        if form.is_valid():
            # Get form data
            topic = form.cleaned_data['topic']
            niche = form.cleaned_data['niche']
            platform = form.cleaned_data['platform']
            tone = form.cleaned_data['tone']
            count = form.cleaned_data['count']
            target_audience = form.cleaned_data['target_audience']
            
            # Generate ideas using Gemini
            ideas_data = GeminiContentGenerator.generate_ideas(
                topic=topic,
                niche=niche,
                count=count,
                platform=platform,
                tone=tone,
                target_audience=target_audience
            )
            
            # Save ideas to database
            saved_ideas = []
            for idea_data in ideas_data:
                idea = ContentIdea.objects.create(
                    title=idea_data['title'],
                    topic=topic,
                    category=idea_data.get('category', 'tips'),
                    platform=idea_data.get('platform', 'linkedin'),
                    tone=tone,
                    angle=idea_data.get('angle', ''),
                    pain_point=idea_data.get('pain_point', ''),
                    target_audience=target_audience
                )
                saved_ideas.append(idea)
            
            messages.success(request, f'Successfully generated {len(saved_ideas)} content ideas!')
            
            # Store in session for potential caption generation
            request.session['last_ideas'] = [idea.id for idea in saved_ideas]
            
            return render(request, 'content/generate_ideas.html', {
                'form': form,
                'ideas': saved_ideas,
                'generated': True
            })
    else:
        form = ContentIdeaForm()
    
    return render(request, 'content/generate_ideas.html', {'form': form})

# Generate Caption View
def generate_caption(request, idea_id=None):
    """Generate caption for a content idea"""
    idea = None
    if idea_id:
        idea = get_object_or_404(ContentIdea, id=idea_id)
    
    if request.method == 'POST':
        form = CaptionForm(request.POST)
        if form.is_valid():
            idea_id = form.cleaned_data['idea_id']
            idea = get_object_or_404(ContentIdea, id=idea_id)
            
            platform = form.cleaned_data['platform']
            tone = form.cleaned_data['tone']
            additional_instructions = form.cleaned_data['additional_instructions']
            
            # Generate caption
            caption_data = GeminiContentGenerator.generate_caption(
                idea_title=idea.title,
                platform=platform,
                tone=tone,
                additional_instructions=additional_instructions
            )
            
            # Check quality
            quality_data = GeminiContentGenerator.check_quality(
                caption_data['caption'],
                platform
            )
            
            # Save generated content
            generated_content = GeneratedContent.objects.create(
                idea=idea,
                caption=caption_data['caption'],
                hashtags=caption_data['hashtags'],
                quality_score=quality_data['overall_score'] / 10,  # Convert to 0-1 scale
                status='review' if quality_data['overall_score'] < 7 else 'draft'
            )
            
            # Save quality check
            QualityCheck.objects.create(
                content=generated_content,
                check_type='initial',
                score=quality_data['overall_score'] / 10,
                issues=json.dumps(quality_data.get('issues', [])),
                suggestions=json.dumps(quality_data.get('suggestions', []))
            )
            
            messages.success(request, 'Caption generated successfully!')
            
            return redirect('content_detail', content_id=generated_content.id)
    else:
        if idea:
            form = CaptionForm(initial={
                'idea_id': idea.id,
                'topic': idea.title,
                'platform': idea.platform,
                'tone': idea.tone
            })
        else:
            # If no idea specified, show idea selection
            ideas = ContentIdea.objects.filter(is_used=False)[:10]
            return render(request, 'content/select_idea.html', {'ideas': ideas})
    
    return render(request, 'content/write_caption.html', {
        'form': form,
        'idea': idea
    })

# Content Detail View
def content_detail(request, content_id):
    content = get_object_or_404(GeneratedContent, id=content_id)
    quality_checks = content.quality_checks.all()
    
    # Process hashtags
    hashtags_list = []
    if content.hashtags:
        hashtags_list = [tag.strip() for tag in content.hashtags.split(',') if tag.strip()]
    
    # Process quality checks
    for check in quality_checks:
        if check.issues:
            try:
                check.issues_list = [issue.strip() for issue in check.issues.split(',') if issue.strip()]
            except:
                check.issues_list = []
        else:
            check.issues_list = []
            
        if check.suggestions:
            try:
                check.suggestions_list = [sugg.strip() for sugg in check.suggestions.split(',') if sugg.strip()]
            except:
                check.suggestions_list = []
        else:
            check.suggestions_list = []
    
    # Calculate values
    word_count_percentage = min(100, (content.word_count / 300) * 100) if content.word_count else 0
    
    # Calculate circle offset for quality gauge
    circumference = 2 * 3.14159 * 70  # 2πr where r=70
    quality_circle_offset = circumference - (content.quality_score * circumference)
    
    context = {
        'content': content,
        'quality_checks': quality_checks,
        'hashtags_list': hashtags_list,
        'word_count_percentage': word_count_percentage,
        'quality_circle_offset': quality_circle_offset,
        'estimated_likes': getattr(content, 'estimated_likes', 234),
        'estimated_comments': getattr(content, 'estimated_comments', 45),
    }
    
    return render(request, 'content/content_detail.html', context)

# Calendar View
def calendar_view(request):
    """View and manage content calendar"""
    form = CalendarFilterForm(request.GET or None)
    calendar_entries = ContentCalendar.objects.all()
    
    if form.is_valid():
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']
        platform = form.cleaned_data['platform']
        status = form.cleaned_data['status']
        
        if start_date:
            calendar_entries = calendar_entries.filter(scheduled_date__gte=start_date)
        if end_date:
            calendar_entries = calendar_entries.filter(scheduled_date__lte=end_date)
        if platform:
            calendar_entries = calendar_entries.filter(platform=platform)
        if status:
            calendar_entries = calendar_entries.filter(content__status=status)
    
    # Group by date for calendar display
    calendar_data = {}
    for entry in calendar_entries:
        date_str = entry.scheduled_date.strftime('%Y-%m-%d')
        if date_str not in calendar_data:
            calendar_data[date_str] = []
        calendar_data[date_str].append(entry)
    
    context = {
        'form': form,
        'calendar_data': calendar_data,
        'entries': calendar_entries[:50],  # Limit for display
    }
    return render(request, 'content/calendar.html', context)

# Schedule Content View
def schedule_content(request, content_id):
    """Schedule content for posting"""
    content = get_object_or_404(GeneratedContent, id=content_id)
    
    if request.method == 'POST':
        scheduled_date = request.POST.get('scheduled_date')
        scheduled_time = request.POST.get('scheduled_time')
        platform = request.POST.get('platform', content.idea.platform)
        notes = request.POST.get('notes', '')
        
        try:
            # Parse date and time
            date_obj = datetime.strptime(scheduled_date, '%Y-%m-%d').date()
            time_obj = datetime.strptime(scheduled_time, '%H:%M').time()
            
            # Create calendar entry
            calendar_entry = ContentCalendar.objects.create(
                content=content,
                scheduled_date=date_obj,
                scheduled_time=time_obj,
                platform=platform,
                notes=notes
            )
            
            # Update content status
            content.status = 'scheduled'
            content.save()
            
            messages.success(request, 'Content scheduled successfully!')
            return redirect('calendar_view')
            
        except Exception as e:
            messages.error(request, f'Error scheduling content: {e}')
    
    # Get platform best times for suggestions
    best_times = {
        'linkedin': '09:00',
        'instagram': '12:00',
        'twitter': '10:00',
        'facebook': '14:00',
        'tiktok': '18:00'
    }
    
    suggested_time = best_times.get(content.idea.platform, '10:00')
    tomorrow = (timezone.now() + timedelta(days=1)).date()
    
    return render(request, 'content/schedule.html', {
        'content': content,
        'suggested_date': tomorrow,
        'suggested_time': suggested_time
    })

# Saved Content View
def saved_content(request):
    """View all saved content"""
    status_filter = request.GET.get('status', '')
    platform_filter = request.GET.get('platform', '')
    
    contents = GeneratedContent.objects.select_related('idea').all()
    
    if status_filter:
        contents = contents.filter(status=status_filter)
    if platform_filter:
        contents = contents.filter(idea__platform=platform_filter)
    
    context = {
        'contents': contents,
        'status_filter': status_filter,
        'platform_filter': platform_filter,
        'status_choices': GeneratedContent.STATUS_CHOICES,
        'platform_choices': ContentIdea.PLATFORM_CHOICES,
    }
    return render(request, 'content/saved_content.html', context)

# API endpoint for quick caption generation (AJAX)
def api_generate_caption(request):
    """API endpoint for AJAX caption generation"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            idea_title = data.get('title')
            platform = data.get('platform', 'linkedin')
            tone = data.get('tone', 'professional')
            
            caption_data = GeminiContentGenerator.generate_caption(
                idea_title=idea_title,
                platform=platform,
                tone=tone
            )
            
            return JsonResponse({
                'success': True,
                'caption': caption_data['caption'],
                'hashtags': caption_data['hashtags']
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid method'})