import streamlit as st
import asyncio
import threading
import sys
import os

# Add the src directory to the path to make imports work
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from client import MCPClient
from typing import Optional
from utils import run_async

# Initialize session state
if "client" not in st.session_state:
    st.session_state.client = None
if "connected" not in st.session_state:
    st.session_state.connected = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "tools_info" not in st.session_state:
    st.session_state.tools_info = None


def process_query(user_input: str):
     with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response, should_continue, detection_result = run_async(st.session_state.client.process_query(user_input))
                    
                    # Process response parts
                    response_text = ""
                    thought_text = ""
                    
                    for part in response.candidates[0].content.parts:
                        if not part.text:
                            continue
                        if hasattr(part, 'thought') and part.thought:
                            thought_text += part.text + "\n"
                        else:
                            response_text += part.text + "\n"
                    
                    # Display thought if available
                    if thought_text.strip():
                        with st.expander("🧠 AI Thoughts", expanded=False):
                            st.write(thought_text.strip())
                    
                    # Display main response
                    if response_text.strip():
                        st.write(response_text.strip())
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": response_text.strip()
                        })
                    else:
                        st.write("No response generated.")
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": "No response generated."
                        })
                    
                    return response, should_continue, detection_result

                except Exception as e:
                    error_msg = f"Error processing query: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": error_msg
                    })

                    return error_msg, False, None

        
# Streamlit app
st.title("🤖 MCP Client Interface")
st.markdown("Connect to your MCP server and chat with Gemini AI")

# Sidebar for connection and tools info
with st.sidebar:
    st.header("Connection")
    
    server_url = st.text_input(
        "MCP Server URL", 
        value="http://127.0.0.1:9000/mcp",
        help="Enter the URL of your MCP server"
    )
    
    if st.button("Connect to Server", type="primary"):
        with st.spinner("Connecting to MCP server..."):
            try:
                st.session_state.client = MCPClient()
                st.session_state.connected = run_async(
                    st.session_state.client.connect_to_server(server_url)
                )
                
                if st.session_state.connected:
                    st.session_state.tools_info = st.session_state.client.get_tools_info()
                    st.success("✅ Connected successfully!")
                    
                    # Get initial greeting
                    with st.spinner("Getting initial message..."):
                        initial_msg = run_async(st.session_state.client.get_initial_message())
                        st.session_state.messages = [
                            {"role": "assistant", "content": initial_msg}
                        ]
                else:
                    st.error("❌ Failed to connect to server")
                    
            except Exception as e:
                st.error(f"❌ Connection error: {str(e)}")
                st.session_state.connected = False
    
    # Connection status
    if st.session_state.connected:
        st.success("🟢 Connected")
    else:
        st.error("🔴 Disconnected")
    
    # Tools information
    if st.session_state.tools_info:
        st.header("Available Tools")
        with st.expander("View Tools", expanded=False):
            for tool in st.session_state.tools_info:
                st.markdown(f"**{tool.name}**")
                if hasattr(tool, 'description') and tool.description:
                    st.caption(tool.description)
                st.divider()
    
    # Disconnect button
    if st.session_state.connected and st.button("Disconnect"):
        try:
            if st.session_state.client:
                run_async(st.session_state.client.cleanup())
            st.session_state.connected = False
            st.session_state.client = None
            st.session_state.tools_info = None
            st.rerun()
        except Exception as e:
            st.error(f"Error during disconnect: {str(e)}")

# Main chat interface
if st.session_state.connected:
    st.header("💬 Chat")
    
    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.write(message["content"])
            else:
                with st.chat_message("assistant"):
                    st.write(message["content"])
    
    # Chat input
    user_input = st.chat_input("Type your message here...")
    
    if user_input:
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Display user message immediately
        with st.chat_message("user"):
            st.write(user_input)
        
        # Get AI response
        should_continue = True
        while should_continue:
            response, should_continue, detection_result = process_query(user_input)
        
    # Clear chat button
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        if st.session_state.client:
            st.session_state.client.messages = []
        st.rerun()

else:
    st.info("👆 Please connect to your MCP server using the sidebar to start chatting.")
    
    st.markdown("""
    ## Getting Started
    
    1. **Start your MCP server** - Make sure your MCP server is running on the specified URL
    2. **Connect** - Use the sidebar to connect to your server
    3. **Chat** - Once connected, you can start chatting with the AI assistant
    
    ### Features
    - 💬 **Real-time chat** with Gemini AI
    - 🛠️ **Tool integration** via MCP protocol
    - 🧠 **AI thoughts** display (when available)
    - 📋 **Tools information** in sidebar
    - 🗑️ **Clear chat** functionality
    """)