import streamlit as st
import asyncio
import sys
import os
from typing import Optional, Tuple, Any
from dataclasses import dataclass
import re

# Add the src directory to the path to make imports work
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from client import MCPClient
from utils import run_async


@dataclass
class AppState:
    """Centralized state management for the application."""
    client: Optional[MCPClient] = None
    connected: bool = False
    messages: list = None
    tools_info: Optional[list] = None
    
    def __post_init__(self):
        if self.messages is None:
            self.messages = []


class MCPClientApp:
    """Main application class for the MCP Client Interface."""
    
    def __init__(self):
        self.init_session_state()
        self.max_session_turns = 3  # Max turns for auto continuation

    def init_session_state(self):
        """Initialize Streamlit session state with default values."""
        defaults = {
            "client": None,
            "connected": False,
            "messages": [],
            "tools_info": None
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    def connect_to_server(self, server_url: str) -> bool:
        """
        Establish connection to MCP server.
        
        Args:
            server_url: URL of the MCP server
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            with st.spinner("Connecting to MCP server..."):
                st.session_state.client = MCPClient()
                st.session_state.connected = run_async(
                    st.session_state.client.connect_to_server(server_url)
                )
                
                if st.session_state.connected:
                    st.session_state.tools_info = st.session_state.client.get_tools_info()
                    self._get_initial_message()
                    st.success("✅ Connected successfully!")
                    return True
                else:
                    st.error("❌ Failed to connect to server")
                    return False
                    
        except Exception as e:
            st.error(f"❌ Connection error: {str(e)}")
            st.session_state.connected = False
            return False
    
    def _get_initial_message(self):
        """Fetch and store initial greeting message."""
        try:
            with st.spinner("Getting initial message..."):
                initial_msg = run_async(st.session_state.client.get_initial_message())
                st.session_state.messages = [
                    {"role": "assistant", "content": initial_msg}
                ]
        except Exception as e:
            st.warning(f"Could not fetch initial message: {str(e)}")
    
    def disconnect_from_server(self):
        """Clean up and disconnect from server."""
        try:
            if st.session_state.client:
                run_async(st.session_state.client.cleanup())
            
            # Reset state
            st.session_state.connected = False
            st.session_state.client = None
            st.session_state.tools_info = None
            st.rerun()
            
        except Exception as e:
            st.error(f"Error during disconnect: {str(e)}")

    def process_query(self, user_input: str, check_continue: bool=True) -> Tuple[Any, bool, Any]:
        """
        Process user query and return response.
        
        Args:
            user_input: User's input message
            
        Returns:
            Tuple of (response, should_continue, detection_result)
        """
        try:
            response, should_continue, detection_result = run_async(
                st.session_state.client.process_query(user_input, check_continue)
            )
            
            response_text, thought_text = self._extract_response_parts(response)
            
            # Display thought if available
            if thought_text.strip():
                with st.expander("🧠 AI Thoughts", expanded=False):
                    st.write(thought_text.strip())

            # check is image
            json_match = re.search(r"```json\s*({.*?})\s*```", response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                json_data = st.session_state.client.check_json(json_str)
            else:
                json_data = st.session_state.client.check_json(response_text)

            if json_data:
                content = json_data.get("text", "")
                image_path = json_data.get("image_path", "")
                st.write(content)
                st.image(image_path)
            else:
                content = response_text.strip() if response_text.strip() else "No response generated."
                st.write(content)

            st.session_state.messages.append({
                "role": "assistant", 
                "content": response_text if json_data else content
            })
            
            return response, should_continue, detection_result
            
        except Exception as e:
            error_msg = f"Error processing query: {str(e)}"
            st.error(error_msg)
            # st.session_state.messages.append({
            #     "role": "assistant", 
            #     "content": error_msg
            # })
            return error_msg, False, None
    
    def _extract_response_parts(self, response) -> Tuple[str, str]:
        """
        Extract response and thought text from response object.
        
        Args:
            response: Response object from client
            
        Returns:
            Tuple of (response_text, thought_text)
        """
        response_text = ""
        thought_text = ""
        
        if hasattr(response, 'candidates') and response.candidates:
            for part in response.candidates[0].content.parts:
                if not part.text:
                    continue
                if hasattr(part, 'thought') and part.thought:
                    thought_text += part.text + "\n"
                else:
                    response_text += part.text + "\n"
        
        return response_text, thought_text
    
    def render_sidebar(self):
        """Render the sidebar with connection controls and tools info."""
        with st.sidebar:
            self._render_connection_section()
            self._render_tools_section()
            self._render_disconnect_section()
    
    def _render_connection_section(self):
        """Render connection controls in sidebar."""
        st.header("Connection")
        
        server_url = st.text_input(
            "MCP Server URL", 
            value="http://127.0.0.1:9000/mcp",
            help="Enter the URL of your MCP server"
        )
        
        if st.button("Connect to Server", type="primary"):
            self.connect_to_server(server_url)
        
        # Connection status indicator
        if st.session_state.connected:
            st.success("🟢 Connected")
        else:
            st.error("🔴 Disconnected")
    
    def _render_tools_section(self):
        """Render available tools section in sidebar."""
        if st.session_state.tools_info:
            st.header("Available Tools")
            with st.expander("View Tools", expanded=False):
                for tool in st.session_state.tools_info:
                    st.markdown(f"**{tool.name}**")
                    if hasattr(tool, 'description') and tool.description:
                        st.caption(tool.description)
                    st.divider()
    
    def _render_disconnect_section(self):
        """Render disconnect button in sidebar."""
        if st.session_state.connected and st.button("Disconnect"):
            self.disconnect_from_server()
    
    def render_chat_interface(self):
        """Render the main chat interface."""
        if not st.session_state.connected:
            self._render_welcome_screen()
            return
        
        st.header("💬 Chat")
        
        # Display chat history
        self._render_chat_history()
        
        # Handle new user input
        self._handle_user_input()
        
        # Clear chat button
        if st.button("🗑️ Clear Chat"):
            self.clear_chat()
    
    def _render_chat_history(self):
        """Render existing chat messages."""
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.messages:
                role = message["role"]
                content = message["content"]
                
                with st.chat_message(role):
                    st.write(content)
    
    def _handle_user_input(self):
        """Handle new user input and generate responses."""
        user_input = st.chat_input("Type your message here...")
        
        if user_input:
            # Add user message to chat
            st.session_state.messages.append({
                "role": "user", 
                "content": user_input
            })
            
            # Display user message immediately
            with st.chat_message("user"):
                st.write(user_input)
            
            # Process query with continuation loop
            self._process_with_continuation(user_input)
    
    def _process_with_continuation(self, user_input: str):
        """Process query with continuation support."""
        counter = 0
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                should_continue = True
                while should_continue and counter < self.max_session_turns:
                    response, should_continue, detection_result = self.process_query(user_input)
                    user_input = "If you have any unfinished tasks, please continue working on them. \
                                If you’re unsure about anything in my instructions, you can use available tools—such \
                                as listing all files, listing all columns, or retrieving unique values to help clarify my input."
                    counter += 1


    def _render_welcome_screen(self):
        """Render welcome screen when not connected."""
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
    
    def clear_chat(self):
        """Clear chat history."""
        st.session_state.messages = []
        if st.session_state.client:
            st.session_state.client.messages = []
        st.rerun()
    
    def run(self):
        """Run the main application."""
        # Set page configuration
        st.set_page_config(
            page_title="MCP Client Interface",
            page_icon="🤖",
            layout="wide"
        )
        
        # App header
        st.title("🤖 MCP Client Interface")
        st.markdown("Connect to your MCP server and chat with Gemini AI")
        
        # Render components
        self.render_sidebar()
        self.render_chat_interface()


def main():
    """Application entry point."""
    app = MCPClientApp()
    app.run()


if __name__ == "__main__":
    main()