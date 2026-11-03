from codeagent.domain.model import LLMResponse, Message


class FakeLLM:
    """Returns scripted responses for testing without API calls."""

    def __init__(self, responses: list[str]) -> None:
        self._responses = list(responses)
        self.calls: list[tuple[str, list[Message]]] = []

    def complete(
        self,
        system: str,
        messages: list[Message],
    ) -> LLMResponse:
        self.calls.append((system, messages))

        if not self._responses:
            raise RuntimeError("FakeLLM has no scripted responses left.")

        response = self._responses.pop(0)

        return LLMResponse(
            text=response,
            input_tokens=0,
            output_tokens=0,
        )