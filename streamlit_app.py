import streamlit as st
from core.app import run_agent_with_tools, ROLLING_MEMORY_WINDOW, build_agent_graph
from langchain_core.messages import HumanMessage

st.title("🎩 Alfred - Your AI Assistant")

# Initialize the agent
if "agent" not in st.session_state:
    with st.spinner("🔧 Initializing Alfred..."):
        st.session_state["agent"] = build_agent_graph()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = []

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
        
        # Run the agent using the built graph
        try:
            # Use the pre-built agent from session state
            agent_response = st.session_state["agent"].invoke({"messages": st.session_state["messages"]})
            # Get the final response from the agent
            final_response = agent_response["messages"][-1].content
            message_placeholder.markdown(final_response)
            # Update session state with all new messages
            st.session_state["messages"] = agent_response["messages"]
        except Exception as e:
            st.error(f"Error: {str(e)}")
            message_placeholder.markdown("I apologize, but I encountered an error. Please try again.")