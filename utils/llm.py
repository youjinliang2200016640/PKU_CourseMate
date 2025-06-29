from openai import OpenAI, NOT_GIVEN
import os
import sys
from typing import Literal, cast
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionMessage
)

from openai.types.chat.completion_create_params import ResponseFormat
from tenacity import retry, stop_after_attempt, wait_random_exponential

class OpenaiModel:
    def __init__(
        self, 
        name,
        max_output_token: int
    ) -> None:
        self.name = name
        self.max_output_token = max_output_token
        self.client : OpenAI |  None = None
    
    def setup(self) -> None:
        """
        Check API key, and initialize OpenAI client.
        """
        if self.client is None:
            key = self.check_api_key()
            self.client = OpenAI(api_key=key, base_url=os.getenv("OPENAI_API_BASE_URL", "https://api.deepseek.com"))

    def extract_resp_content(
        self, chat_completion_message: ChatCompletionMessage
    ) -> str:
        """
        Given a chat completion message, extract the content from it.
        """
        content = chat_completion_message.content
        if content is None:
            return ""
        else:
            return content
    def check_api_key(self) -> str:
        key = os.getenv("OPENAI_KEY")
        if not key:
            print("Please set the OPENAI_KEY env var")
            sys.exit(1)
        return key
    
    @retry(wait=wait_random_exponential(min=30, max=600), stop=stop_after_attempt(3))
    def call(
        self,
        messages: list[dict],
        top_p: float = 1,
        response_format: Literal["text", "json_object"] = "text",
        temperature: float | None = None,
        **kwargs,
    ) -> tuple[
        str,
        int,
        int
    ]:
        assert self.client is not None
        response: ChatCompletion = self.client.chat.completions.create(
            model=self.name,
            messages=messages,  # type: ignore
            temperature=(
                temperature if temperature is not None else NOT_GIVEN
            ),
            response_format=cast(ResponseFormat, {"type": response_format}),
            max_tokens= self.max_output_token,
            max_completion_tokens=self.max_output_token,
            top_p=top_p,
            stream=False,
        )
        usage_stats = response.usage
        assert usage_stats is not None

        input_tokens = int(usage_stats.prompt_tokens)
        output_tokens = int(usage_stats.completion_tokens)
        raw_response = response.choices[0].message
        content = self.extract_resp_content(raw_response)
        return (
            content, 
            input_tokens, 
            output_tokens
        )
        
        
class Deepseek_V3(OpenaiModel):
    def __init__(self):
        super().__init__("deepseek-chat", 8192)
        self.note = "Deepseek chat .64k window. Input $0.14/M, Output $0.28/M."

class Deepseek_R1(OpenaiModel):
    def __init__(self):
        super().__init__("deepseek-reasoner", 8192)
        self.note = "Deepseek reasoner. 64k window. Input $0.55/M, Output $2.19/M."