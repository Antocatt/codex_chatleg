# Exec Mode JSON Events Reference

This document provides a complete reference of all JSON events emitted by `codex exec` mode. These events are emitted as JSONL (JSON Lines) format, with one event per line.

## Top-Level Event Types

All events follow a common structure with a `type` field that indicates the event kind. The following top-level events are available:

### 1. `thread.started`

Emitted when a new thread is started as the first event.

**Event Name:** `thread.started`

**Fields:**
- `type`: `"thread.started"`
- `thread_id`: String - The identifier of the new thread. Can be used to resume the thread later.

**Example:**
```json
{
  "type": "thread.started",
  "thread_id": "67e55044-10b1-426f-9247-bb680e5fe0c8"
}
```

---

### 2. `turn.started`

Emitted when a turn is started by sending a new prompt to the model. A turn encompasses all events that happen while the agent is processing the prompt.

**Event Name:** `turn.started`

**Fields:**
- `type`: `"turn.started"`

**Example:**
```json
{
  "type": "turn.started"
}
```

---

### 3. `turn.completed`

Emitted when a turn is completed, typically right after the assistant's response.

**Event Name:** `turn.completed`

**Fields:**
- `type`: `"turn.completed"`
- `usage`: Object containing token usage statistics
  - `input_tokens`: Number (i64) - The number of input tokens used during the turn
  - `cached_input_tokens`: Number (i64) - The number of cached input tokens used during the turn
  - `output_tokens`: Number (i64) - The number of output tokens used during the turn

**Example:**
```json
{
  "type": "turn.completed",
  "usage": {
    "input_tokens": 1200,
    "cached_input_tokens": 200,
    "output_tokens": 345
  }
}
```

---

### 4. `turn.failed`

Indicates that a turn failed with an error.

**Event Name:** `turn.failed`

**Fields:**
- `type`: `"turn.failed"`
- `error`: Object containing error information
  - `message`: String - The error message

**Example:**
```json
{
  "type": "turn.failed",
  "error": {
    "message": "Failed to process request"
  }
}
```

---

### 5. `item.started`

Emitted when a new item is added to the thread. Typically the item will be in an "in progress" state.

**Event Name:** `item.started`

**Fields:**
- `type`: `"item.started"`
- `item`: Object - The thread item (see Thread Item Types below)

**Example:**
```json
{
  "type": "item.started",
  "item": {
    "id": "item_0",
    "type": "command_execution",
    "command": "bash -lc 'echo hi'",
    "aggregated_output": "",
    "exit_code": null,
    "status": "in_progress"
  }
}
```

---

### 6. `item.updated`

Emitted when an item is updated.

**Event Name:** `item.updated`

**Fields:**
- `type`: `"item.updated"`
- `item`: Object - The updated thread item (see Thread Item Types below)

**Example:**
```json
{
  "type": "item.updated",
  "item": {
    "id": "item_0",
    "type": "todo_list",
    "items": [
      {
        "text": "step one",
        "completed": true
      },
      {
        "text": "step two",
        "completed": false
      }
    ]
  }
}
```

---

### 7. `item.completed`

Signals that an item has reached a terminal state—either success or failure.

**Event Name:** `item.completed`

**Fields:**
- `type`: `"item.completed"`
- `item`: Object - The completed thread item (see Thread Item Types below)

**Example:**
```json
{
  "type": "item.completed",
  "item": {
    "id": "item_0",
    "type": "command_execution",
    "command": "bash -lc 'echo hi'",
    "aggregated_output": "hi\n",
    "exit_code": 0,
    "status": "completed"
  }
}
```

---

### 8. `error`

Represents an unrecoverable error emitted directly by the event stream.

**Event Name:** `error`

**Fields:**
- `type`: `"error"`
- `message`: String - The error message

**Example:**
```json
{
  "type": "error",
  "message": "Stream error occurred"
}
```

---

## Thread Item Types

Thread items are contained within `item.started`, `item.updated`, and `item.completed` events. Each item has an `id` field and a `type` field that determines its structure.

### 1. `agent_message`

Response from the agent. Either a natural-language response or a JSON string when structured output is requested.

**Item Type:** `agent_message`

**Fields:**
- `id`: String - Unique identifier for this item
- `type`: `"agent_message"`
- `text`: String - The agent's message text

**Example:**
```json
{
  "id": "item_0",
  "type": "agent_message",
  "text": "Hello! I'm here to help."
}
```

---

### 2. `reasoning`

Agent's reasoning summary.

**Item Type:** `reasoning`

**Fields:**
- `id`: String - Unique identifier for this item
- `type`: `"reasoning"`
- `text`: String - The reasoning text

**Example:**
```json
{
  "id": "item_0",
  "type": "reasoning",
  "text": "Let me think about the best approach to solve this problem..."
}
```

---

### 3. `command_execution`

Tracks a command executed by the agent. The item starts when the command is spawned and completes when the process exits with an exit code.

**Item Type:** `command_execution`

