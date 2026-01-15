# TUI Mode Events Reference

This document provides a complete reference of all events emitted by the regular Codex TUI (Terminal User Interface) mode. These events are used for communication between the Codex client and agent through an Event Queue pattern.

## Event Structure

All events follow a common structure:

```typescript
{
  id: string,        // Unique identifier for this event
  msg: EventMsg      // The event payload (see Event Types below)
}
```

## Event Types

The following events can be emitted during a Codex session. Events are defined in the `EventMsg` enum.

---

### Session & Configuration Events

#### 1. `SessionConfigured`

Acknowledgment that the client's configuration message has been received and the session is ready.

**Fields:**
- `session_id`: String (ThreadId) - The unique identifier for this thread/session
- `model`: String - The model being used (e.g., "gpt-4", "claude-3")
- `model_provider_id`: String - The provider identifier
- `approval_policy`: Enum - When to ask for approval for execution (Never, Always, etc.)
- `sandbox_policy`: Enum - How to sandbox commands (ReadOnly, ReadWrite, etc.)
- `cwd`: PathBuf - The working directory for the session
- `reasoning_effort`: Optional - The effort level for model reasoning
- `history_log_id`: Number (u64) - Identifier of the history log file
- `history_entry_count`: Number - Current number of entries in history
- `initial_messages`: Optional - Initial messages for resumed sessions
- `rollout_path`: PathBuf - Path to rollout configuration

**Example:**
```json
{
  "id": "evt_1",
  "msg": {
    "session_configured": {
      "session_id": "67e55044-10b1-426f-9247-bb680e5fe0c8",
      "model": "gpt-4",
      "model_provider_id": "openai",
      "approval_policy": "never",
      "sandbox_policy": "read_write",
      "cwd": "/home/user/project",
      "reasoning_effort": null,
      "history_log_id": 12345,
      "history_entry_count": 0,
      "rollout_path": "/tmp/rollout.json"
    }
  }
}
```

---

### Turn Events

#### 2. `TurnStarted` (wire format: `task_started`)

Emitted when the agent starts processing a new turn.

**Fields:**
- `model_context_window`: Optional Number (i64) - The context window size for the model

**Example:**
```json
{
  "id": "evt_2",
  "msg": {
    "task_started": {
      "model_context_window": 128000
    }
  }
}
```

---

#### 3. `TurnComplete` (wire format: `task_complete`)

Emitted when the agent completes all actions for a turn.

**Fields:**
- `last_agent_message`: Optional String - The final message from the agent

**Example:**
```json
{
  "id": "evt_3",
  "msg": {
    "task_complete": {
      "last_agent_message": "I've completed the requested changes."
    }
  }
}
```

---

#### 4. `TurnAborted`

Emitted when a turn is aborted, typically in response to an `Interrupt` operation.

**Fields:**
- `message`: Optional String - Explanation of why the turn was aborted

**Example:**
```json
{
  "id": "evt_4",
  "msg": {
    "turn_aborted": {
      "message": "User interrupted the operation"
    }
  }
}
```

---

### Message Events

#### 5. `AgentMessage`

A complete text message from the agent.

**Fields:**
- `message`: String - The agent's message text

**Example:**
```json
{
  "id": "evt_5",
  "msg": {
    "agent_message": {
      "message": "I'll help you with that. Let me start by examining the code."
    }
  }
}
```

---

#### 6. `AgentMessageDelta`

Incremental chunk of an agent message being streamed.

**Fields:**
- `delta`: String - The incremental text chunk

**Example:**
```json
{
  "id": "evt_6",
  "msg": {
    "agent_message_delta": {
      "delta": "I'll help"
    }
  }
}
```

---

#### 7. `UserMessage`

A message from the user that was sent to the model.

**Fields:**
- `message`: String - The user's message text
- `images`: Optional Array<String> - Optional image attachments

**Example:**
```json
{
  "id": "evt_7",
  "msg": {
    "user_message": {
      "message": "Please add error handling to the login function",
      "images": null
    }
  }
}
```

---

### Reasoning Events

#### 8. `AgentReasoning`

A complete reasoning summary from the agent explaining its thought process.

**Fields:**
- `text`: String - The reasoning text

**Example:**
```json
{
  "id": "evt_8",
  "msg": {
    "agent_reasoning": {
      "text": "I need to first understand the current implementation before making changes."
    }
  }
}
```

