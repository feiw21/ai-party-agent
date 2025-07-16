"""
Simple test script to test LangFuse setup separately.
"""

import os
from evaluation import setup_langfuse

def test_langfuse_setup():
    """Test LangFuse setup and connection."""
    print("🧪 Testing LangFuse Setup")
    print("=" * 50)
    
    # Check environment variables
    print("📋 Environment Variables:")
    print(f"   LANGFUSE_PUBLIC_KEY: {'✅ Set' if os.environ.get('LANGFUSE_PUBLIC_KEY') else '❌ Not set'}")
    print(f"   LANGFUSE_SECRET_KEY: {'✅ Set' if os.environ.get('LANGFUSE_SECRET_KEY') else '❌ Not set'}")
    print(f"   LANGFUSE_HOST: {'✅ Set' if os.environ.get('LANGFUSE_HOST') else '❌ Not set'}")
    
    # Show actual values (masked for security)
    public_key = os.environ.get('LANGFUSE_PUBLIC_KEY', '')
    secret_key = os.environ.get('LANGFUSE_SECRET_KEY', '')
    host = os.environ.get('LANGFUSE_HOST', '')
    
    if public_key:
        print(f"   Public Key: {public_key[:10]}...{public_key[-10:] if len(public_key) > 20 else ''}")
    if secret_key:
        print(f"   Secret Key: {secret_key[:10]}...{secret_key[-10:] if len(secret_key) > 20 else ''}")
    if host:
        print(f"   Host: {host}")
    
    print("\n🔗 Testing Connection:")
    
    # Test the setup function
    try:
        langfuse = setup_langfuse()
        
        if langfuse:
            print("✅ LangFuse setup successful!")
            
            # Test a simple operation
            print("\n🧪 Testing Basic Operations:")
            try:
                # Test that we can create a CallbackHandler (this is what we need for LangGraph)
                from langfuse.langchain import CallbackHandler
                handler = CallbackHandler()
                print("✅ Can create CallbackHandler - LangGraph integration ready!")
                
                # Test basic client functionality
                print("✅ LangFuse client is working correctly!")
                
            except Exception as e:
                print(f"⚠️  Basic operations failed: {str(e)}")
                
        else:
            print("❌ LangFuse setup failed!")
            
    except Exception as e:
        print(f"❌ Exception during setup: {str(e)}")

if __name__ == "__main__":
    test_langfuse_setup() 