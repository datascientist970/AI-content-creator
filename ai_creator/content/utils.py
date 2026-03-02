import google.generativeai as genai
import json
import re
from django.conf import settings
from datetime import datetime

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

class GeminiContentGenerator:
     
    @staticmethod
    def generate_ideas(topic, niche=None, count=5, platform=None, tone='professional', target_audience=None):
        """Generate content ideas using Gemini"""
        
        current_year = datetime.now().year
        current_date = datetime.now().strftime("%B %d, %Y")
        
        prompt = f"""Generate {count} creative and engaging content ideas about "{topic}" for {current_year}.

        IMPORTANT: Today's date is {current_date}. Use CURRENT year {current_year} in all examples, NOT 2024.

        Additional Context:
        - Niche/Specific Area: {niche if niche else 'General'}
        - Target Platform: {platform if platform else 'Multiple platforms'}
        - Preferred Tone: {tone}
        - Target Audience: {target_audience if target_audience else 'General audience'}
        
        For each idea, provide the following in a structured format:
        1. Title: A catchy, click-worthy headline (use current year {current_year} in titles if mentioning years)
        2. Category: Choose from [tips, case_study, news, how_to, inspirational, trending]
        3. Platform: Best platform for this idea [instagram, linkedin, twitter, facebook, tiktok]
        4. Angle: Unique perspective or approach
        5. Pain Point: What problem does this solve for the audience?
        
        Format the response as a valid JSON array with objects containing keys: 
        title, category, platform, angle, pain_point
        
        CRITICAL: Do NOT use 2024 in any titles or content. Use {current_year} instead.
        Make the ideas specific, actionable, and tailored to the context provided.
        """
             
        try:
            response = model.generate_content(prompt)
            
            # Extract JSON from response
            json_str = re.search(r'\[.*\]', response.text, re.DOTALL)
            if json_str:
                ideas = json.loads(json_str.group())
            else:
                # Fallback parsing
                ideas = GeminiContentGenerator._parse_ideas_fallback(response.text)
            
            # Add metadata
            for idea in ideas:
                idea['tone'] = tone
                idea['topic'] = topic
                if target_audience:
                    idea['target_audience'] = target_audience
            
            return ideas
            
        except Exception as e:
            print(f"Error generating ideas: {e}")
            return GeminiContentGenerator._generate_fallback_ideas(topic, count)
    
    @staticmethod
    def generate_caption(idea_title, platform, tone, additional_instructions=""):
        """Generate a caption using Gemini"""
        
        platform_guidelines = {
            'instagram': "Instagram: Visual-focused, use emojis, engaging, 5-10 hashtags, casual tone",
            'linkedin': "LinkedIn: Professional, value-driven, longer form, industry insights, 3-5 hashtags",
            'twitter': "Twitter: Concise, witty, under 280 characters, 1-2 hashtags, conversation starter",
            'facebook': "Facebook: Community-focused, storytelling, longer, 2-3 hashtags, encourage comments",
            'tiktok': "TikTok: Trendy, energetic, short, viral potential, minimal hashtags"
        }
        
        prompt = f"""Write a compelling social media caption for this content idea:
        
        Content Topic: {idea_title}
        Platform: {platform}
        Tone: {tone}
        
        Platform Guidelines: {platform_guidelines.get(platform, 'Write an engaging caption')}
        
        Additional Instructions: {additional_instructions if additional_instructions else 'None'}
        
        Requirements:
        - Start with a strong hook to grab attention
        - Include value proposition in the first 2 lines
        - Add relevant emojis where appropriate
        - Include platform-appropriate hashtags
        - End with a call-to-action or question
        - Keep it authentic and engaging
        
        Return format:
        CAPTION: [The main caption text]
        HASHTAGS: [Comma-separated hashtags]
        """
        
        try:
            response = model.generate_content(prompt)
            
            # Parse the response
            caption_text = response.text
            
            # Extract hashtags
            hashtags = re.findall(r'#\w+', caption_text)
            hashtag_line = ', '.join(hashtags) if hashtags else ''
            
            # Clean caption (remove hashtag section if it exists)
            if 'HASHTAGS:' in caption_text:
                parts = caption_text.split('HASHTAGS:')
                caption_text = parts[0].replace('CAPTION:', '').strip()
                if not hashtag_line and len(parts) > 1:
                    hashtag_line = parts[1].strip()
            
            return {
                'caption': caption_text,
                'hashtags': hashtag_line
            }
            
        except Exception as e:
            print(f"Error generating caption: {e}")
            return GeminiContentGenerator._generate_fallback_caption(idea_title)
    
    @staticmethod
    def check_quality(caption, platform):
        """Check content quality using Gemini"""
        
        prompt = f"""Evaluate this social media caption for quality and provide improvement suggestions.
        
        Caption: "{caption}"
        Platform: {platform}
        
        Evaluate these aspects (score 0-10):
        1. Hook strength
        2. Engagement potential
        3. Clarity
        4. Platform appropriateness
        5. Call-to-action effectiveness
        
        Also identify:
        - Any issues or weaknesses
        - Specific improvement suggestions
        
        Return as JSON:
        {{
            "overall_score": 0-10,
            "hook_score": 0-10,
            "engagement_score": 0-10,
            "clarity_score": 0-10,
            "platform_score": 0-10,
            "cta_score": 0-10,
            "issues": ["issue1", "issue2"],
            "suggestions": ["suggestion1", "suggestion2"]
        }}
        """
        
        try:
            response = model.generate_content(prompt)
            
            # Extract JSON
            json_str = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_str:
                quality_data = json.loads(json_str.group())
                return quality_data
            
        except Exception as e:
            print(f"Error checking quality: {e}")
        
        # Return default quality data
        return {
            'overall_score': 7.5,
            'hook_score': 7.0,
            'engagement_score': 7.0,
            'clarity_score': 8.0,
            'platform_score': 7.5,
            'cta_score': 7.0,
            'issues': ['Unable to perform detailed quality check'],
            'suggestions': ['Review manually for best results']
        }
    
    @staticmethod
    def _parse_ideas_fallback(text):
        """Fallback parser for ideas"""
        ideas = []
        lines = text.split('\n')
        current_idea = {}
        
        for line in lines:
            line = line.strip()
            if line.startswith('Title:') or '1.' in line and 'Title' in line:
                if current_idea and 'title' in current_idea:
                    ideas.append(current_idea)
                current_idea = {}
                current_idea['title'] = line.replace('Title:', '').replace('1.', '').strip()
            elif 'Category:' in line:
                current_idea['category'] = line.replace('Category:', '').strip().lower()
            elif 'Platform:' in line:
                current_idea['platform'] = line.replace('Platform:', '').strip().lower()
            elif 'Angle:' in line:
                current_idea['angle'] = line.replace('Angle:', '').strip()
            elif 'Pain Point:' in line:
                current_idea['pain_point'] = line.replace('Pain Point:', '').strip()
        
        if current_idea and 'title' in current_idea:
            ideas.append(current_idea)
        
        return ideas if ideas else GeminiContentGenerator._generate_fallback_ideas("content", 5)
    
    @staticmethod
    def _generate_fallback_ideas(topic, count):
        current_year = datetime.now().year

    
        ideas = []
        categories = ['tips', 'how_to', 'inspirational', 'case_study', 'news']
        platforms = ['linkedin', 'instagram', 'twitter', 'facebook']
    
        for i in range(count):
            ideas.append({
            'title': f"5 {topic} strategies that actually work in {current_year}",
            'category': categories[i % len(categories)],
            'platform': platforms[i % len(platforms)],
            'angle': f"Practical {topic} advice from industry experts for {current_year}",
            'pain_point': f"Not seeing results with current {topic} efforts",
            'tone': 'professional',
            'topic': topic
        })
    
        return ideas
    
    @staticmethod
    def _generate_fallback_caption(topic):
        """Generate fallback caption"""
        return {
            'caption': f"Want to master {topic}? Here's what you need to know...\n\n[Content would go here]\n\nWhat's your biggest challenge with {topic}? Share below! 👇",
            'hashtags': f"#{topic.replace(' ', '')}, #SocialMedia, #MarketingTips"
        }