import os

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from instructor import from_openai
from openai import OpenAI
import json5

from tool import Tools

load_dotenv()

MODEL = os.getenv("LLM_MODEL")
API_BASE = os.getenv("OPENAI_API_BASE")
API_KEY = os.getenv("OPENAI_API_KEY")

# Tool description template
TOOL_DESC = """{name_for_model}: Call this tool to interact with the {name_for_human} API. What is the {name_for_human} API useful for? {description_for_model} Parameters: {parameters} Format the arguments as a JSON object."""

# System prompt for the ReAct Agent
REACT_PROMPT = """You are an AI assistant that answers questions using the provided tools when necessary.

You have access to the following tools:
{tool_descs}

To use a tool, respond with:
Thought: [your thought process]
Action: [the action to take, should be one of {tool_names}]
Action Input: [the input to the action]

When you have the final answer, respond with:
Final Answer: [the final answer]

You can think and take actions multiple times if needed. When the question involves the current date or real-time data, use a tool.

Begin!"""


# Pydantic model for structured LLM responses
class AgentStep(BaseModel):
    Thought: str = Field(None, description="The thought process")
    Action: str = Field(None, description="The action to take")
    ActionInput: str = Field(None, description="The input to the action")
    FinalAnswer: str = Field(None, description="The final answer")


# OpenAI client with instructor support
class OpenAIChat:
    def __init__(self):
        self.client = from_openai(OpenAI(base_url=API_BASE, api_key=API_KEY))

    def chat(self, messages, response_model=None):
        if response_model:
            response = self.client.chat.completions.create(
                model=MODEL,
                messages=messages,
                response_model=response_model,
            )
            return response
        else:
            response = self.client.chat.completions.create(
                model=MODEL,
                messages=messages,
            )
            return response.choices[0].message.content


# ReAct Agent class
class Agent:
    def __init__(self, path: str = ''):
        self.path = path
        self.tool = Tools()
        self.system_prompt = self.build_system_input()
        self.model = OpenAIChat()

    def build_system_input(self):
        """Builds the system prompt with tool descriptions and names."""
        tool_descs = [TOOL_DESC.format(**tool) for tool in self.tool.toolConfig]
        tool_descs = '\n\n'.join(tool_descs)
        tool_names = ','.join([tool['name_for_model'] for tool in self.tool.toolConfig])
        sys_prompt = REACT_PROMPT.replace('{tool_descs}', tool_descs).replace('{tool_names}', tool_names)
        return sys_prompt

    def call_plugin(self, plugin_name, plugin_args):
        """Executes the specified tool with the given arguments."""
        try:
            args_dict = json5.loads(plugin_args)
        except:
            args_dict = {"search_query": plugin_args}
        if plugin_name == 'exa_search':
            return self.tool.exa_search(**args_dict)
        raise ValueError(f"Unknown plugin: {plugin_name}")

    def text_completion(self, text, history=None):
        """Processes the user query through multiple thought/action cycles."""
        if history is None:
            history = []
        print(f"\n👨‍🍳: {text}")
        messages = [{"role": "system", "content": self.system_prompt}] + history
        messages.append({"role": "user", "content": text})

        while True:
            step = self.model.chat(messages, response_model=AgentStep)
            print(f"🤖Step log...[Thinking]: {step.Thought}; [Action]: {step.Action}")

            if step.FinalAnswer:
                return step.FinalAnswer, messages

            elif step.Action and step.ActionInput:
                observation = self.call_plugin(step.Action, step.ActionInput)
                messages.append({"role": "assistant", "content": str(step)})
                messages.append({"role": "user", "content": f"Observation: {observation}"})

            else:
                raise ValueError("Invalid response from LLM: neither action nor final answer provided")


# Main execution for testing
if __name__ == '__main__':
    agent = Agent()
    prompt = agent.build_system_input()
    print(prompt)

    response, _ = agent.text_completion(text='Hello', history=[])
    print("✨Final Response(See FinalAnswer): " + response)

    response, _ = agent.text_completion(text='What is the weather like in Shenzhen, China today?', history=[])
    print("✨Final Response(See FinalAnswer): " + response)

    response, _ = agent.text_completion(
        text='What is today date? Are US stocks up or down? Please give me the specific data.',
        history=[])
    print("✨Final Response(See FinalAnswer): " + response)
