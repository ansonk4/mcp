## how the system determines when a task is done and when to return control to the user:

  Task Completion and Control Flow

  1. Finish Reasons from LLM
  The system monitors the finishReason provided by the LLM in each response:
   - STOP: Normal completion - task is considered done
   - MAX_TOKENS: Response was cut off due to token limits
   - SAFETY/RECITATION: Response was stopped due to safety or policy reasons
   - Other specific reasons that indicate the model has finished processing

  When any of these finish reasons are detected, the system yields a Finished event with the specific reason.

  2. Next Speaker Detection
  After each model response, the system uses a special mechanism to determine who should speak next:
   1. It asks the LLM to analyze its own previous response using specific rules:
      - Model Continues: If the response indicates an immediate next action or seems incomplete
      - Question to User: If the response ends with a direct question to the user
      - Waiting for User: If the response completed a task and is waiting for user input
   2. Based on this analysis, the LLM decides if it should continue (next_speaker: 'model') or wait for user input (next_speaker: 'user')
   3. If the model should continue, it automatically sends a "Please continue" prompt to keep the conversation going

  3. Session Turn Limits
  The system enforces a maximum number of conversation turns:
   - Configurable via maxSessionTurns setting (default is -1, meaning no limit)
   - When the limit is reached, a MaxSessionTurns event is emitted
   - This prevents infinite loops or excessively long conversations

  4. User Cancellation
  The system monitors for user cancellation signals:
   - If the user interrupts the process (Ctrl+C), a UserCancelled event is emitted
   - This immediately stops processing and returns control to the user

  5. Tool Execution Boundaries
  The system also determines task completion based on tool execution:
   - When the model makes tool calls, the system waits for all responses
   - After receiving all tool responses, it evaluates if the task is complete or if more processing is needed

  6. Technical Implementation
  In the main processing loop (client.ts), after each turn:
   1. If there are no pending tool calls and the signal isn't aborted:
   2. The system checks if the model should continue via the next speaker detection
   3. If the next speaker should be the user, control is returned to the user interface
   4. If the next speaker should be the model, it automatically continues with a "Please continue" prompt

  This multi-layered approach ensures that the system can intelligently determine when a task is truly complete versus when it needs to continue processing, while also providing safeguards against infinite loops and resource exhaustion.

## Next speaker detection
 
 1. Triggering the Check
  The next speaker detection is triggered after each complete model response in the conversation flow:
   1. When a turn completes (all streaming chunks have been processed)
   2. There are no pending tool calls waiting for responses
   3. The user hasn't cancelled the operation
   4. The system hasn't skipped the next speaker check (configurable)

  2. The Detection Process
  The detection works by asking the LLM to analyze its own previous response:

   1. Preparation:
      - The system gets the curated conversation history (filtered for valid content)
      - It ensures the last message was from the model (not the user)

   2. Special Cases Handling:
      - If the last message was a function/tool response, the model should speak next
      - If the last message was an empty model response, the model should speak next
      - If there's no history or the last speaker wasn't the model, it returns null

   3. Main Detection Logic:
      - The system appends a special prompt (CHECK_PROMPT) to the conversation history
      - This prompt asks the model to analyze its previous response and decide who should speak next

  3. The Special Prompt
  The CHECK_PROMPT provides clear decision rules:
   1. Model Continues: If the response indicates an immediate next action or seems incomplete
   2. Question to User: If the response ends with a direct question to the user
   3. Waiting for User: If the response completed a task and is waiting for input

  4. Structured Response
  The system requests a structured JSON response with a specific schema:

   1 {
   2   "reasoning": "Brief explanation justifying the choice",
   3   "next_speaker": "user" or "model"
   4 }

  5. Processing the Result
  After getting the response:
   1. If next_speaker is 'model':
      - The system automatically sends a "Please continue." prompt
      - This creates a recursive call to keep the conversation going
      - This allows the model to execute multi-step tasks without user intervention

   2. If next_speaker is 'user':
      - Control is returned to the user interface
      - The user can then provide input or instructions

  6. Example Flow
   1. User: "List all TODO comments in this project"
   2. Model responds with file search results
   3. Next speaker detection runs:
      - Model analyzes its response
      - Determines it has more work to do (searching files)
      - Returns { next_speaker: 'model' }
   4. System sends "Please continue."
   5. Model continues with the next step (reading files)
   6. Process repeats until task is complete
   7. When model determines task is done, it returns { next_speaker: 'user' }
   8. Control returns to user

  This mechanism allows the AI to work autonomously on multi-step tasks while still knowing when to pause and wait for user input, creating a natural conversation flow.