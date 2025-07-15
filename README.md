# 🎩 Alfred - AI Party Agent

An AI assistant that helps you prepare for conversations with party guests by combining web search, guest information, and smart reasoning.

## ✨ What Alfred Does

- **🤖 Smart Conversations**: Powered by OpenAI GPT-4
- **🔍 Web Search**: Real-time information from DuckDuckGo
- **📊 Guest Info**: Access to party guest data
- **🌐 Web Interface**: Easy-to-use Streamlit chat

## 🚀 Quick Start

### What You Need
- Python 3.8+
- OpenAI API key ([get one here](https://platform.openai.com/api-keys))

### Setup
```bash
git clone https://github.com/feiw21/ai-party-agent.git
cd ai-party-agent
pip install -r requirements.txt
export OPENAI_API_KEY="your-key-here"
streamlit run streamlit_app.py
```

Open `http://localhost:8501` and start chatting!

## 🎯 Examples

**"Tell me about Dr. Nikola Tesla"**
→ Alfred provides background info and conversation topics

**"What are the latest developments in wireless energy?"**
→ Alfred searches the web for current news

**"Help me prepare for a conversation with Dr. Tesla about tech trends"**
→ Alfred combines guest info with current tech news

## 📁 Project Structure

```
ai-party-agent/
├── app.py                 # Main agent logic
├── streamlit_app.py       # Web interface
├── tools.py               # Search and info tools
├── retriever.py           # Guest data retrieval
├── invitees/              # Guest dataset
└── docs/                  # Setup and architecture guides
```

## 🛠️ Configuration

Change the model in `app.py`:
```python
llm = OpenAILLM(model="gpt-4")  # or "gpt-3.5-turbo"
```

## 📖 Documentation

- [Setup Guide](docs/setup.md) - Get started in 5 minutes
- [How It Works](docs/architecture.md) - Simple technical overview

---

**Happy party planning with Alfred! 🎉** 