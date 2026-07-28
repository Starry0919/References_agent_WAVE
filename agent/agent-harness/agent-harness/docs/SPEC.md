# Agent Harness — Build Specification (authoritative contract)

Every implementer MUST follow this document exactly: file paths, names, signatures,
JSON shapes. Independently written parts are integrated later — drift breaks the build.

## 0. Overview

A local-first agent harness:

- **Backend**: Python 3.10+, FastAPI + uvicorn. Runs an LLM tool-calling loop over
  the OpenAI-compatible chat protocol.
- **Providers**: a pluggable vendor registry (`harness/providers.py`). Default is
  DeepSeek with model `deepseek-v4-pro`; switching vendors (OpenAI, Moonshot, Qwen,
  Zhipu, or any custom OpenAI-compatible endpoint) is a `.env` change, never a code
  change.
- **Tools**: pluggable modules. Drop a `.py` file into `tools/` at the project root,
  decorate a function with `@tool`, restart (or `--reload`) — the agent can call it.
- **Frontend**: one self-contained `web/index.html` (no build step, no CDN). Live
  monitoring of every agent step over WebSocket. UI copy in Chinese.
- **Persistence**: JSONL per session under `runs/`.

Code identifiers/comments in English; README and UI copy in Chinese.

## 1. Repository layout

```
agent-harness/
├── .env                  # real secrets (exists; NEVER print or overwrite)
├── .env.example
├── .gitignore
├── README.md             # Chinese
├── requirements.txt
├── main.py               # entry: python main.py [--reload] [--host H] [--port P]
├── docs/SPEC.md          # this file
├── harness/
│   ├── __init__.py
│   ├── config.py
│   ├── providers.py      # vendor registry: presets + strict/lenient resolution
│   ├── llm.py
│   ├── agent.py
│   ├── events.py
│   ├── sessions.py
│   ├── server.py
│   └── tools/
│       ├── __init__.py   # re-exports: tool, REGISTRY, all_tools, get_tool, execute_tool
│       ├── base.py
│       ├── loader.py
│       └── builtin/
│           ├── __init__.py
│           ├── calculator.py
│           └── clock.py
├── tools/                # USER tool modules, auto-discovered (ships with 2 examples)
│   ├── http_get.py
│   └── read_file.py
├── web/
│   └── index.html
├── runs/                 # created at runtime, gitignored
└── workspace/            # created at runtime, gitignored; sandbox for file tools
```

Project root at runtime = `Path(harness/__file__).resolve().parent.parent`.
`main.py` must insert the project root into `sys.path` defensively before
importing `harness`.

## 2. Config — `harness/config.py`

Load `.env` from project root via `python-dotenv` (`load_dotenv(override=False)`).
Dataclass `Settings` with fields (env var of same name; defaults shown):

