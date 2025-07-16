"""
Enhanced Streamlit app for Alfred AI Agent with LangFuse evaluation integration.
This provides both the original chat functionality and evaluation capabilities.
"""

import streamlit as st
import time
from langchain_core.messages import HumanMessage

from core.app import run_agent_with_tools, ROLLING_MEMORY_WINDOW, build_agent_graph
from evaluation.evaluation import AlfredEvaluator, record_user_feedback, list_recent_traces

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="🎩 Alfred - AI Party Agent (with Evaluation)",
    page_icon="🎩",
    layout="wide"
)

# ============================================================================
# SIDEBAR CONFIGURATION
# ============================================================================
st.sidebar.title("🎩 Alfred Control Panel")

# Mode selection
mode = st.sidebar.selectbox(
    "Choose Mode:",
    ["💬 Chat Mode", "🧪 Evaluation Mode", "📊 Monitoring Dashboard"]
)

# ============================================================================
# INITIALIZATION
# ============================================================================
# Initialize components
if "agent" not in st.session_state:
    with st.spinner("🔧 Initializing Alfred..."):
        st.session_state["agent"] = build_agent_graph()

if "evaluator" not in st.session_state:
    with st.spinner("🔧 Setting up evaluation..."):
        st.session_state["evaluator"] = AlfredEvaluator()

if "messages" not in st.session_state:
    st.session_state["messages"] = []

# ============================================================================
# CHAT MODE
# ============================================================================
if mode == "💬 Chat Mode":
    st.title("🎩 Alfred - Your AI Assistant")
    
    # Display chat messages from history
    for message in st.session_state["messages"]:
        with st.chat_message(message.type):
            st.markdown(message.content)
    
    # Accept user input
    if prompt := st.chat_input("What would you like to know?"):
        # Add user message to chat history
        st.session_state["messages"].append(HumanMessage(content=prompt))
        
        # Display user message in chat message container
        with st.chat_message("human"):
            st.markdown(prompt)
        
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            
            # Run the agent with evaluation
            try:
                # Use evaluator for tracing
                result = st.session_state["evaluator"].trace_conversation(
                    user_input=prompt,
                    user_id="streamlit-user",
                    session_id=f"session-{int(time.time())}",
                    metadata={"interface": "streamlit", "mode": "chat"}
                )
                
                # Display response
                message_placeholder.markdown(result["response"])
                
                # Update session state with new messages
                if result.get("success"):
                    # Add AI response to session state
                    from langchain_core.messages import AIMessage
                    st.session_state["messages"].append(AIMessage(content=result["response"]))
                    
                    # Store trace info for feedback
                    st.session_state["last_trace_id"] = result.get("trace_id")
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
                message_placeholder.markdown("I apologize, but I encountered an error. Please try again.")
    
    # User feedback section
    if "last_trace_id" in st.session_state and st.session_state["evaluator"].langfuse:
        st.markdown("---")
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown("**How was this response?**")
        
        with col2:
            if st.button("👍 Good"):
                record_user_feedback(
                    st.session_state["evaluator"].langfuse,
                    st.session_state["last_trace_id"],
                    5,
                    "user-rating"
                )
                st.success("Thanks for your feedback!")
        
        with col3:
            if st.button("👎 Poor"):
                record_user_feedback(
                    st.session_state["evaluator"].langfuse,
                    st.session_state["last_trace_id"],
                    1,
                    "user-rating"
                )
                st.error("Thanks for your feedback!")

# ============================================================================
# EVALUATION MODE
# ============================================================================
elif mode == "🧪 Evaluation Mode":
    st.title("🧪 Alfred Evaluation Mode")
    
    # Evaluation controls
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Test Cases")
        
        # Predefined test cases
        test_cases = [
            "Tell me about Dr. Nikola Tesla",
            "What are the latest developments in wireless energy?",
            "Help me prepare for a conversation with Dr. Tesla about tech trends",
            "Who is Marie Curie and what should I know about her?",
            "What are the current trends in renewable energy?"
        ]
        
        selected_tests = st.multiselect(
            "Select test cases to run:",
            test_cases,
            default=test_cases[:3]
        )
        
        if st.button("🚀 Run Evaluation"):
            if selected_tests:
                with st.spinner("Running evaluation..."):
                    from evaluation import run_evaluation
                    results = run_evaluation(st.session_state["evaluator"], selected_tests)
                    
                    # Store results
                    st.session_state["evaluation_results"] = results
    
    with col2:
        st.subheader("📊 Quick Stats")
        
        if "evaluation_results" in st.session_state:
            results = st.session_state["evaluation_results"]
            
            # Display metrics
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Success Rate", f"{results['success_rate']:.1%}")
                st.metric("Total Tests", results['total_tests'])
            
            with col_b:
                st.metric("Avg Time", f"{results['average_execution_time']:.2f}s")
                st.metric("Total Time", f"{results['total_execution_time']:.2f}s")
    
    # Display detailed results
    if "evaluation_results" in st.session_state:
        st.subheader("📋 Detailed Results")
        
        results = st.session_state["evaluation_results"]
        
        for i, result in enumerate(results["results"], 1):
            with st.expander(f"Test {i}: {result.get('response', 'No response')[:50]}..."):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Query:**", selected_tests[i-1])
                    st.write("**Response:**", result.get("response", "No response"))
                
                with col2:
                    st.write("**Execution Time:**", f"{result.get('execution_time', 0):.2f}s")
                    st.write("**Success:**", "✅" if result.get("success") else "❌")
                    if result.get("trace_id"):
                        st.write("**Trace ID:**", result["trace_id"])

