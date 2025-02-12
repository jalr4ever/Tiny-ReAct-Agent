import os
from typing import List, Tuple

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class BaseModel:
    def __init__(self) -> None:
        pass

    def chat(self, prompt: str, history: List[dict], meta_instruction: str = ''):
        pass


class OpenAIChat(BaseModel):
    def __init__(self) -> None:
        self.client = OpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
            base_url=os.getenv('OPENAI_API_BASE'))

    def chat(self, prompt: str, history: List[dict], meta_instruction: str = '') -> Tuple[str, List[dict]]:
        messages = []
        if meta_instruction:
            messages.append({"role": "system", "content": meta_instruction})

        for msg in history:
            if 'user' in msg:
                messages.append({"role": "user", "content": msg['user']})
            if 'assistant' in msg:
                messages.append({"role": "assistant", "content": msg['assistant']})

        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=os.getenv('LLM_MODEL'),
            messages=messages,
            temperature=0.1
        )

        assistant_message = response.choices[0].message.content
        history.append({"user": prompt, "assistant": assistant_message})

        return assistant_message, history


# 使用示例
if __name__ == '__main__':
    model = OpenAIChat()  # 确保设置了环境变量
    response, history = model.chat('Hello', [])
    print(response)
