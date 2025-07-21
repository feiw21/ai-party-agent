import streamlit as st
from core.app import run_agent_with_tools
from langchain_core.messages import HumanMessage

st.title("🎩 Alfred - Your AI Assistant")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Display chat messages from history
for message in st.session_state["messages"]:
    with st.chat_message(message.type):
        st.markdown(message.content)

# Accept user input
if prompt := st.chat_input("What would you like to know?"):
    # Display user message in chat message container
    with st.chat_message("human"):
        st.markdown(prompt)
    
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            # Add user message to conversation history
            current_messages = st.session_state["messages"] + [HumanMessage(content=prompt)]
            
            # Use the simplified function to process the messages
            updated_conversation = run_agent_with_tools(current_messages)
            
            # Get the final response (last message in conversation)
            final_response = updated_conversation[-1].content
            message_placeholder.markdown(final_response)
            
            # Update session state with the complete conversation
            st.session_state["messages"] = updated_conversation
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
            message_placeholder.markdown("I apologize, but I encountered an error. Please try again.")