---

#### 9. `AgentReasoningDelta`

Incremental chunk of reasoning text being streamed.

**Fields:**
- `delta`: String - The incremental reasoning text

**Example:**
```json
{
  "id": "evt_9",
  "msg": {
    "agent_reasoning_delta": {
      "delta": "First, I'll"
    }
  }
}
```

---

#### 10. `AgentReasoningRawContent`

Raw chain-of-thought content from the agent (unprocessed reasoning).

**Fields:**
- `text`: String - Raw reasoning content

**Example:**
```json
{
  "id": "evt_10",
  "msg": {
    "agent_reasoning_raw_content": {
      "text": "Let me think step by step..."
    }
  }
}
```

---

#### 11. `AgentReasoningRawContentDelta`

Incremental chunk of raw reasoning content.

**Fields:**
- `delta`: String - The incremental raw reasoning chunk

**Example:**
```json
{
  "id": "evt_11",
  "msg": {
    "agent_reasoning_raw_content_delta": {
      "delta": "step 1:"
    }
  }
}
```

---

#### 12. `AgentReasoningSectionBreak`

Signals when the model begins a new reasoning section (e.g., a new titled block).

**Fields:**
- `item_id`: String - The item this section belongs to
- `summary_index`: Number (i64) - Index of the summary section

**Example:**
```json
{
  "id": "evt_12",
  "msg": {
    "agent_reasoning_section_break": {
      "item_id": "item_0",
      "summary_index": 1
    }
  }
}
```

---

### Command Execution Events

#### 13. `ExecCommandBegin`

Notification that the agent is about to execute a command.

**Fields:**
- `call_id`: String - Unique identifier to pair with ExecCommandEnd
- `process_id`: Optional String - Process ID of the underlying PTY
- `turn_id`: String - The turn this command belongs to
- `command`: Array<String> - The command and its arguments
- `cwd`: PathBuf - The working directory for the command
- `parsed_cmd`: Array - Parsed command structure
- `source`: Enum - Where the command originated (Agent, User, etc.)
- `interaction_input`: Optional String - Input for interactive commands

**Example:**
```json
{
  "id": "evt_13",
  "msg": {
    "exec_command_begin": {
      "call_id": "cmd_1",
      "process_id": "12345",
      "turn_id": "turn_1",
      "command": ["npm", "install", "lodash"],
      "cwd": "/home/user/project",
      "parsed_cmd": [],
      "source": "agent",
      "interaction_input": null
    }
  }
}
```

---

#### 14. `ExecCommandOutputDelta`

Incremental chunk of output from a running command.

**Fields:**
- `call_id`: String - Identifier for the ExecCommandBegin
- `stream`: Enum - Which stream produced this ("stdout" or "stderr")
- `chunk`: String (base64) - Raw bytes from the stream

**Example:**
```json
{
  "id": "evt_14",
  "msg": {
    "exec_command_output_delta": {
      "call_id": "cmd_1",
      "stream": "stdout",
      "chunk": "aW5zdGFsbGluZy4uLg=="
    }
  }
}
```

---

#### 15. `ExecCommandEnd`

Notification that a command execution has finished.

**Fields:**
- `call_id`: String - Identifier for the corresponding ExecCommandBegin
- `process_id`: Optional String - Process ID
- `turn_id`: String - The turn this command belongs to
- `command`: Array<String> - The command that was executed
- `cwd`: PathBuf - Working directory
- `parsed_cmd`: Array - Parsed command structure
- `source`: Enum - Command source
- `interaction_input`: Optional String - Interactive input
- `stdout`: String - Captured stdout
- `stderr`: String - Captured stderr
- `aggregated_output`: String - Combined output
- `exit_code`: Number (i32) - The command's exit code
- `duration`: String (Duration) - How long the command took
- `formatted_output`: String - Formatted output shown to the model

**Example:**
```json
{
  "id": "evt_15",
  "msg": {
    "exec_command_end": {
      "call_id": "cmd_1",
      "process_id": "12345",
      "turn_id": "turn_1",
      "command": ["npm", "install", "lodash"],
      "cwd": "/home/user/project",
      "parsed_cmd": [],
      "source": "agent",
      "interaction_input": null,
      "stdout": "added 1 package",
      "stderr": "",
      "aggregated_output": "added 1 package",
      "exit_code": 0,
      "duration": "2.5s",
      "formatted_output": "✓ Successfully installed lodash"
    }
  }
}
```