**Fields:**
- `id`: String - Unique identifier for this item
- `type`: `"command_execution"`
- `command`: String - The command being executed
- `aggregated_output`: String - The accumulated output from the command
- `exit_code`: Number (i32) or null - The exit code (null while in progress)
- `status`: String - One of:
  - `"in_progress"` - Command is currently running
  - `"completed"` - Command completed successfully
  - `"failed"` - Command failed
  - `"declined"` - Command was declined by the user

**Example (in progress):**
```json
{
  "id": "item_0",
  "type": "command_execution",
  "command": "npm install",
  "aggregated_output": "Installing dependencies...\n",
  "exit_code": null,
  "status": "in_progress"
}
```

**Example (completed):**
```json
{
  "id": "item_0",
  "type": "command_execution",
  "command": "npm install",
  "aggregated_output": "Successfully installed 42 packages\n",
  "exit_code": 0,
  "status": "completed"
}
```

---

### 4. `file_change`

Represents a set of file changes by the agent. The item is emitted only as a completed event once the patch succeeds or fails.

**Item Type:** `file_change`

**Fields:**
- `id`: String - Unique identifier for this item
- `type`: `"file_change"`
- `changes`: Array of change objects, each containing:
  - `path`: String - The file path
  - `kind`: String - One of:
    - `"add"` - File was added
    - `"delete"` - File was deleted
    - `"update"` - File was modified
- `status`: String - One of:
  - `"in_progress"` - Changes are being applied
  - `"completed"` - Changes were successfully applied
  - `"failed"` - Changes failed to apply

**Example:**
```json
{
  "id": "item_0",
  "type": "file_change",
  "changes": [
    {
      "path": "src/app.js",
      "kind": "update"
    },
    {
      "path": "src/newfile.js",
      "kind": "add"
    }
  ],
  "status": "completed"
}
```

---

### 5. `mcp_tool_call`

Represents a call to an MCP (Model Context Protocol) tool. The item starts when the invocation is dispatched and completes when the MCP server reports success or failure.

**Item Type:** `mcp_tool_call`

**Fields:**
- `id`: String - Unique identifier for this item
- `type`: `"mcp_tool_call"`
- `server`: String - The MCP server name
- `tool`: String - The tool name
- `arguments`: Object - The arguments passed to the tool (defaults to null if not provided)
- `result`: Object or null - The result from the tool call (null until completed)
  - `content`: Array - Array of content blocks from the tool
  - `structured_content`: Object or null - Structured data returned by the tool
- `error`: Object or null - Error information if the call failed
  - `message`: String - The error message
- `status`: String - One of:
  - `"in_progress"` - Tool call is in progress
  - `"completed"` - Tool call completed successfully
  - `"failed"` - Tool call failed

**Example (in progress):**
```json
{
  "id": "item_0",
  "type": "mcp_tool_call",
  "server": "filesystem",
  "tool": "read_file",
  "arguments": {
    "path": "/home/user/file.txt"
  },
  "result": null,
  "error": null,
  "status": "in_progress"
}
```

**Example (completed):**
```json
{
  "id": "item_0",
  "type": "mcp_tool_call",
  "server": "filesystem",
  "tool": "read_file",
  "arguments": {
    "path": "/home/user/file.txt"
  },
  "result": {
    "content": [
      {
        "type": "text",
        "text": "File contents here"
      }
    ],
    "structured_content": null
  },
  "error": null,
  "status": "completed"
}
```

**Example (failed):**
```json
{
  "id": "item_0",
  "type": "mcp_tool_call",
  "server": "filesystem",
  "tool": "read_file",
  "arguments": {
    "path": "/nonexistent/file.txt"
  },
  "result": null,
  "error": {
    "message": "File not found"
  },
  "status": "failed"
}
```

---

### 6. `web_search`

Captures a web search request. It starts when the search is kicked off and completes when results are returned to the agent.

**Item Type:** `web_search`

**Fields:**
- `id`: String - Unique identifier for this item
- `type`: `"web_search"`
- `query`: String - The search query

**Example:**
```json
{
  "id": "item_0",
  "type": "web_search",
  "query": "rust async programming best practices"
}
```

---

### 7. `todo_list`

Tracks the agent's running to-do list. It starts when the plan is first issued, updates as steps change state, and completes when the turn ends.

**Item Type:** `todo_list`

**Fields:**
- `id`: String - Unique identifier for this item
- `type`: `"todo_list"`
- `items`: Array of todo items, each containing:
  - `text`: String - The description of the todo item
  - `completed`: Boolean - Whether the item is completed

**Example:**
```json
{
  "id": "item_0",
  "type": "todo_list",
  "items": [
    {
      "text": "Analyze the codebase",
      "completed": true
    },
    {
      "text": "Write the new feature",
      "completed": false
    },
    {
      "text": "Add tests",
      "completed": false
    }
  ]
}
```

---

### 8. `error`

Describes a non-fatal error surfaced as an item (distinct from the top-level error event).

**Item Type:** `error`

**Fields:**
- `id`: String - Unique identifier for this item
- `type`: `"error"`
- `message`: String - The error message

**Example:**
```json
{
  "id": "item_0",
  "type": "error",
  "message": "Warning: This operation may take a long time"
}
```