# ============================================================================
# MONITORING DASHBOARD
# ============================================================================
elif mode == "📊 Monitoring Dashboard":
    st.title("📊 Alfred Monitoring Dashboard")
    
    if st.session_state["evaluator"].langfuse:
        # LangFuse Status and Information
        st.subheader("🔗 LangFuse Connection Status")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.success("✅ Connected")
            st.write("**Host:**", "us.cloud.langfuse.com")
        
        with col2:
            st.info("📊 Traces")
            st.write("**Status:**", "Auto-generated")
            st.write("**Method:**", "CallbackHandler")
        
        with col3:
            st.info("⭐ Scores")
            st.write("**Status:**", "User feedback")
            st.write("**Method:**", "create_score()")
        
        # Instructions for viewing data
        st.subheader("📋 How to View Your Data")
        
        st.markdown("""
        **To see your traces and scores in LangFuse:**
        
        1. **Visit:** [https://us.cloud.langfuse.com](https://us.cloud.langfuse.com)
        2. **Login** to your account
        3. **Navigate to:**
           - **Traces tab** → See all conversation traces
           - **Scores tab** → See all user feedback scores
           - **Metrics tab** → See performance analytics
        
        **Recent Activity:**
        - Each conversation turn creates a new trace
        - User feedback (👍/👎) creates scores
        - All data is automatically flushed to LangFuse
        """)
        
        # Test connection
        st.subheader("🧪 Test Connection")
        
        if st.button("🔄 Test LangFuse Connection"):
            try:
                # Test basic operations
                test_trace = st.session_state["evaluator"].langfuse.traces.create(
                    name="test-connection",
                    input={"test": "streamlit connection"},
                    output={"status": "success"}
                )
                
                # Test score creation
                st.session_state["evaluator"].langfuse.create_score(
                    trace_id=test_trace.id,
                    name="test-score",
                    value=5,
                    data_type="NUMERIC",
                    comment="Test from Streamlit"
                )
                
                # Flush data
                st.session_state["evaluator"].langfuse.flush()
                
                st.success(f"✅ Connection test successful! Trace ID: {test_trace.id}")
                st.info("💡 Check your LangFuse dashboard to see this test trace and score!")
                
            except Exception as e:
                st.error(f"❌ Connection test failed: {str(e)}")
        
        # Manual flush option
        st.subheader("📤 Manual Data Flush")
        
        if st.button("🔄 Flush All Data"):
            try:
                st.session_state["evaluator"].langfuse.flush()
                st.success("✅ All data flushed to LangFuse!")
            except Exception as e:
                st.error(f"❌ Flush failed: {str(e)}")
        
    else:
        st.warning("⚠️ LangFuse not configured. Please set up your API keys to see monitoring data.")

# ============================================================================
# SIDEBAR UTILITIES
# ============================================================================
# Clear conversation button
if st.sidebar.button("🗑️ Clear Conversation"):
    st.session_state["messages"] = []
    st.rerun()

# Export conversation
if st.sidebar.button("📤 Export Conversation"):
    if st.session_state["messages"]:
        conversation_text = "\n\n".join([
            f"{msg.type}: {msg.content}" 
            for msg in st.session_state["messages"]
        ])
        
        st.sidebar.download_button(
            label="📥 Download Conversation",
            data=conversation_text,
            file_name=f"alfred_conversation_{int(time.time())}.txt",
            mime="text/plain"
        )

# LangFuse status
st.sidebar.markdown("---")
if st.session_state["evaluator"].langfuse:
    st.sidebar.success("✅ LangFuse Connected")
    
    # Add flush button to ensure scores are sent
    if st.sidebar.button("🔄 Flush LangFuse Data"):
        try:
            st.session_state["evaluator"].langfuse.flush()
            st.sidebar.success("✅ Data flushed to LangFuse!")
        except Exception as e:
            st.sidebar.error(f"❌ Flush failed: {str(e)}")
else:
    st.sidebar.error("❌ LangFuse Not Connected")
    st.sidebar.info("💡 Set LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY in ~/.zshrc")

# Add proper cleanup on app shutdown
import atexit

def cleanup_langfuse():
    """Cleanup function to flush LangFuse data on shutdown"""
    try:
        if "evaluator" in st.session_state and st.session_state["evaluator"].langfuse:
            st.session_state["evaluator"].langfuse.flush()
            print("✅ LangFuse data flushed on shutdown")
    except Exception as e:
        print(f"⚠️  LangFuse cleanup failed: {str(e)}")

# Register cleanup function
atexit.register(cleanup_langfuse) 