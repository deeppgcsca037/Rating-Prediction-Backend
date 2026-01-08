"""
LLM service for generating AI responses, summaries, and recommendations
"""
import json
import os
import requests
from typing import Dict, Optional
from config import USE_GEMINI, GEMINI_API_KEY, OPENROUTER_API_KEY, OPENROUTER_URL


class LLMService:
    """Service for interacting with LLMs"""
    
    def __init__(self):
        # Set OpenRouter credentials as instance variables regardless of which service is used
        self.api_key = OPENROUTER_API_KEY
        self.api_url = OPENROUTER_URL
        
        if USE_GEMINI and GEMINI_API_KEY:
            try:
                import google.generativeai as genai
                genai.configure(api_key=GEMINI_API_KEY)
                self.model = genai.GenerativeModel('gemini-2.5-flash')
                self.use_gemini = True
            except ImportError:
                raise Exception("google-generativeai is not installed. Install with: pip install google-generativeai")
        else:
            self.use_gemini = False

    def _call_gemini(self, prompt: str) -> str:
        """Call Gemini API"""
        try:
            response = self.model.generate_content(prompt)
            if hasattr(response, 'text'):
                result = response.text.strip()
                if result:  # Check if we got a valid response
                    return result
            # If response is empty or doesn't have text, return a more descriptive fallback
            print(f"Gemini API returned empty response for prompt: {prompt[:100]}...")
            raise Exception("Gemini API returned empty response")
        except Exception as e:
            print(f"Gemini API error: {str(e)}")
            raise Exception(f"Gemini API error: {str(e)}")

    def _call_openrouter(self, prompt: str) -> str:
        """Call OpenRouter API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "openai/gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}]
            }
            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content'].strip()
        except Exception as e:
            raise Exception(f"OpenRouter API error: {str(e)}")

    def _call_llm(self, prompt: str) -> str:
        """Call LLM (Gemini or OpenRouter)"""
        if self.use_gemini:
            try:
                return self._call_gemini(prompt)
            except Exception as e:
                # If Gemini fails (e.g., quota exceeded), fall back to OpenRouter
                print(f"Gemini failed: {str(e)}, falling back to OpenRouter")
                return self._call_openrouter(prompt)
        else:
            return self._call_openrouter(prompt)

    def generate_user_response(self, rating: int, review_text: str) -> str:
        """Generate AI response for user after submission"""
        prompt = f"""A customer submitted a {rating}-star review for a restaurant. 

Review: "{review_text}"

Generate a brief, professional, and empathetic response (2-3 sentences) that:
- Acknowledges their feedback
- Shows appreciation for their input
- Is appropriate for the rating level

Response:"""
        
        try:
            response = self._call_llm(prompt)
            print(f"User response generated: {response[:100]}...")
            return response[:500]  # Limit length
        except Exception as e:
            print(f"Error in generate_user_response: {str(e)}")
            return f"Thank you for your feedback. We appreciate your input and will use it to improve our service. (Note: AI service temporarily unavailable due to quota limits or API key issues)"

    def generate_summary(self, rating: int, review_text: str) -> str:
        """Generate AI summary of the review"""
        prompt = f"""Summarize this {rating}-star restaurant review in 1-2 sentences, highlighting the key points:

Review: "{review_text}"

Summary:"""
        
        try:
            response = self._call_llm(prompt)
            print(f"Summary generated: {response[:100]}...")
            return response[:300]  # Limit length
        except Exception as e:
            print(f"Error in generate_summary: {str(e)}")
            return f"AI Summary: {rating}-star review: {review_text[:200]}... (Note: AI service temporarily unavailable due to quota limits or API key issues)"

    def generate_recommended_actions(self, rating: int, review_text: str) -> str:
        """Generate recommended actions for admin based on review"""
        prompt = f"""Based on this {rating}-star restaurant review, suggest 2-3 specific, actionable recommendations for the restaurant management:

Review: "{review_text}"

Provide recommendations as a bulleted list. Be specific and practical.

Recommendations:"""
        
        try:
            response = self._call_llm(prompt)
            print(f"Recommended actions generated: {response[:100]}...")
            return response[:500]  # Limit length
        except Exception as e:
            print(f"Error in generate_recommended_actions: {str(e)}")
            if rating <= 2:
                return "• Follow up with customer to address concerns\n• Review service protocols\n• Investigate specific issues mentioned\n\n(Note: AI service temporarily unavailable due to quota limits or API key issues)"
            elif rating == 3:
                return "• Identify areas for improvement\n• Consider customer feedback in planning\n\n(Note: AI service temporarily unavailable due to quota limits or API key issues)"
            else:
                return "• Maintain current service standards\n• Share positive feedback with staff\n• Consider highlighting strengths in marketing\n\n(Note: AI service temporarily unavailable due to quota limits or API key issues)"


