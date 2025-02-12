from LLM import OpenAIChat
import json5

from tool import Tools

TOOL_DESC = """{name_for_model}: Call this tool to interact with the {name_for_human} API. What is the {name_for_human} API useful for? {description_for_model} Parameters: {parameters} Format the arguments as a JSON object."""
REACT_PROMPT = """Answer the following questions as best you can. You have access to the following tools:

{tool_descs}

Use the following JSON format:
{
  "Question": "The input question you must answer",
  "Thought": "Think what todo, you can use tool when you encounter difficulties. keep Action null if you don't need to invoke tool",
  "Action": "The action to take, should be one of [{tool_names}]",
  "ActionInput": "the input to the action",
  "Observation": "the result of the action"
  "Thought": "I now know the final answer",
  "FinalAnswer": "the final answer to the original input question"
}

Note: This Thought/Action/Action Input/Observation can be repeated zero or more times.
Note: When it comes to the current or latest date, you should use a tool.

Now Begin!
"""


class Agent:
    def __init__(self, path: str = '') -> None:
        self.path = path
        self.tool = Tools()
        self.system_prompt = self.build_system_input()
        self.model = OpenAIChat()

    def build_system_input(self):
        tool_descs, tool_names = [], []
        for tool in self.tool.toolConfig:
            tool_descs.append(TOOL_DESC.format(**tool))
            tool_names.append(tool['name_for_model'])
        tool_descs = '\n\n'.join(tool_descs)
        tool_names = ','.join(tool_names)
        # sys_prompt = REACT_PROMPT.format(tool_descs=tool_descs, tool_names=tool_names)
        sys_prompt = REACT_PROMPT.replace('{tool_descs}', tool_descs)
        sys_prompt = sys_prompt.replace('{tool_names}', tool_names)
        return sys_prompt

    def parse_latest_plugin_call(self, text):
        plugin_name, plugin_args = '', ''
        text_d = json5.loads(text)
        action = text_d['Action']
        action_input = text_d['ActionInput']
        # if there's an action call
        if action and action_input:
            plugin_name = action
            plugin_args = action_input
            text = {
                "Question": text_d['Question'],
                "Thought": text_d['Thought'],
                "Action": text_d['Action'],
                "ActionInput": text_d['ActionInput'],
            }
        return plugin_name, plugin_args, text

    def call_plugin(self, plugin_name, plugin_args):
        plugin_args = {
            "search_query" : plugin_args
        }
        if plugin_name == 'exa_search':
            return self.tool.exa_search(**plugin_args)

    def text_completion(self, text, history=[]):
        text = "\nQuestion:" + text
        response, his = self.model.chat(text, history, self.system_prompt)
        # print(response)
        plugin_name, plugin_args, response = self.parse_latest_plugin_call(response)
        if plugin_name:
            response["Observation"] = self.call_plugin(plugin_name, plugin_args)
        response, his = self.model.chat(str(response), history, self.system_prompt)
        return response, his


if __name__ == '__main__':
    agent = Agent()
    prompt = agent.build_system_input()
    print(prompt)

    response, _ = agent.text_completion(text='Hello', history=[])
    print(">>> Final Response(See FinalAnswer): " + response)

    response, _ = agent.text_completion(text='What is the weather like in Shenzhen, China today?', history=[])
    print(">>> Final Response(See FinalAnswer)" + response)

    response, _ = agent.text_completion(text='What is the date today? What is today date? Are US stocks up or down? Please give me the specific data.', history=[])
    print(">>> Final Response(See FinalAnswer)" + response)
