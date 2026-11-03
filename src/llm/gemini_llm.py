import os

from google import genai
from google.genai import Client, types

from codeagent.domain.model import LLMResponse, Message


class GeminiLLM:
    """Gemini implementation of the LLM port."""

    def __init__(
        self,
        model: str = "gemini-3.8-flash",
        api_key: str | None = None,
        client: Client | None = None,
    ) -> None:
        self.model = model
        self.client = client or genai.Client(
            api_key=api_key or os.getenv("CODEAGENT_LLM_API_KEY")
        )

    def complete(
        self,
        system: str,
        messages: list[Message],
    ) -> LLMResponse:

        contents = [
            types.Content(
                role="model" if message.role == "assistant" else message.role,
                parts=[types.Part.from_text(text=message.content)],
            )
            for message in messages
        ]

        response = self.client.models.generate_content(
            model=self.model,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system,
            ),
        )

        usage = response.usage_metadata

        return LLMResponse(
            text=response.text or "",
            input_tokens=(
                usage.prompt_token_count or 0 if usage else 0
            ),
            output_tokens=(
                usage.candidates_token_count or 0 if usage else 0
            ),
        )