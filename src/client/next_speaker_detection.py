from typing import List, Dict, Any, Optional, Literal
from dataclasses import dataclass
import json
import re
from google import genai


@dataclass
class NextSpeakerResult:
    """Result of next speaker detection"""
    next_speaker: Literal["user", "model"]
    reasoning: str
    should_continue: bool = False


class NextSpeakerDetector:
    """
    Determines who should speak next in a conversation between user and AI agent.
    Based on analysis of the AI's previous response to decide if it should continue
    working or wait for user input.
    """
    
    CHECK_PROMPT = """
Analyze your previous response in this conversation and determine who should speak next.

Decision Rules:
1. **Model Continues**: Choose this if:
   - Your response indicates an immediate next action (e.g., "I'll now check the files...")
   - The task is **incomplete** or **an error occured**
   - You're in the middle of a multi-step process
   - You started a task but haven't finished it yet

2. **Question to User**: Choose this if:
   - Your response ends with a direct question to the user
   - You're asking for clarification, preferences, or additional information

3. **Waiting for User**: Choose this if:
   - You've completed the requested task
   - You've provided a final answer or summary
   - The conversation has reached a natural stopping point

Respond with valid JSON in this exact format:
{
    "reasoning": "Brief explanation of why you chose this option",
    "next_speaker": "user" or "model"
}

Only respond with the JSON, no other text.
"""

    def __init__(self, gemini_client):
        self.gemini_client = gemini_client

    def _get_last_model_message(self, messages: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Get the last message from the model in the conversation"""
        for message in reversed(messages):
            if message.get("role") == "model":
                return message
        return None

    def _is_empty_response(self, message: Dict[str, Any]) -> bool:
        """Check if the model response is empty or only contains tool calls"""
        if not message or not message.get("parts"):
            return True
        
        # Check if all parts are either empty text or function calls
        for part in message["parts"]:
            if part.text.strip():
                return False
        return True

    def _has_pending_tool_calls(self, message: Dict[str, Any]) -> bool:
        """Check if the message contains tool/function calls"""
        if not message or not message.get("parts"):
            return False
        
        for part in message["parts"]:
            if "function_call" in part:
                return True
        return False

    def _extract_json_from_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON from the response text"""
        # Try to find JSON in the response
        json_patterns = [
            r'\{[^{}]*"next_speaker"\s*:\s*"(?:user|model)"[^{}]*\}',
            r'\{.*?"reasoning".*?"next_speaker".*?\}',
            r'\{.*?\}'
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, response_text, re.DOTALL)
            for match in matches:
                try:
                    data = json.loads(match)
                    if "next_speaker" in data and data["next_speaker"] in ["user", "model"]:
                        return data
                except json.JSONDecodeError:
                    continue
        
        return None

    async def detect_next_speaker(
        self, 
        messages: List[Dict[str, Any]], 
        skip_detection: bool = False
    ) -> Optional[NextSpeakerResult]:
        """
        Detect who should speak next based on the conversation history.
        
        Args:
            messages: List of conversation messages
            skip_detection: If True, skip the detection process
            
        Returns:
            NextSpeakerResult or None if detection couldn't be performed
        """
        if skip_detection:
            return None
        
        if not messages:
            return None
        
        last_message = messages[-1] if messages else None
        
        # Special case: if last message was a function response, model should speak
        if last_message and last_message.get("role") == "function":
            return NextSpeakerResult(
                next_speaker="model",
                reasoning="Function/tool response received, model should process the result",
                should_continue=True
            )
        
        # Get the last model message
        last_model_message = self._get_last_model_message(messages)
        
        if not last_model_message:
            return None
        
        # Special case: if last model message is empty, model should speak
        if self._is_empty_response(last_model_message):
            return NextSpeakerResult(
                next_speaker="model",
                reasoning="Last model response was empty, model should continue",
                should_continue=True
            )
        
        # Special case: if there are pending tool calls, let tools execute first
        if self._has_pending_tool_calls(last_model_message):
            return NextSpeakerResult(
                next_speaker="model",
                reasoning="Model made tool calls, waiting for tool responses",
                should_continue=False  # Don't auto-continue, wait for tool responses
            )
        
        # Prepare messages for analysis
        analysis_messages = messages.copy()
        analysis_messages.append({
            "role": "user",
            "parts": [{"text": self.CHECK_PROMPT}]
        })
        

        try:
            # Call Gemini to analyze the conversation
            response = await self.gemini_client.aio.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=analysis_messages,
                config=genai.types.GenerateContentConfig(
                    temperature=0.1,
                    max_output_tokens=200,
                    system_instruction="You are analyzing a conversation to determine who should speak next. Respond only with the requested JSON format."
                )
            )
            
            response_text = response.text if response.text else ""
        
            # Extract JSON from response
            json_data = self._extract_json_from_response(response_text)
            
            if not json_data:
                # Fallback: assume user should speak if we can't parse the response
                return NextSpeakerResult(
                    next_speaker="user",
                    reasoning="Failed to parse next speaker detection response",
                    should_continue=False
                )
            
            next_speaker = json_data.get("next_speaker", "user")
            reasoning = json_data.get("reasoning", "No reasoning provided")
            
            return NextSpeakerResult(
                next_speaker=next_speaker,
                reasoning=reasoning,
                should_continue=(next_speaker == "model")
            )
            
        except Exception as e:
            print(f"Error in next speaker detection: {str(e)}")
            # Default to user speaking on error
            return NextSpeakerResult(
                next_speaker="user",
                reasoning=f"Error during detection: {str(e)}",
                should_continue=False
            )

    async def should_continue_conversation(
        self, 
        messages: List[Dict[str, Any]], 
        max_turns: int = -1,
        current_turn: int = 0
    ) -> bool:
        """
        Determine if the conversation should continue automatically.
        
        Args:
            messages: Current conversation messages
            max_turns: Maximum number of turns allowed (-1 for no limit)
            current_turn: Current turn number
            
        Returns:
            True if conversation should continue, False otherwise
        """
        # Check turn limits
        if max_turns > 0 and current_turn >= max_turns:
            return False
        
        # Perform next speaker detection
        result = await self.detect_next_speaker(messages)
        
        if not result:
            return False
        
        return result.should_continue