---

#### 16. `TerminalInteraction`

Terminal interaction event showing stdin sent and stdout observed for a running command.

**Fields:**
- `call_id`: String - Identifier for the ExecCommandBegin
- `process_id`: String - Process ID of the running command
- `stdin`: String - Input sent to the terminal

**Example:**
```json
{
  "id": "evt_16",
  "msg": {
    "terminal_interaction": {
      "call_id": "cmd_1",
      "process_id": "12345",
      "stdin": "yes\n"
    }
  }
}
```

---

### MCP (Model Context Protocol) Events

#### 17. `McpStartupUpdate`

Incremental progress update during MCP server startup.

**Fields:**
- `server`: String - Name of the server being started
- `status`: Enum - Current status (Starting, Ready, Failed, Cancelled)

**Example:**
```json
{
  "id": "evt_17",
  "msg": {
    "mcp_startup_update": {
      "server": "filesystem",
      "status": "ready"
    }
  }
}
```

---

#### 18. `McpStartupComplete`

Aggregate summary of MCP startup completion.

**Fields:**
- `ready`: Array<String> - Servers that started successfully
- `failed`: Array - Servers that failed with error details
- `cancelled`: Array<String> - Servers that were cancelled

**Example:**
```json
{
  "id": "evt_18",
  "msg": {
    "mcp_startup_complete": {
      "ready": ["filesystem", "github"],
      "failed": [],
      "cancelled": []
    }
  }
}
```

---

#### 19. `McpToolCallBegin`

Notification that an MCP tool call is starting.

**Fields:**
- `call_id`: String - Unique identifier
- `invocation`: Object
  - `server`: String - MCP server name
  - `tool`: String - Tool name
  - `arguments`: Optional Object - Arguments to the tool

**Example:**
```json
{
  "id": "evt_19",
  "msg": {
    "mcp_tool_call_begin": {
      "call_id": "mcp_1",
      "invocation": {
        "server": "filesystem",
        "tool": "read_file",
        "arguments": {
          "path": "/home/user/file.txt"
        }
      }
    }
  }
}
```

---

#### 20. `McpToolCallEnd`

Notification that an MCP tool call has finished.

**Fields:**
- `call_id`: String - Identifier for the corresponding begin event
- `invocation`: Object - The invocation details (same as begin)
- `duration`: String (Duration) - How long the call took
- `result`: Result - Either Ok with CallToolResult or Err with error message

**Example (success):**
```json
{
  "id": "evt_20",
  "msg": {
    "mcp_tool_call_end": {
      "call_id": "mcp_1",
      "invocation": {
        "server": "filesystem",
        "tool": "read_file",
        "arguments": {
          "path": "/home/user/file.txt"
        }
      },
      "duration": "0.5s",
      "result": {
        "Ok": {
          "content": [{"type": "text", "text": "file contents"}],
          "is_error": false,
          "structured_content": null
        }
      }
    }
  }
}
```

**Example (failure):**
```json
{
  "id": "evt_21",
  "msg": {
    "mcp_tool_call_end": {
      "call_id": "mcp_1",
      "invocation": {
        "server": "filesystem",
        "tool": "read_file",
        "arguments": {
          "path": "/nonexistent/file.txt"
        }
      },
      "duration": "0.1s",
      "result": {
        "Err": "File not found"
      }
    }
  }
}
```

---

#### 21. `McpListToolsResponse`

Response to a request for available MCP tools.

**Fields:**
- `tools`: HashMap - Fully qualified tool name to tool definition
- `resources`: HashMap - Known resources grouped by server name
- `resource_templates`: HashMap - Resource templates grouped by server
- `auth_statuses`: HashMap - Authentication status per MCP server

**Example:**
```json
{
  "id": "evt_22",
  "msg": {
    "mcp_list_tools_response": {
      "tools": {
        "filesystem.read_file": { "name": "read_file", "description": "Read a file" }
      },
      "resources": {},
      "resource_templates": {},
      "auth_statuses": {
        "filesystem": "unsupported"
      }
    }
  }
}
```

---

### Web Search Events

#### 22. `WebSearchBegin`

