"""LLM service module for analyzing text and generating atomic notes."""

import json
import os
import time
from typing import Dict, List, Optional, Union
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class LLMService:
    """Handles interactions with various LLM APIs for text analysis."""
    
    def __init__(self, provider: str = "openai", model: Optional[str] = None):
        """
        Initialize LLM service with specified provider.
        
        Args:
            provider: LLM provider ("openai", "anthropic", "google")
            model: Specific model to use (optional, uses defaults)
        """
        self.provider = provider.lower()
        self.model = model
        self.client = None
        
        self._setup_client()
    
    def _setup_client(self):
        """Set up the appropriate client based on provider."""
        if self.provider == "openai":
            try:
                import openai
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError("OPENAI_API_KEY not found in environment variables")
                self.client = openai.OpenAI(api_key=api_key)
                self.model = self.model or "gpt-4o-mini"
            except ImportError:
                raise ImportError("openai library not installed. Run: pip install openai")
        
        elif self.provider == "anthropic":
            try:
                import anthropic
                api_key = os.getenv("ANTHROPIC_API_KEY")
                if not api_key:
                    raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
                self.client = anthropic.Anthropic(api_key=api_key)
                self.model = self.model or "claude-3-5-haiku-20241022"
            except ImportError:
                raise ImportError("anthropic library not installed. Run: pip install anthropic")
        
        elif self.provider == "google":
            try:
                import google.generativeai as genai
                api_key = os.getenv("GOOGLE_API_KEY")
                if not api_key:
                    raise ValueError("GOOGLE_API_KEY not found in environment variables")
                genai.configure(api_key=api_key)
                self.client = genai.GenerativeModel(self.model or "gemini-1.5-flash")
            except ImportError:
                raise ImportError("google-generativeai library not installed. Run: pip install google-generativeai")
        
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def get_atomic_notes_from_text(self, text_chunk: str, max_retries: int = 3) -> List[Dict]:
        """
        Analyze text and extract atomic notes using LLM.
        
        Args:
            text_chunk: Text to analyze
            max_retries: Maximum number of retry attempts
            
        Returns:
            List of atomic note dictionaries
        """
        prompt = self._build_analysis_prompt(text_chunk)
        
        for attempt in range(max_retries):
            try:
                if self.provider == "openai":
                    response = self._query_openai(prompt)
                elif self.provider == "anthropic":
                    response = self._query_anthropic(prompt)
                elif self.provider == "google":
                    response = self._query_google(prompt)
                
                # Parse JSON response
                notes_data = json.loads(response)
                
                # Validate the response structure
                if self._validate_notes_data(notes_data):
                    return notes_data
                else:
                    raise ValueError("Invalid response structure from LLM")
                    
            except json.JSONDecodeError as e:
                print(f"Attempt {attempt + 1}: Failed to parse JSON response - {e}")
                if attempt == max_retries - 1:
                    raise Exception(f"Failed to get valid JSON response after {max_retries} attempts")
                time.sleep(2 ** attempt)  # Exponential backoff
                
            except Exception as e:
                print(f"Attempt {attempt + 1}: Error querying LLM - {e}")
                if attempt == max_retries - 1:
                    raise Exception(f"Failed to get response from LLM after {max_retries} attempts: {e}")
                time.sleep(2 ** attempt)
        
        raise Exception("Unexpected error in get_atomic_notes_from_text")
    
    def _build_analysis_prompt(self, text_chunk: str) -> str:
        """Build the master prompt for text analysis."""
        return f"""You are an AI expert in knowledge management, specifically the Zettelkasten and atomic note-taking method. Your task is to analyze the following text from the book "A Random Walk Down Wall Street".

Perform the following actions:

1. Read the text and identify all distinct, core financial concepts, theories, or key terms.
2. For each concept, write a concise, self-contained summary (an "atomic note").
3. Within each summary, identify where other concepts you've found are mentioned and wrap their exact names in [[wikilinks]].
4. Return the output as a single JSON array of objects, where each object represents a single atomic note and has three keys: "title", "summary", and "tags".

Example JSON Output:
[
  {{
    "title": "Random Walk Theory",
    "summary": "The Random Walk Theory posits that stock market prices evolve according to a random walk and thus cannot be predicted. This idea is a cornerstone of the [[Efficient Market Hypothesis]] and challenges the effectiveness of [[Technical Analysis]].",
    "tags": ["market-theory", "stock-prices"]
  }},
  {{
    "title": "Efficient Market Hypothesis",
    "summary": "The Efficient Market Hypothesis (EMH) asserts that financial markets are 'informationally efficient,' meaning prices fully reflect all available information. This theory is built upon the [[Random Walk Theory]].",
    "tags": ["market-efficiency", "investment-theory"]
  }}
]

Guidelines:
- Each note should be self-contained and understandable on its own
- Use [[wikilinks]] to connect related concepts within summaries
- Tags should be lowercase and use hyphens instead of spaces
- Focus on the most important and distinct concepts
- Avoid creating notes for very basic or common terms unless they're specifically defined in the text
- Keep summaries concise but informative (2-4 sentences)

Now, analyze this text:

{text_chunk}"""
    
    def _query_openai(self, prompt: str) -> str:
        """Query OpenAI API."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=4000
        )
        return response.choices[0].message.content
    
    def _query_anthropic(self, prompt: str) -> str:
        """Query Anthropic API."""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    
    def _query_google(self, prompt: str) -> str:
        """Query Google Generative AI API."""
        response = self.client.generate_content(
            prompt,
            generation_config={
                "temperature": 0.7,
                "max_output_tokens": 4000,
            }
        )
        return response.text
    
    def _validate_notes_data(self, notes_data: Union[List, Dict]) -> bool:
        """Validate the structure of notes data from LLM."""
        if not isinstance(notes_data, list):
            return False
        
        for note in notes_data:
            if not isinstance(note, dict):
                return False
            
            required_keys = {"title", "summary", "tags"}
            if not all(key in note for key in required_keys):
                return False
            
            if not isinstance(note["title"], str) or not note["title"].strip():
                return False
            
            if not isinstance(note["summary"], str) or not note["summary"].strip():
                return False
            
            if not isinstance(note["tags"], list):
                return False
        
        return True


def get_atomic_notes_from_text(text_chunk: str, provider: str = "openai", model: Optional[str] = None) -> List[Dict]:
    """
    Convenience function for getting atomic notes from text.
    
    Args:
        text_chunk: Text to analyze
        provider: LLM provider to use
        model: Specific model to use
        
    Returns:
        List of atomic note dictionaries
    """
    service = LLMService(provider=provider, model=model)
    return service.get_atomic_notes_from_text(text_chunk)