---

## Event Flow Examples

### Simple Command Execution Flow

```jsonl
{"type":"thread.started","thread_id":"abc123"}
{"type":"turn.started"}
{"type":"item.started","item":{"id":"item_0","type":"command_execution","command":"ls -la","aggregated_output":"","exit_code":null,"status":"in_progress"}}
{"type":"item.completed","item":{"id":"item_0","type":"command_execution","command":"ls -la","aggregated_output":"total 48\ndrwxr-xr-x  12 user  staff  384 Jan 15 09:00 .\n","exit_code":0,"status":"completed"}}
{"type":"turn.completed","usage":{"input_tokens":100,"cached_input_tokens":0,"output_tokens":50}}
```

### Multi-Step Plan Execution Flow

```jsonl
{"type":"thread.started","thread_id":"xyz789"}
{"type":"turn.started"}
{"type":"item.started","item":{"id":"item_0","type":"todo_list","items":[{"text":"Install dependencies","completed":false},{"text":"Run tests","completed":false}]}}
{"type":"item.started","item":{"id":"item_1","type":"command_execution","command":"npm install","aggregated_output":"","exit_code":null,"status":"in_progress"}}
{"type":"item.completed","item":{"id":"item_1","type":"command_execution","command":"npm install","aggregated_output":"added 42 packages","exit_code":0,"status":"completed"}}
{"type":"item.updated","item":{"id":"item_0","type":"todo_list","items":[{"text":"Install dependencies","completed":true},{"text":"Run tests","completed":false}]}}
{"type":"item.started","item":{"id":"item_2","type":"command_execution","command":"npm test","aggregated_output":"","exit_code":null,"status":"in_progress"}}
{"type":"item.completed","item":{"id":"item_2","type":"command_execution","command":"npm test","aggregated_output":"All tests passed!","exit_code":0,"status":"completed"}}
{"type":"item.updated","item":{"id":"item_0","type":"todo_list","items":[{"text":"Install dependencies","completed":true},{"text":"Run tests","completed":true}]}}
{"type":"item.completed","item":{"id":"item_0","type":"todo_list","items":[{"text":"Install dependencies","completed":true},{"text":"Run tests","completed":true}]}}
{"type":"turn.completed","usage":{"input_tokens":250,"cached_input_tokens":50,"output_tokens":120}}
```

### Error Handling Flow

```jsonl
{"type":"thread.started","thread_id":"err456"}
{"type":"turn.started"}
{"type":"item.started","item":{"id":"item_0","type":"command_execution","command":"invalid-command","aggregated_output":"","exit_code":null,"status":"in_progress"}}
{"type":"item.completed","item":{"id":"item_0","type":"command_execution","command":"invalid-command","aggregated_output":"command not found: invalid-command","exit_code":127,"status":"failed"}}
{"type":"error","message":"Command execution failed"}
{"type":"turn.failed","error":{"message":"Command execution failed"}}
```

---

## Usage

To consume these events, read the output line by line and parse each line as JSON. Each line represents a complete event object.

**Example in JavaScript/Node.js:**

```javascript
const readline = require('readline');
const { spawn } = require('child_process');

const codex = spawn('codex', ['exec', '--prompt', 'List files']);
const rl = readline.createInterface({
  input: codex.stdout,
  crlfDelay: Infinity
});

rl.on('line', (line) => {
  try {
    const event = JSON.parse(line);
    console.log('Event type:', event.type);
    
    switch (event.type) {
      case 'thread.started':
        console.log('Thread ID:', event.thread_id);
        break;
      case 'item.completed':
        console.log('Item completed:', event.item.id);
        break;
      case 'turn.completed':
        console.log('Tokens used:', event.usage.input_tokens + event.usage.output_tokens);
        break;
    }
  } catch (e) {
    console.error('Failed to parse event:', line);
  }
});
```

**Example in Python:**

```python
import json
import subprocess

process = subprocess.Popen(
    ['codex', 'exec', '--prompt', 'List files'],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

for line in process.stdout:
    try:
        event = json.loads(line)
        event_type = event.get('type')
        
        if event_type == 'thread.started':
            print(f"Thread started: {event['thread_id']}")
        elif event_type == 'item.completed':
            print(f"Item completed: {event['item']['id']}")
        elif event_type == 'turn.completed':
            usage = event['usage']
            print(f"Turn completed. Tokens: {usage['input_tokens'] + usage['output_tokens']}")
    except json.JSONDecodeError:
        print(f"Failed to parse: {line}")
```

---

## Notes

- All events are emitted in chronological order
- Item IDs are unique within a thread and increment sequentially (e.g., `item_0`, `item_1`, `item_2`)
- A turn may contain multiple items of various types
- The `item.started` event indicates the beginning of an operation, while `item.completed` indicates its conclusion
- Some items (like `agent_message`, `reasoning`, `web_search`) only emit `item.completed` events without a prior `item.started`
- The `todo_list` item type will emit `item.started`, potentially multiple `item.updated` events as steps progress, and finally `item.completed` when the turn ends
