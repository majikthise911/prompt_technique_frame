# providers.py
import os
from openai import OpenAI
from anthropic import Anthropic
from dotenv import load_dotenv
from typing import Dict, List, Tuple

load_dotenv()

class MultiProviderClient:
    """Unified interface for Claude, GPT, and Grok"""

    def __init__(self):
        self.providers = {
            "claude": {
                "client": Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY")),
                "model": os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5-20250929"),
                "type": "anthropic"
            },
            "gpt": {
                "client": OpenAI(api_key=os.getenv("OPENAI_API_KEY")),
                "model": os.getenv("GPT_MODEL", "gpt-4o-mini"),
                "type": "openai"
            },
            "grok": {
                "client": OpenAI(
                    api_key=os.getenv("GROK_API_KEY"),
                    base_url=os.getenv("GROK_BASE_URL", "https://api.x.ai/v1")
                ),
                "model": os.getenv("GROK_MODEL", "grok-4-fast-reasoning"),
                "type": "openai"
            }
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
        available = []
        for name, config in self.providers.items():
            # Map provider names to their actual environment variable names
            if name == "claude":
                key_var = "ANTHROPIC_API_KEY"
            elif name == "gpt":
                key_var = "OPENAI_API_KEY"
            elif name == "grok":
                key_var = "GROK_API_KEY"
            else:
                key_var = f"{name.upper()}_API_KEY"

            if os.getenv(key_var):
                available.append(name)
        return available
