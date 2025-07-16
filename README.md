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

#### 1. Get the Code
```bash
git clone https://github.com/feiw21/ai-party-agent.git
cd ai-party-agent
```

#### 2. Create a Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Set Up Environment Variables

**Option A: Export in Terminal (Temporary)**
```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

**Option B: Create .env File (Recommended)**
```bash
# Create .env file
echo "OPENAI_API_KEY=your-openai-api-key-here" > .env
```

**Option C: Add to Shell Profile (Permanent)**
Add to your `~/.zshrc`:
```bash
echo 'export OPENAI_API_KEY="your-openai-api-key-here"' >> ~/.zshrc
```

#### 5. Verify Installation
```bash
# Test Python imports
python -c "import openai, streamlit, langgraph; print('✅ All imports successful!')"

# Test OpenAI connection (optional)
python -c "import openai; openai.api_key='$OPENAI_API_KEY'; print('✅ OpenAI API key configured!')"
```

## 🌐 Running the Application

### Start the Streamlit App
```bash
streamlit run streamlit_app.py
```
The app will open automatically in your browser at `http://localhost:8501`

### Alternative: Run from Python
```bash
python app.py
```
This will run a test conversation with Alfred.

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
└── docs/                  # Architecture guide
```

## 🛠️ Configuration

### Change the Model
In `app.py`:
```python
llm = ChatOpenAI(model="gpt-4")  # or "gpt-3.5-turbo"
```

### Adjust Memory
```python
ROLLING_MEMORY_WINDOW = 50  # messages to remember
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### 2. OpenAI API Key Issues
```bash
# Check if API key is set
echo $OPENAI_API_KEY

# Test API connection
python -c "import openai; openai.api_key='$OPENAI_API_KEY'; print(openai.Model.list())"
```

#### 3. Streamlit Port Issues
```bash
# Use a different port
streamlit run streamlit_app.py --server.port 8502
```

#### 4. Memory Issues
- Reduce `ROLLING_MEMORY_WINDOW` in `app.py`
- Use a smaller model like `gpt-3.5-turbo`

## 📖 Documentation

- [How It Works](docs/architecture.md) - Simple technical overview

---

**Happy party planning with Alfred! 🎉** 