| field | type | default |
|---|---|---|
| LLM_PROVIDER | str | "deepseek" (preset name in harness/providers.py) |
| LLM_MODEL | str | "" (empty = preset's default model; required for presets without one) |
| LLM_BASE_URL | str | "" (empty = preset's base URL; required for the `custom` preset) |
| LLM_API_KEY | str | "" (empty = read the preset's own key env var, e.g. DEEPSEEK_API_KEY) |
| MAX_STEPS | int | 30 |
| TOOL_TIMEOUT_S | float | 60 |
| LLM_TIMEOUT_S | float | 120 |
| LLM_RETRIES | int | 3 |
| LLM_MAX_TOKENS | int \| None | None |
| TEMPERATURE | float \| None | None |
| HOST | str | "127.0.0.1" |
| PORT | int | 8642 |
| SYSTEM_PROMPT | str | see below |

Vendor-specific key env vars (DEEPSEEK_API_KEY, OPENAI_API_KEY, ...) are NOT
Settings fields — presets read them from the environment (populated by
load_dotenv) via their `key_env` name; see §10.

`get_settings() -> Settings` cached singleton. Never log the API key.

Default system prompt (English text, verbatim spirit): a capable general agent running
in a local harness; may call the provided tools, may call them repeatedly and reason
over results before deciding the next step; keep answers grounded in tool results;
respond in the user's language.

## 3. Tool system

### 3.1 `harness/tools/base.py`

- `@tool` decorator, usable bare (`@tool`) or with args
  (`@tool(name=..., description=..., timeout=...)`). Works on sync **and** async functions.
- Builds an OpenAI-style JSON Schema from the signature:
  - type hints: `str`→string, `int`→integer, `float`→number, `bool`→boolean,
    `list`/`list[X]`→array (with `items` when X is a supported scalar), `dict`→object;
    `Optional[X]`/`X | None`→X, not required. Missing hint → string.
  - parameter has a default → not in `required`; otherwise required.
  - description: docstring text before the `Args:` line; per-param descriptions parsed
    from a Google-style `Args:` section (best-effort; absent is fine).
- `ToolSpec` dataclass: `name, description, parameters (dict), func, timeout (float|None),
  is_async (bool), source (str module/file)`. Method `to_openai() -> dict` returning
  `{"type": "function", "function": {"name", "description", "parameters"}}`.
- Registry: module-level `REGISTRY: dict[str, ToolSpec]`; `register(spec)` replaces on
  duplicate name with a `logging.warning`; `get_tool(name) -> ToolSpec | None`;
  `all_tools() -> list[ToolSpec]` (sorted by name).
- `ToolOutcome` dataclass: `result: str, is_error: bool, duration_ms: int`.
- `async execute_tool(name: str, arguments: dict) -> ToolOutcome`:
  - unknown tool → error outcome, never raises.
  - call `func(**arguments)`; sync funcs via `asyncio.to_thread`; whole call wrapped in
    `asyncio.wait_for(timeout=spec.timeout or settings.TOOL_TIMEOUT_S)`.
  - `TypeError` (bad args), timeout, or any exception → `is_error=True`, result is a
    readable one-line message like `"ERROR: <ExcType>: <msg>"`. The agent loop must
    never crash because of a tool.
  - non-`str` return values are `json.dumps(..., ensure_ascii=False, default=str)`.
  - results longer than 50_000 chars truncated with suffix `"\n...[truncated {n} chars]"`.

### 3.2 `harness/tools/loader.py`

`load_all_tools() -> list[str]` (returns error strings for reporting):
1. Import every module in the `harness.tools.builtin` package (pkgutil).
2. Import every top-level `*.py` in project-root `tools/` (skip names starting with `_`),
   via `importlib.util.spec_from_file_location` with unique module names
   (`user_tools.<stem>`).
3. An exception importing one file is caught, logged as a warning, appended to the
   returned error list — a broken user tool must never prevent startup.

### 3.3 Builtins

- `calculator(expression: str) -> str`: safe arithmetic via `ast` whitelist
  (numbers, + - * / // % **, unary ±, parentheses). NO `eval`.
- `clock() -> str`: current local time, ISO format with tz.

### 3.4 Example user tools in `tools/` (templates; rich Chinese comments explaining
how to write your own)

- `http_get(url: str, timeout: float = 20) -> str`: GET via `httpx`, return
  `"HTTP {status}\n{first 5000 chars of body text}"`.
- `read_file(path: str) -> str`: read a text file **restricted to `workspace/`**:
  resolve against `<project root>/workspace`, reject anything escaping it
  (return an ERROR string, don't raise). Root computed as
  `Path(__file__).resolve().parent.parent / "workspace"`.

Both import the decorator as: `from harness.tools import tool`.

## 4. LLM client — `harness/llm.py`

- `ToolCallReq` dataclass: `id: str, name: str, arguments_json: str` (raw JSON string).
- `AssistantTurn` dataclass: `content: str, thinking: str, tool_calls: list[ToolCallReq],
  finish_reason: str | None, usage: dict | None`.
- `class LLMError(Exception)` with readable message.
- `class LLMClient`:
  `async chat(messages: list[dict], tools: list[dict], on_delta=None, on_thinking_delta=None) -> AssistantTurn`
  - Connection info (api_key, base_url, model) comes from `providers.resolve()`
    (§10), captured once at client construction; `ProviderError` is re-raised as
    `LLMError`. Uses `openai.AsyncOpenAI(api_key, base_url, timeout=LLM_TIMEOUT_S)`,
    `stream=True`, passing `tools=tools` when non-empty; include
    `max_tokens`/`temperature` only if set.
  - Accumulate stream deltas: `delta.content` → append to content, `await on_delta(text)`
    if provided; `delta.reasoning_content` (DeepSeek reasoning models; use getattr,
    field may not exist) → thinking, `await on_thinking_delta(text)`;
    `delta.tool_calls` → accumulate by `index` (first chunk carries id/name; later
    chunks append `function.arguments` fragments).
  - Retries: on connection errors, 429, and 5xx — up to LLM_RETRIES attempts total,
    backoff 1s/2s/4s. 4xx other than 429 → raise `LLMError` immediately with the
    server's message. Exhausted retries → `LLMError`.
- `get_llm_client() -> LLMClient`: process-wide cached singleton (one httpx pool
  reused across turns; provider changes in .env take effect on restart).

## 5. Event contract (`harness/events.py`)

`Event` dataclass: `seq: int` (per-session, monotonic from 1), `type: str`,
`ts: float` (unix seconds), `data: dict`. `to_dict()` → `{"seq", "type", "ts", "data"}`.

Event types and their `data`:

| type | data |
|---|---|
| `user_message` | `{content}` |
| `run_started` | `{run_id}` (uuid hex) |
| `llm_call_started` | `{step}` (1-based) |
| `assistant_thinking_delta` | `{text}` |
| `assistant_delta` | `{text}` |
| `assistant_message` | `{content, thinking, tool_calls: [{id, name, arguments}]}` — `arguments` parsed object, or raw string if unparsable |
| `tool_call` | `{id, name, arguments}` (emitted immediately before execution) |
| `tool_result` | `{id, name, result, is_error, duration_ms}` |
| `run_finished` | `{status: "completed"\|"stopped"\|"error"\|"max_steps", error?}` |
| `session_meta` | `{title}` |

`EventBus` (one per session): `publish(event)` appends to the session's event list,
persists it (§6), and fans out to subscriber `asyncio.Queue`s (maxsize 1000;
`put_nowait` in try/except — a full/broken subscriber is dropped, never blocks
the loop). `subscribe()` → async context manager yielding a queue.

## 6. Sessions & persistence — `harness/sessions.py`

`Session`: `id` (uuid4 hex[:12]), `title` (default `"新会话"`), `created_at: float`,
`status: "idle"|"running"`, `messages: list[dict]` (OpenAI format, seeded with the
system prompt), `events: list[Event]`, `bus: EventBus`, `current_task: asyncio.Task | None`,
seq counter. `next_seq()`.

`SessionStore`:
- Ensures `runs/` exists. In-memory `dict[str, Session]`.
- Persistence: append-only `runs/{id}.jsonl`. Line kinds:
  - `{"kind": "meta", "id", "title", "created_at"}` — written at create and again on
    title change (last meta wins on load).
  - `{"kind": "message", "message": {...}}` — every message appended to `messages`,
    including the initial system message.
  - `{"kind": "event", "event": {seq, type, ts, data}}`
- On startup, load all `runs/*.jsonl` back into memory (skip corrupt lines with a
  warning; resume seq from max loaded). Loaded sessions get `status="idle"`.
- `create() -> Session`; `get(id)`; `list() -> list[Session]` sorted by created_at desc;
  `delete(id)` removes memory + file (refuse while running).
- Title: on the first user message of a session, set title to its first 40 chars
  (single line) and emit `session_meta`.

## 7. Agent loop — `harness/agent.py`

`async def run_agent_turn(store: SessionStore, session: Session, user_content: str) -> None`

1. `session.status = "running"`. Emit `user_message`, append user message. Set title
   if first user message (§6). Emit `run_started`.
2. For `step` in `1..MAX_STEPS`:
   - Emit `llm_call_started {step}`.
   - `turn = await client.chat(messages, [t.to_openai() for t in all_tools()],
     on_delta→emit assistant_delta, on_thinking_delta→emit assistant_thinking_delta)`.
   - Append assistant message:
     `{"role": "assistant", "content": turn.content or ""}`, plus key
     `"tool_calls": [{"id", "type": "function", "function": {"name", "arguments": raw}}]`
     only when tool_calls exist. Emit `assistant_message` (arguments parsed via
     json.loads best-effort for display).
   - No tool calls → emit `run_finished {status: "completed"}`; return.
   - Else execute tool calls **sequentially in order**: emit `tool_call`; parse
     arguments with `json.loads` (parse failure → don't execute; outcome =
     `ERROR: could not parse tool arguments as JSON: ...`, is_error=True);
     else `await execute_tool(...)`. Append
     `{"role": "tool", "tool_call_id": id, "content": outcome.result}`;
     emit `tool_result`.
3. Loop exhausted → emit `run_finished {status: "max_steps"}`.
4. `except asyncio.CancelledError`: backfill (below), emit
   `run_finished {status: "stopped"}`, swallow (do not re-raise).
5. `except Exception as e`: backfill, emit `run_finished {status: "error",
   error: str(e)}`. Never let the exception escape to crash the server.
6. `finally`: `session.status = "idle"`, `session.current_task = None`.

**Backfill rule** (protocol integrity): if the last assistant message has `tool_calls`
whose ids lack a following `role=tool` message, append
`{"role": "tool", "tool_call_id": id, "content": "ERROR: run interrupted before this tool finished"}`
for each unanswered id — otherwise the next LLM call would be rejected.

## 8. HTTP/WS API — `harness/server.py`, `main.py`

`create_app() -> FastAPI` using a **lifespan** context (not deprecated on_event):
on startup call `load_all_tools()`, init the `SessionStore`, ensure `workspace/`
exists, log a summary line (tool count, provider, model via the lenient
`providers.describe()`). Module level:
`app = create_app()` so `uvicorn harness.server:app` works. Bind localhost only.

| route | behavior |
|---|---|
| `GET /` | `FileResponse` of `web/index.html` |
| `GET /api/health` | `{"ok": true, "provider": str, "model": str, "tools": int}` (via lenient `providers.describe()` — never 500s on incomplete config) |
| `GET /api/tools` | `{"tools": [{"name", "description", "parameters", "source"}]}` |
| `GET /api/sessions` | `{"sessions": [{"id", "title", "created_at", "status", "event_count"}]}` (desc) |
| `POST /api/sessions` | create → same summary shape, 200 |
| `GET /api/sessions/{id}` | `{"id", "title", "created_at", "status", "events": [event dicts]}`; 404 unknown |
| `DELETE /api/sessions/{id}` | `{"deleted": true}`; 409 if running; 404 unknown |
| `POST /api/sessions/{id}/messages` | body `{"content": str}` (reject empty/blank → 422). 409 `{"detail": "session is busy"}` if running. Else spawn `asyncio.create_task(run_agent_turn(...))`, store as `current_task`, return 202 `{"accepted": true}` |
| `POST /api/sessions/{id}/stop` | cancel `current_task` if running → `{"stopped": true}` else `{"stopped": false}` |
| `WS /ws/{id}` | on connect: send every existing event (as normal frames, in order), then live events from a bus subscription. Also send `{"type": "ping"}` every 20s. Clean up subscription on disconnect. Unknown id → close. |

WS frames are exactly `Event.to_dict()` JSON, or `{"type": "ping"}` (no `seq` key —
clients ignore frames without `seq`).

`main.py`: argparse `--host --port --reload`; print a short Chinese banner (URL,
provider, model) then
`uvicorn.run("harness.server:app", host=..., port=..., reload=args.reload)`.

## 9. Frontend — `web/index.html` (single file, no external requests)

Layout:
- **Left sidebar**: title "Agent Harness"; provider chip + model chip from
  `/api/health`; "新建会话" button; session list (title, relative time,
  status dot — green idle / pulsing amber running; hover shows a delete ✕ that calls
  DELETE with confirm()); collapsible "工具 (N)" section listing registered tools
  (name + description).
- **Main**: header (session title, run status, 「停止」 button visible while running);
  scrollable timeline; composer (textarea, Enter=发送 / Shift+Enter=换行; send disabled
  while running).

Timeline rendering (drive EVERYTHING from events — history replay and live WS use the
same renderer):
- `user_message` → right-aligned bubble.
- `llm_call_started` → subtle divider `第 N 步 · 思考中…`.
- `assistant_thinking_delta` → stream into a collapsed-by-default muted accordion
  「思考过程」 attached to the current step.
- `assistant_delta` → stream into the current assistant bubble (create on first delta).
- `assistant_message` → finalize: replace the streaming bubble's text with
  `data.content` (skip bubble entirely if content empty); store thinking.
- `tool_call` → card: 🔧 tool name, pretty-printed JSON args (collapsible), spinner
  until the matching `tool_result` arrives (pair by `id`).
- `tool_result` → fill the card: monospace pre-wrap result (max-height ~16rem with
  「展开」 toggle for long output), red accent + ⚠ when `is_error`, duration badge.
- `run_finished` → status line: ✓ 已完成 / ⏹ 已停止 / ⚠ 出错(show error)/
  ⚠ 达到最大步数.
- `session_meta` → update titles in place.

Behavior:
- On load: `GET /api/sessions`; select the newest or auto-create one. Selecting a
  session closes the previous WS, clears the timeline, opens `WS /ws/{id}` (backlog
  replays through the renderer).
- Dedup by `seq` (track last seen per session; ignore `seq <= lastSeen`). Ignore
  frames without `seq`. WS auto-reconnect with backoff (1s→2s→4s→…max 15s).
- Auto-scroll pinned to bottom unless the user scrolled up (resume pin when they
  return to bottom).
- **Security**: all dynamic text via `textContent`/`createElement` — never innerHTML
  with server/LLM data. Assistant final text gets minimal safe markdown (escape
  first; then fenced code blocks, `inline code`, **bold**, links) — implement
  escape-then-transform, or DOM-build directly.
- Theming: CSS variables, `prefers-color-scheme` dark/light. Clean, minimal, modern:
  system-ui font stack, generous spacing, rounded cards, subtle borders. UI copy 中文.

## 10. Provider registry — `harness/providers.py`

- `Provider` frozen dataclass: `name, base_url, key_env (str, env var holding that
  vendor's API key), default_model (str, "" = must set LLM_MODEL)`.
- `PROVIDERS: dict[str, Provider]` presets — all OpenAI-compatible:
  `deepseek` (https://api.deepseek.com, DEEPSEEK_API_KEY, default model
  `deepseek-v4-pro`), `openai`, `moonshot`, `qwen` (DashScope compatible mode),
  `zhipu`, and `custom` (empty base_url; everything comes from LLM_* overrides).
  Adding a vendor permanently = one line here.
- `ResolvedProvider` frozen dataclass: `name, base_url, api_key, model`.
- `resolve() -> ResolvedProvider` (strict; used by LLMClient): unknown provider →
  `ProviderError` listing known names; then base_url (LLM_BASE_URL else preset's,
  required), api_key (LLM_API_KEY else `os.environ[preset.key_env]`, required),
  model (LLM_MODEL else preset default, required). Every error message names the
  exact env var to set.
- `describe() -> dict {provider, model, base_url}` (lenient; used by banner and
  `/api/health`): never raises, never includes the key.
- Only real runs exist — there is deliberately NO mock/offline mode in this project.

## 11. `requirements.txt` (exact content)

```
fastapi>=0.110
uvicorn[standard]>=0.29
openai>=1.40
python-dotenv>=1.0
httpx>=0.27
```

## 12. `README.md` (Chinese) — required sections

项目简介(一句话 + 特性列表)/ 快速开始(uv 或 venv+pip 两种;`python main.py`;
打开 http://127.0.0.1:8642)/ **添加自己的工具**(核心章节:完整可复制的模板、
类型注解与 docstring 如何映射成 schema、同步/异步、超时、`--reload` 热重载)/
配置项表格(§2)/ 切换模型供应商(预设切换、custom 自建端点、如何永久新增一家)/
项目结构树 / HTTP & WS API 简表 / 常见问题(换模型或供应商、工具报错去哪看、
会话数据存哪、如何清空)。内容必须与代码实际行为一致。

## 13. Quality bar

Type hints everywhere; docstrings on public functions; `logging` (INFO) instead of
print (except the main.py banner and smoke.py output); no state outside the documented
singletons; Ctrl-C exits cleanly; the API key is never logged, never sent to the
frontend, never echoed in errors.
