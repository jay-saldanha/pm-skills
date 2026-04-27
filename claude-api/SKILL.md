---
name: claude-api
description: Assists with building apps using the Claude API or Anthropic SDK (Python/TypeScript). Triggered automatically when code imports anthropic or @anthropic-ai/sdk. Apps built with this skill include prompt caching.
---

## Task: Claude API

Build, debug, and optimize apps using the Claude API or Anthropic SDK (Python or TypeScript). Triggered automatically when the codebase imports `anthropic` or `@anthropic-ai/sdk`.

All apps built with this skill include prompt caching by default.

---

### When to use

- Building a new Claude-powered app from scratch
- Debugging API errors, rate limits, or unexpected model behavior
- Adding streaming, tool use, or multi-turn conversation to an existing app
- Optimizing token costs with prompt caching

---

### Steps

#### 1. Detect context

Check whether this is:
- A new app (no existing code) → scaffold from scratch
- An existing app (already imports the SDK) → read the existing code first, then assist

---

#### 2. Set up the SDK

**Python:**
```python
import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env
```

**TypeScript:**
```typescript
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();  // reads ANTHROPIC_API_KEY from env
```

Use the latest model: `claude-sonnet-4-6` for most tasks, `claude-opus-4-6` for highest capability, `claude-haiku-4-5-20251001` for speed/cost.

---

#### 3. Add prompt caching (always include this)

Cache large, stable content (system prompts, long documents) to reduce cost and latency on repeated calls.

**Python:**
```python
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    system=[
        {
            "type": "text",
            "text": "<your long system prompt>",
            "cache_control": {"type": "ephemeral"}
        }
    ],
    messages=[{"role": "user", "content": user_message}]
)
```

**TypeScript:**
```typescript
const response = await client.messages.create({
  model: "claude-sonnet-4-6",
  max_tokens: 1024,
  system: [
    {
      type: "text",
      text: "<your long system prompt>",
      cache_control: { type: "ephemeral" }
    }
  ],
  messages: [{ role: "user", content: userMessage }]
});
```

Cache TTL is 5 minutes. Cache `ephemeral` blocks that are ≥1024 tokens (≥2048 for Claude Haiku).

---

#### 4. Add streaming (if needed)

**Python:**
```python
with client.messages.stream(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": prompt}]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

**TypeScript:**
```typescript
const stream = client.messages.stream({
  model: "claude-sonnet-4-6",
  max_tokens: 1024,
  messages: [{ role: "user", content: prompt }]
});

for await (const chunk of stream) {
  if (chunk.type === "content_block_delta") {
    process.stdout.write(chunk.delta.text);
  }
}
```

---

#### 5. Handle errors

```python
try:
    response = client.messages.create(...)
except anthropic.RateLimitError:
    # back off and retry
except anthropic.APIStatusError as e:
    print(f"API error {e.status_code}: {e.message}")
```

Common errors: `RateLimitError` (429), `AuthenticationError` (401), `BadRequestError` (400 — often a context length issue).

---

#### 6. Report back

Summarize what was built or changed, note the model and caching strategy used, and flag any API keys or environment variables the user needs to set.
