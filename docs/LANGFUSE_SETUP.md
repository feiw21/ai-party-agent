# LangFuse US Cloud Setup Guide

This guide helps you set up LangFuse with the US cloud instance for Alfred AI Agent monitoring and evaluation.

## 1. Get Your LangFuse US Cloud Credentials

1. Go to [https://us.cloud.langfuse.com](https://us.cloud.langfuse.com)
2. Sign up or log in to your account
3. Navigate to your project settings
4. Copy your API keys:
   - **Public Key** (starts with `pk-`)
   - **Secret Key** (starts with `sk-`)

## 2. Set Environment Variables

Add these to your `~/.zshrc` file:

```bash
# LangFuse US Cloud Configuration
export LANGFUSE_PUBLIC_KEY="pk-your-public-key-here"
export LANGFUSE_SECRET_KEY="sk-your-secret-key-here"
export LANGFUSE_HOST="https://us.cloud.langfuse.com"
```

## 3. Reload Your Shell

```bash
source ~/.zshrc
```

## 4. Test the Setup

Run the test script to verify everything is working:

```bash
python test_langfuse.py
```

You should see:
- ✅ All environment variables set
- ✅ LangFuse client authenticated and ready
- ✅ Can fetch and create traces

## 5. Run Alfred with Monitoring

Now you can run Alfred with full tracing and monitoring:

```bash
# Run evaluation
python evaluation.py

# Or use the Streamlit app with monitoring
streamlit run streamlit_app.py
```

## 6. View Your Traces

Visit [https://us.cloud.langfuse.com](https://us.cloud.langfuse.com) to see:
- Real-time traces of Alfred's conversations
- Performance metrics and execution times
- Tool usage patterns
- User feedback and ratings

## Troubleshooting

### "LangFuse credentials not found"
- Make sure you've added the environment variables to `~/.zshrc`
- Run `source ~/.zshrc` to reload
- Check that the keys are correct

### "Authentication failed"
- Verify your API keys are correct
- Make sure you're using the US cloud instance
- Check that your LangFuse account is active

### "Connection timeout"
- Ensure you have internet access
- The US cloud instance should be accessible from most locations
- Try running `ping us.cloud.langfuse.com` to test connectivity 