from unittest.mock import MagicMock

from codeagent.domain.model import Message
from llm.gemini_llm import GeminiLLM


def create_mock_gemini_client() -> MagicMock:
    client = MagicMock()

    client.models.generate_content.return_value.text = "print('Hello World')"
    client.models.generate_content.return_value.usage_metadata = MagicMock(
        prompt_token_count=10,
        candidates_token_count=5,
    )

    return client

def test_gemini_llm_returns_structured_response() -> None:
    mock_client = create_mock_gemini_client()

    llm = GeminiLLM(client=mock_client)

    response = llm.complete(
        system="You are a Python programmer.",
        messages=[
            Message(
                role="user",
                content="Write Hello World in Python.",
            )
        ],
    )

    assert response.text == "print('Hello World')"
    assert response.input_tokens == 10
    assert response.output_tokens == 5

    assert mock_client.models.generate_content.called

def test_gemini_llm_sends_correct_request() -> None:
    mock_client = create_mock_gemini_client()

    llm = GeminiLLM(
        model="gemini-3.8-flash",
        client=mock_client,
    )

    system = "You are an expert Python programmer."

    messages = [
        Message(
            role="user",
            content="Write a prime number checker.",
        ),
        Message(
            role="assistant",
            content="I will write a Python function.",
        ),
    ]

    llm.complete(system=system, messages=messages)

    mock_client.models.generate_content.assert_called_once()

    call_kwargs = mock_client.models.generate_content.call_args.kwargs

    assert call_kwargs["model"] == "gemini-3.8-flash"

    assert call_kwargs["config"].system_instruction == system

    contents = call_kwargs["contents"]

    assert len(contents) == 2

    assert contents[0].role == "user"
    assert contents[0].parts[0].text == "Write a prime number checker."

    assert contents[1].role == "model"
    assert contents[1].parts[0].text == "I will write a Python function."

def test_gemini_llm_handles_missing_usage_metadata() -> None:
    mock_client = MagicMock()

    mock_client.models.generate_content.return_value.text = "print('Hello')"
    mock_client.models.generate_content.return_value.usage_metadata = None

    llm = GeminiLLM(client=mock_client)

    response = llm.complete(
        system="You are a Python programmer.",
        messages=[
            Message(
                role="user",
                content="Write Hello World.",
            )
        ],
    )

    assert response.text == "print('Hello')"
    assert response.input_tokens == 0
    assert response.output_tokens == 0