Notification that a web search is starting.

**Fields:**
- `call_id`: String - Unique identifier

**Example:**
```json
{
  "id": "evt_23",
  "msg": {
    "web_search_begin": {
      "call_id": "search_1"
    }
  }
}
```

---

#### 23. `WebSearchEnd`

Notification that a web search has completed.

**Fields:**
- `call_id`: String - Identifier for the corresponding begin event
- `query`: String - The search query that was executed

**Example:**
```json
{
  "id": "evt_24",
  "msg": {
    "web_search_end": {
      "call_id": "search_1",
      "query": "rust async programming best practices"
    }
  }
}
```

---

### File Change Events

#### 24. `PatchApplyBegin`

Notification that the agent is about to apply a code patch.

**Fields:**
- `call_id`: String - Unique identifier
- `turn_id`: String - The turn this patch belongs to
- `auto_approved`: Boolean - If true, no approval request was shown
- `changes`: HashMap - Map of file paths to change types

**Example:**
```json
{
  "id": "evt_25",
  "msg": {
    "patch_apply_begin": {
      "call_id": "patch_1",
      "turn_id": "turn_1",
      "auto_approved": true,
      "changes": {
        "src/app.js": { "update": { "unified_diff": "...", "move_path": null } }
      }
    }
  }
}
```

---

#### 25. `PatchApplyEnd`

Notification that a patch application has finished.

**Fields:**
- `call_id`: String - Identifier for the corresponding begin event
- `turn_id`: String - The turn this patch belongs to
- `stdout`: String - Summary printed by apply_patch
- `stderr`: String - Parser errors, IO failures, etc.
- `success`: Boolean - Whether the patch was applied successfully
- `changes`: HashMap - The changes that were applied

**Example:**
```json
{
  "id": "evt_26",
  "msg": {
    "patch_apply_end": {
      "call_id": "patch_1",
      "turn_id": "turn_1",
      "stdout": "Applied 1 change successfully",
      "stderr": "",
      "success": true,
      "changes": {
        "src/app.js": { "update": { "unified_diff": "...", "move_path": null } }
      }
    }
  }
}
```

---

### Token Usage Events

#### 26. `TokenCount`

Usage update for the current session, including totals and last turn.

**Fields:**
- `info`: Optional Object - Token usage information
  - `total_token_usage`: Object
    - `input_tokens`: Number (i64)
    - `cached_input_tokens`: Number (i64)
    - `output_tokens`: Number (i64)
    - `reasoning_output_tokens`: Number (i64)
    - `total_tokens`: Number (i64)
  - `last_token_usage`: Object - Same structure as total_token_usage
  - `model_context_window`: Optional Number (i64)
- `rate_limits`: Optional - Rate limit information

**Example:**
```json
{
  "id": "evt_27",
  "msg": {
    "token_count": {
      "info": {
        "total_token_usage": {
          "input_tokens": 1200,
          "cached_input_tokens": 200,
          "output_tokens": 450,
          "reasoning_output_tokens": 100,
          "total_tokens": 1750
        },
        "last_token_usage": {
          "input_tokens": 300,
          "cached_input_tokens": 50,
          "output_tokens": 120,
          "reasoning_output_tokens": 30,
          "total_tokens": 450
        },
        "model_context_window": 128000
      },
      "rate_limits": null
    }
  }
}
```

---

### Error & Warning Events

#### 27. `Error`

Error while executing a submission.

**Fields:**
- `message`: String - The error message
- `codex_error_info`: Optional Enum - Structured error type

**Example:**
```json
{
  "id": "evt_28",
  "msg": {
    "error": {
      "message": "Failed to execute command",
      "codex_error_info": "sandbox_error"
    }
  }
}
```

---

#### 28. `Warning`

Warning issued during processing. Unlike Error, the turn continues.

**Fields:**
- `message`: String - The warning message

**Example:**
```json
{
  "id": "evt_29",
  "msg": {
    "warning": {
      "message": "Long conversations may reduce accuracy. Consider starting a new session."
    }
  }
}
```

---

#### 29. `StreamError`

Notification that a model stream experienced an error and the system is handling it (e.g., retrying).

**Fields:**
- `message`: String - The error message
- `codex_error_info`: Optional Enum - Structured error type
- `additional_details`: Optional String - Additional context

