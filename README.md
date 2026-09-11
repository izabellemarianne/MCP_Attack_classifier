## Running the Model Server

### 1. Start the API server

From the project root, run:

```bash
OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 TOKENIZERS_PARALLELISM=false \
uvicorn serving.deploy:app --host 127.0.0.1 --port 8000
```

The server will start at:

```text
http://127.0.0.1:8000
```

Keep this terminal running while sending requests.

### 2. Input format

The `/predict` endpoint expects a JSON object containing a `response` field.

`response` should be a list of message objects. Each message contains:

* `type`: the message type, such as `HumanMessage`, `AIMessage`, `ToolMessage`, or `SystemMessage`
* `content`: the message content
* `tool_calls`: included for `AIMessage` objects when the model makes a tool call

A minimal request looks like:

```json
{
  "response": [
    {
      "type": "HumanMessage",
      "content": "What is the weather in Toronto?"
    }
  ]
}
```

### 3. Send a prediction request

Open a **second terminal window** and run:

```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"response": [{"type": "HumanMessage", "content": "What is the weather in Toronto?"}]}'
```

### 4. Example: multi-message tool-call trace

The `response` field can contain an entire agent interaction, including system messages, user messages, tool calls, and tool outputs.

For example:

```json
{
  "response": [
    {
      "type": "SystemMessage",
      "content": "You are a helpful assistant."
    },
    {
      "type": "HumanMessage",
      "content": "Search for the weather in Toronto."
    },
    {
      "type": "AIMessage",
      "tool_calls": [
        {
          "name": "weather_search",
          "args": {
            "location": "Toronto"
          },
          "id": "call_123",
          "type": "tool_call"
        }
      ]
    },
    {
      "type": "ToolMessage",
      "content": "{\"temperature\": 20, \"condition\": \"sunny\"}"
    }
  ]
}
```

This format allows the model to receive the complete sequence of messages and tool interactions as a single `response`.

### 5. Testing attack and benign examples

For benchmark evaluation, the same `/predict` endpoint can be used for both benign and attack traces. The primary difference is the content of the `response` sequence.

For example:

```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"response": [{"type": "HumanMessage", "content": "What is the weather in Toronto?"}]}'
```

For longer traces, preserve the same JSON structure and include the complete sequence of `SystemMessage`, `HumanMessage`, `AIMessage`, and `ToolMessage` objects as required by the benchmark.

### 6. Endpoint

| Method | Endpoint   | Description                          |
| ------ | ---------- | ------------------------------------ |
| `POST` | `/predict` | Classifies a message/tool-call trace |

The request body must contain a `response` list following the message format described above.
