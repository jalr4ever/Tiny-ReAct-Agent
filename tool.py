import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()

"""
Tool Functions

- First, add the description of the tool in `tools`.
- Then, add the specific implementation of the tool in `tools`.

"""


class Tools:
    def __init__(self) -> None:
        self.toolConfig = self._tools()

    def _tools(self):
        tools = [
            {
                'name_for_human': 'Exa Search',
                'name_for_model': 'exa_search',
                'description_for_model': 'Exa.ai Search is a powerful search engine that can be used to access the internet, query the latest research developments, stay updated with current news, and more.',
                'parameters': [
                    {
                        'name': 'search_query',
                        'description': 'Search for keywords or phrases',
                        'required': True,
                        'schema': {'type': 'string'},
                    }
                ],
            }
        ]
        return tools

    def exa_search(self, search_query: str):
        url = "https://api.exa.ai/answer"

        payload = json.dumps({
            "query": search_query,
            "text": True
        })
        headers = {
            'Authorization': f'Bearer {os.getenv("EXA-API-KEY")}',
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload).json()
        return response["answer"]