**Example:**
```json
{
  "id": "evt_30",
  "msg": {
    "stream_error": {
      "message": "Connection lost, retrying...",
      "codex_error_info": "response_stream_disconnected",
      "additional_details": "HTTP 503"
    }
  }
}
```

---

### Planning Events

#### 30. `PlanUpdate`

Update to the agent's running to-do list/plan.

**Fields:**
- `explanation`: Optional String - Explanation of the plan
- `plan`: Array - List of plan items
  - Each item has:
    - `step`: String - Description of the step
    - `status`: Enum - Status (Pending, InProgress, Completed, Failed)

**Example:**
```json
{
  "id": "evt_31",
  "msg": {
    "plan_update": {
      "explanation": "Breaking down the task",
      "plan": [
        { "step": "Read existing code", "status": "completed" },
        { "step": "Make changes", "status": "in_progress" },
        { "step": "Run tests", "status": "pending" }
      ]
    }
  }
}
```

---

### Item Events

#### 31. `ItemStarted`

Emitted when a new item (turn item) is started.

**Fields:**
- `thread_id`: String (ThreadId)
- `turn_id`: String
- `item`: TurnItem - The item being started (various types possible)

**Example:**
```json
{
  "id": "evt_32",
  "msg": {
    "item_started": {
      "thread_id": "67e55044-10b1-426f-9247-bb680e5fe0c8",
      "turn_id": "turn_1",
      "item": {
        "type": "web_search",
        "id": "item_0",
        "query": "rust error handling"
      }
    }
  }
}
```

---

#### 32. `ItemCompleted`

Emitted when an item reaches completion.

**Fields:**
- `thread_id`: String (ThreadId)
- `turn_id`: String
- `item`: TurnItem - The completed item with final state

**Example:**
```json
{
  "id": "evt_33",
  "msg": {
    "item_completed": {
      "thread_id": "67e55044-10b1-426f-9247-bb680e5fe0c8",
      "turn_id": "turn_1",
      "item": {
        "type": "web_search",
        "id": "item_0",
        "query": "rust error handling",
        "results": "..."
      }
    }
  }
}
```

---

#### 33. `AgentMessageContentDelta`

Incremental content delta for an agent message item.

**Fields:**
- `thread_id`: String
- `turn_id`: String
- `item_id`: String
- `delta`: String - The incremental content

**Example:**
```json
{
  "id": "evt_34",
  "msg": {
    "agent_message_content_delta": {
      "thread_id": "67e55044-10b1-426f-9247-bb680e5fe0c8",
      "turn_id": "turn_1",
      "item_id": "item_0",
      "delta": "Here's "
    }
  }
}
```

---

#### 34. `ReasoningContentDelta`

Incremental reasoning content delta.

**Fields:**
- `thread_id`: String
- `turn_id`: String
- `item_id`: String
- `delta`: String - The incremental reasoning
- `summary_index`: Number (i64) - Index of the summary section

**Example:**
```json
{
  "id": "evt_35",
  "msg": {
    "reasoning_content_delta": {
      "thread_id": "67e55044-10b1-426f-9247-bb680e5fe0c8",
      "turn_id": "turn_1",
      "item_id": "item_0",
      "delta": "First, ",
      "summary_index": 0
    }
  }
}
```

---

#### 35. `ReasoningRawContentDelta`

Incremental raw reasoning content delta.

**Fields:**
- `thread_id`: String
- `turn_id`: String
- `item_id`: String
- `delta`: String - The incremental raw reasoning
- `content_index`: Number (i64) - Index of the content section

**Example:**
```json
{
  "id": "evt_36",
  "msg": {
    "reasoning_raw_content_delta": {
      "thread_id": "67e55044-10b1-426f-9247-bb680e5fe0c8",
      "turn_id": "turn_1",
      "item_id": "item_0",
      "delta": "thinking...",
      "content_index": 0
    }
  }
}
```

---

### History & Context Events

#### 36. `ContextCompacted`

Notification that conversation history was compacted.

**Fields:** (empty struct)

**Example:**
```json
{
  "id": "evt_37",
  "msg": {
    "context_compacted": {}
  }
}
```

---

#### 37. `ThreadRolledBack`

Notification that conversation history was rolled back.

**Fields:**
- `num_turns`: Number (u32) - Number of user turns that were removed

