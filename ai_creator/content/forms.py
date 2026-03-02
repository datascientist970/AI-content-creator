from django import forms
from .models import ContentIdea, GeneratedContent

class ContentIdeaForm(forms.Form):
    topic = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Social Media Marketing, Digital Trends, etc.'
        })
    )
    
    niche = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., B2B SaaS, Fitness, Real Estate (optional)'
        })
    )
    
    platform = forms.ChoiceField(
        choices=[('', 'All Platforms')] + ContentIdea.PLATFORM_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    tone = forms.ChoiceField(
        choices=ContentIdea.TONE_CHOICES,
        initial='professional',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    count = forms.IntegerField(
        min_value=1,
        max_value=20,
        initial=5,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 1,
            'max': 20
        })
    )
    
    target_audience = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Small business owners, Marketing managers'
        })
    )

class CaptionForm(forms.Form):
    idea_id = forms.IntegerField(widget=forms.HiddenInput())
    topic = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'readonly': True
        })
    )
    
    platform = forms.ChoiceField(
        choices=ContentIdea.PLATFORM_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    tone = forms.ChoiceField(
        choices=ContentIdea.TONE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    additional_instructions = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Any specific instructions? (e.g., include a statistic, mention a specific feature)'
        })
    )

class CalendarFilterForm(forms.Form):
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    platform = forms.ChoiceField(
        choices=[('', 'All Platforms')] + ContentIdea.PLATFORM_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    status = forms.ChoiceField(
        choices=[('', 'All Status')] + GeneratedContent.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )