from openai import OpenAI
import copy
import json
from typing import List, Dict
from pprint import pprint
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError


# OPENAI_API_KEY = CONFIG['OPENAI_API_AIXPA']
DEFAULT_OPENAI_MODEL = "llama-3.3-70b-versatile"  #gpt-3.5-turbo-0125"  "gpt-4o-mini-2024-07-18" "gpt-3.5-turbo-0125"
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 500




class GenerationModelChat:
    def __init__(self,
                 model_name = DEFAULT_OPENAI_MODEL,
                 temperature = DEFAULT_TEMPERATURE,
                 max_tokens = DEFAULT_MAX_TOKENS,
                 access_token = "",
                 question_sys_prompt = ""):

        self.model_name = model_name
        self.access_token = access_token
        self.model = self.set_model()
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.question_sys_prompt = question_sys_prompt 



    def set_model(self):
        return OpenAI(api_key=self.access_token, base_url="https://api.groq.com/openai/v1")

    def generate_text(self, chat):
        try:
            response = self.model.chat.completions.create(
                model= self.model_name,
                messages=chat,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error: {e}")
            return "An error occurred. Please, try again."



class GenerationModelComplete:
    def __init__(self,
                 model_name: str = DEFAULT_OPENAI_MODEL,
                 temperature: float = DEFAULT_TEMPERATURE,
                 max_tokens: int = DEFAULT_MAX_TOKENS,
                 access_token: str = ""):
        self.model_name = model_name
        self.access_token = access_token
        self.model = self.set_model()
        self.temperature = temperature
        self.max_tokens = max_tokens

    def set_model(self):
        # Initialize the OpenAI API client with the provided access token
        return OpenAI(api_key=self.access_token, base_url="https://api.groq.com/openai/v1")

    def generate_text(self, prompt: str) -> str:
        try:
            # Call the completions.create method from OpenAI's API
            response = self.model.Completion.create(
                model=self.model_name,
                prompt=prompt,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            # Extract and return the generated text
            return response['choices'][0]['text']
        except Exception as e:
            # Print the error for debugging purposes
            print(f"Error: {e}")
            return "An error occurred. Please, try again."