**Example:**
```json
{
  "id": "evt_38",
  "msg": {
    "thread_rolled_back": {
      "num_turns": 2
    }
  }
}
```

---

#### 38. `GetHistoryEntryResponse`

Response to a request for a specific history entry.

**Fields:**
- `offset`: Number (usize) - The offset requested
- `log_id`: Number (u64) - The log identifier
- `entry`: Optional Object - The history entry if available

**Example:**
```json
{
  "id": "evt_39",
  "msg": {
    "get_history_entry_response": {
      "offset": 5,
      "log_id": 12345,
      "entry": { "..." }
    }
  }
}
```

---

#### 39. `TurnDiff`

Shows the diff for changes made during a turn.

**Fields:**
- `unified_diff`: String - Unified diff format

**Example:**
```json
{
  "id": "evt_40",
  "msg": {
    "turn_diff": {
      "unified_diff": "--- a/file.js\n+++ b/file.js\n@@ -1,3 +1,4 @@\n+const x = 1;\n"
    }
  }
}
```

---

### Approval Events

#### 40. `ExecApprovalRequest`

Request for user approval to execute a command.

**Fields:**
- `call_id`: String
- `command`: Array<String>
- `cwd`: PathBuf
- `parsed_cmd`: Array
- `auto_declined`: Boolean

**Example:**
```json
{
  "id": "evt_41",
  "msg": {
    "exec_approval_request": {
      "call_id": "cmd_1",
      "command": ["rm", "-rf", "node_modules"],
      "cwd": "/home/user/project",
      "parsed_cmd": [],
      "auto_declined": false
    }
  }
}
```

---

#### 41. `ApplyPatchApprovalRequest`

Request for user approval to apply a patch.

**Fields:**
- `call_id`: String
- `changes`: HashMap - File changes to be applied

**Example:**
```json
{
  "id": "evt_42",
  "msg": {
    "apply_patch_approval_request": {
      "call_id": "patch_1",
      "changes": {
        "src/app.js": { "update": { "unified_diff": "...", "move_path": null } }
      }
    }
  }
}
```

---

#### 42. `ElicitationRequest`

Request for user input or clarification during execution.

**Fields:**
- (Complex structure - varies based on elicitation type)

**Example:**
```json
{
  "id": "evt_43",
  "msg": {
    "elicitation_request": {
      "question": "Which file should I modify?",
      "options": ["app.js", "index.js"]
    }
  }
}
```

---

### Utility Events

#### 43. `ViewImageToolCall`

Notification that the agent viewed a local image.

**Fields:**
- `call_id`: String - Identifier for the tool call
- `path`: PathBuf - Local filesystem path to the image

**Example:**
```json
{
  "id": "evt_44",
  "msg": {
    "view_image_tool_call": {
      "call_id": "img_1",
      "path": "/home/user/screenshot.png"
    }
  }
}
```

---

#### 44. `BackgroundEvent`

Background notification message.

**Fields:**
- `message`: String - The notification message

**Example:**
```json
{
  "id": "evt_45",
  "msg": {
    "background_event": {
      "message": "Indexing files in the background..."
    }
  }
}
```

---

#### 45. `DeprecationNotice`

Notification that something is deprecated.

**Fields:**
- `summary`: String - What is deprecated
- `details`: Optional String - Migration guidance

**Example:**
```json
{
  "id": "evt_46",
  "msg": {
    "deprecation_notice": {
      "summary": "Command format is deprecated",
      "details": "Use the new syntax: codex --flag instead"
    }
  }
}
```

---

### Undo Events

#### 46. `UndoStarted`

Notification that an undo operation has started.

**Fields:**
- `message`: Optional String - Description of what's being undone

**Example:**
```json
{
  "id": "evt_47",
  "msg": {
    "undo_started": {
      "message": "Undoing last file changes"
    }
  }
}
```

---

#### 47. `UndoCompleted`

Notification that an undo operation has completed.

**Fields:**
- `success`: Boolean - Whether the undo succeeded
- `message`: Optional String - Result message

**Example:**
```json
{
  "id": "evt_48",
  "msg": {
    "undo_completed": {
      "success": true,
      "message": "Successfully reverted 3 files"
    }
  }
}
```

---

### Review Mode Events

#### 48. `EnteredReviewMode`

