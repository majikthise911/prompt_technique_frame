# providers.py
import os
from openai import OpenAI
from anthropic import Anthropic
from dotenv import load_dotenv
from typing import Dict, List, Tuple

# Load environment variables from .env file (local development)
load_dotenv()

# Support for Streamlit secrets (cloud deployment)
try:
    import streamlit as st
    # If running in Streamlit, use st.secrets
    if hasattr(st, 'secrets'):
        USE_STREAMLIT_SECRETS = True
    else:
        USE_STREAMLIT_SECRETS = False
except:
    USE_STREAMLIT_SECRETS = False

def get_env(key: str, default: str = None) -> str:
    """Get environment variable from either .env or Streamlit secrets"""
    if USE_STREAMLIT_SECRETS:
        try:
            # Streamlit secrets accessed with bracket notation or .get() on the underlying dict
            if key in st.secrets:
                return st.secrets[key]
            else:
                return default
        except Exception as e:
            # Fallback if secrets access fails
            pass
    return os.getenv(key, default)

class MultiProviderClient:
    """Unified interface for Claude, GPT, and Grok"""

    def __init__(self):
        # Initialize providers dict - clients created lazily
        self.providers = {}

        # Configure Claude if API key available
        anthropic_key = get_env("ANTHROPIC_API_KEY")
        if anthropic_key:
            self.providers["claude"] = {
                "client": Anthropic(api_key=anthropic_key),
                "model": get_env("CLAUDE_MODEL", "claude-sonnet-4-5-20250929"),
                "type": "anthropic"
            }

        # Configure GPT if API key available
        openai_key = get_env("OPENAI_API_KEY")
        if openai_key:
            self.providers["gpt"] = {
                "client": OpenAI(api_key=openai_key),
                "model": get_env("GPT_MODEL", "gpt-4o-mini"),
                "type": "openai"
            }

        # Configure Grok if API key available
        grok_key = get_env("GROK_API_KEY")
        if grok_key:
            self.providers["grok"] = {
                "client": OpenAI(
                    api_key=grok_key,
                    base_url=get_env("GROK_BASE_URL", "https://api.x.ai/v1")
                ),
                "model": get_env("GROK_MODEL", "grok-4-fast-reasoning"),
                "type": "openai"
            }

    def complete(self, provider: str, system_prompt: str, user_message: str,
                 temperature: float = 0.7, max_tokens: int = 2048) -> Tuple[str, Dict]:
        """
        Send completion request to specified provider
        Returns: (response_text, metadata)
        """
        if provider not in self.providers:
            raise ValueError(f"Unknown provider: {provider}")

        config = self.providers[provider]

        try:
            if config["type"] == "anthropic":
                response = config["client"].messages.create(
                    model=config["model"],
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_message}]
                )
                text = response.content[0].text
                metadata = {
                    "provider": provider,
                    "model": config["model"],
                    "tokens": response.usage.input_tokens + response.usage.output_tokens,
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                }

            else:  # OpenAI-compatible (GPT, Grok)
                response = config["client"].chat.completions.create(
                    model=config["model"],
                    temperature=temperature,
                    max_tokens=max_tokens,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ]
                )
                text = response.choices[0].message.content
                metadata = {
                    "provider": provider,
                    "model": config["model"],
                    "tokens": response.usage.total_tokens,
                    "input_tokens": response.usage.prompt_tokens,
                    "output_tokens": response.usage.completion_tokens
                }

            return text, metadata

        except Exception as e:
            return f"Error from {provider}: {str(e)}", {"error": True}

    def get_available_providers(self) -> List[str]:
        """Return list of providers with valid API keys"""
        # Simply return the keys from initialized providers
        return list(self.providers.keys())