class ConversationController:
    """
    Controls the flow of conversation between user and AI agent.
    Manages automatic continuation and turn limits.
    """
    
    CONTINUE_PROMPT = "Please continue."
    
    def __init__(self, gemini_client, max_session_turns: int = -1):
        self.detector = NextSpeakerDetector(gemini_client)
        self.max_session_turns = max_session_turns
        self.current_turn = 0
        
    async def process_turn(
        self, 
        messages: List[Dict[str, Any]], 
        auto_continue: bool = True
    ) -> tuple[bool, Optional[NextSpeakerResult]]:
        """
        Process a conversation turn and determine if it should continue.
        
        Args:
            messages: Current conversation messages
            auto_continue: Whether to allow automatic continuation
            
        Returns:
            Tuple of (should_continue, detection_result)
        """
        self.current_turn += 1
        
        # Check session turn limits
        if self.max_session_turns > 0 and self.current_turn >= self.max_session_turns:
            return False, NextSpeakerResult(
                next_speaker="user",
                reasoning="Maximum session turns reached",
                should_continue=False
            )
        
        if not auto_continue:
            return False, None
        
        # Detect next speaker
        result = await self.detector.detect_next_speaker(messages)
        
        if not result:
            return False, None
        
        return result.should_continue, result
    
    def get_continue_message(self) -> Dict[str, Any]:
        """Get the message to continue the conversation"""
        return {
            "role": "user",
            "parts": [{"text": self.CONTINUE_PROMPT}]
        }
    
    def reset_turn_counter(self):
        """Reset the turn counter"""
        self.current_turn = 0