Notification that the agent entered review mode.

**Fields:**
- (Complex ReviewRequest structure)

**Example:**
```json
{
  "id": "evt_49",
  "msg": {
    "entered_review_mode": {
      "review_type": "code_review",
      "files": ["src/app.js"]
    }
  }
}
```

---

#### 49. `ExitedReviewMode`

Notification that the agent exited review mode.

**Fields:**
- `review_output`: Optional Object - Final result to apply

**Example:**
```json
{
  "id": "evt_50",
  "msg": {
    "exited_review_mode": {
      "review_output": null
    }
  }
}
```

---

### Response Item Events

#### 50. `RawResponseItem`

Raw response item from the model (for debugging/advanced use).

**Fields:**
- `item`: ResponseItem - The raw response item

**Example:**
```json
{
  "id": "evt_51",
  "msg": {
    "raw_response_item": {
      "item": { "..." }
    }
  }
}
```

---

### Custom Prompts & Skills Events

#### 51. `ListCustomPromptsResponse`

Response to a request for available custom prompts.

**Fields:**
- `custom_prompts`: Array - List of custom prompt definitions

**Example:**
```json
{
  "id": "evt_52",
  "msg": {
    "list_custom_prompts_response": {
      "custom_prompts": [
        {
          "name": "code_review",
          "description": "Review code for issues",
          "content": "..."
        }
      ]
    }
  }
}
```

---

#### 52. `ListSkillsResponse`

Response to a request for available skills.

**Fields:**
- `skills`: Array - List of skill entries with metadata

**Example:**
```json
{
  "id": "evt_53",
  "msg": {
    "list_skills_response": {
      "skills": [
        {
          "cwd": "/home/user/project",
          "skills": [
            {
              "name": "test_runner",
              "description": "Run project tests",
              "path": ".codex/skills/test.md",
              "scope": "repo"
            }
          ],
          "errors": []
        }
      ]
    }
  }
}
```

---

#### 53. `SkillsUpdateAvailable`

Notification that skill data may have been updated.

**Fields:** (empty)

**Example:**
```json
{
  "id": "evt_54",
  "msg": "skills_update_available"
}
```

---

### Shutdown Event

#### 54. `ShutdownComplete`

Notification that the agent is shutting down.

**Fields:** (empty)

**Example:**
```json
{
  "id": "evt_55",
  "msg": "shutdown_complete"
}
```

---

## Event Flow Examples

### Simple Command Execution Flow

```json
{"id":"1","msg":{"session_configured":{...}}}
{"id":"2","msg":{"task_started":{"model_context_window":128000}}}
{"id":"3","msg":{"agent_message":{"message":"I'll run npm install for you."}}}
{"id":"4","msg":{"exec_command_begin":{"call_id":"cmd_1","command":["npm","install"],...}}}
{"id":"5","msg":{"exec_command_output_delta":{"call_id":"cmd_1","stream":"stdout",...}}}
{"id":"6","msg":{"exec_command_end":{"call_id":"cmd_1","exit_code":0,...}}}
{"id":"7","msg":{"task_complete":{"last_agent_message":"Installation complete!"}}}
```

### MCP Tool Call Flow

```json
{"id":"1","msg":{"mcp_tool_call_begin":{"call_id":"mcp_1","invocation":{...}}}}
{"id":"2","msg":{"mcp_tool_call_end":{"call_id":"mcp_1","result":{"Ok":{...}}}}}
```

### Error Handling Flow

```json
{"id":"1","msg":{"task_started":{...}}}
{"id":"2","msg":{"exec_command_begin":{...}}}
{"id":"3","msg":{"exec_command_end":{"exit_code":1,...}}}
{"id":"4","msg":{"error":{"message":"Command failed with exit code 1"}}}
```

---

## Notes

- Events are emitted in chronological order during a session
- Some events come in pairs (Begin/End, Started/Completed)
- Delta events allow for streaming updates in real-time
- The TUI mode provides richer event details compared to exec mode's JSONL output
- Error events may be followed by retry attempts or turn completion
- Context can be compacted or rolled back to manage conversation length
- Approval requests pause execution until user responds

---

## See Also

- [Exec Mode JSON Events Reference](./exec-mode-json-events.md) - For the non-interactive exec mode events
- Source: `codex-rs/protocol/src/protocol.rs`
