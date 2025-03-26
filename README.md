# Overview

Inspired by [Tiny-Agent](https://github.com/KMnO4-zx/TinyAgent).

A tiny agent based on [ReAct](https://arxiv.org/abs/2210.03629), OpenAI API compatible, with built-in search capabilities.

The purpose is to better understand the principles and implementation of [ReAct](https://arxiv.org/abs/2210.03629).

This agent shows:
```mermaid
sequenceDiagram
    participant User
    participant LLM
    participant Tool

    User->>LLM: Input Question
    Note over LLM: Parse Question into ReAct Format
    
    loop Think & Act Process
        LLM->>LLM: Generate Thought
        alt Needs Tool
            LLM->>Tool: Action & ActionInput
            Tool->>LLM: Return Observation
            LLM->>LLM: Process Observation
        else No Tool Needed
            LLM->>LLM: Direct Thinking
        end
    end
    
    LLM->>LLM: Generate Final Thought
    LLM->>User: Return FinalAnswer
```

# Motivation

- More trendy: [Tiny-Agent](https://github.com/KMnO4-zx/TinyAgent) used local models, but this one will utilize online models, and any OpenAI-compatible model provider can be used.
- Easier to understand: Agent system prompt has been optimized for a clearer LLM interaction process.

# Setup & Executing

Apply `Exa.ai` API Key for Web Search: https://dashboard.exa.ai/api-keys

Add .env to the project according to .env.template and fill in your OPENAI & Search Tool service provider information.

Setup environment：

```bash
conda create -n tiny-react-agent python=3.11
pip install -r requirements.txt
python agent.py
```

Output Example:
```bash
(tiny-react-agent) L@Warren-MBP Tiny-OAI-Agent % python agent.py
Enter your question (type 'exit' to quit): hi

👨‍🍳: hi
🤖Step log...[Thinking]: None; [Action]: None
✨Final Response: Hello! How can I assist you today?

Enter your question (type 'exit' to quit): How's the wearther today in China ShenZhen?

👨‍🍳: How's the wearther today in China ShenZhen?
🤖Step log...[Thinking]: I need to find the current weather in Shenzhen, China.; [Action]: exa_search
🤖Step log...[Thinking]: The current weather in Shenzhen, China is 72°F according to the provided AccuWeather link.; [Action]: None
✨Final Response: The current weather in Shenzhen, China is 72°F.

Enter your question (type 'exit' to quit): Please turn F to C

👨‍🍳: Please turn F to C
🤖Step log...[Thinking]: I need to convert 72 degrees Fahrenheit to Celsius.; [Action]: FinalAnswer
✨Final Response: The temperature 72°F is approximately 22.2°C.

Enter your question (type 'exit' to quit): What is today date? Are US stocks up or down? Please give me the specific data.

👨‍🍳: What is today date? Are US stocks up or down? Please give me the specific data.
🤖Step log...[Thinking]: I need to find out today's date and check the current status of US stock markets.; [Action]: exa_search
🤖Step log...[Thinking]: US stock markets specific data can change rapidly within a single day, so I'll perform a search to gather the latest information.; [Action]: exa_search
🤖Step log...[Thinking]: I have determined the current date and gathered information on US stocks from the latest market trading period.; [Action]: None
✨Final Response: Today's date is March 26, 2025.

As of the last trading day on March 25, 2025, the U.S. stock market showed mixed results:
- The S&P 500 gained 0.13%.
- The Nasdaq Composite gained 0.32%.
- The Dow Jones Industrial Average rose by 0.04%.

Enter your question (type 'exit' to quit): exit
```

**Note**:
Running agent might encounter errors, as **ReAct doesn't guarantee stable Agent operation**. To reduce the probability of errors, it's recommended to use a more powerful model, such as gpt-4o (default), or other SOTA models of similar capability.
