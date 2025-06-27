"""Unified client for querying multiple LLM providers."""
import os
import time
import datetime
from dotenv import load_dotenv
from openai import OpenAI
from google import genai
from google.genai import types
from together import Together
from mistralai import Mistral


# Constants
DEFAULT_TEMPERATURE = 0.7  # Default temperature for generation
MODEL_OPENAI = "gpt-4o-2024-08-06"
MODEL_GOOGLE = "gemini-1.5-pro" 
MODEL_DEEPSEEK = "deepseek-ai/DeepSeek-V3" 
MODEL_MISTRAL = "mistral-large-2407"


# Load environment variables from .env file
load_dotenv()

def call_api(model_id: int, prompt: str) -> dict:
    """
    Dispatch prompt to the chosen provider and append timing metadata.
    """
    # Map provider IDs to helper functions
    api_functions = {
        0: get_openai_api,
        1: get_google_api,
        2: get_deepseek_api,
        3: get_mistral_api,
    }

    if model_id not in api_functions:
        raise ValueError(f"Unsupported model_id: {model_id}")

    # Measure latency
    start_time = time.time()
    result = api_functions[model_id](prompt)
    end_time = time.time()

    # Annotate response with timestamp and latency
    result.update({
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "request_latency_ms": int((end_time - start_time) * 1000),
    })

    return result

def get_openai_api(prompt: str, model: str = MODEL_OPENAI) -> dict:
    """Return OpenAI chat completion."""
    # Build client
    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)

    # Fire request
    completion = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        store=True,  # Store the response in the API
        temperature=DEFAULT_TEMPERATURE
    )

    return {
        "raw_response": completion.choices[0].message.content,
        "tokens_input": completion.usage.prompt_tokens,
        "tokens_output": completion.usage.completion_tokens,
    }

def get_google_api(prompt: str, model: str = MODEL_GOOGLE) -> dict:
    """Return Google Gemini chat completion."""
    # Build client
    api_key = os.getenv("GOOGLE_API_KEY")
    client = genai.Client(api_key=api_key)

    # Fire request
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(temperature=DEFAULT_TEMPERATURE)
    )

    return {
        "raw_response": response.candidates[0].content.parts[0].text,
        "tokens_input": response.usage_metadata.prompt_token_count,
        "tokens_output": response.usage_metadata.candidates_token_count,
    }

def get_deepseek_api(prompt: str, model: str = MODEL_DEEPSEEK) -> dict:
    """Return DeepSeek chat completion via TogetherAI."""
    # Build client
    api_key = os.getenv("TOGETHER_API_KEY")  # library looks for this env var
    client = Together(api_key=api_key)

    # Fire request
    completion = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=DEFAULT_TEMPERATURE
    )

    return {
        "raw_response": completion.choices[0].message.content,
        "tokens_input": completion.usage.prompt_tokens,
        "tokens_output": completion.usage.completion_tokens,
    }

def get_mistral_api(prompt: str, model: str = MODEL_MISTRAL) -> dict:
    """Return Mistral chat completion."""
    # Build client
    api_key = os.getenv("MISTRAL_API_KEY")
    client = Mistral(api_key=api_key)

    # Fire request
    chat_response = client.chat.complete(
        model=model,
        temperature=DEFAULT_TEMPERATURE,
        messages=[{"role": "user", "content": prompt}],
    )

    usage = getattr(chat_response, "usage", None)

    return {
        "raw_response": chat_response.choices[0].message.content,
        "tokens_input": usage.prompt_tokens if usage else None,
        "tokens_output": usage.completion_tokens if usage else None,
    }
