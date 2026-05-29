"""Transport layer: drive Claude through the Agent SDK instead of `claude -p`.

khazad-dum used to shell out with ``subprocess.run(["claude", "-p", prompt])``,
which gave the agent the full Claude Code toolset and no way to scope what it
could touch. This module wraps the Agent SDK's ``query()`` so each invocation
declares a *mode* that controls tool access:

- ``Mode.TEXT``      — no tools, no ambient config. The agent answers purely from
                       the prompt it is given (questionnaires, summaries). It
                       cannot read or write files. khazad-dum persists the output.
- ``Mode.READ_ONLY`` — may read/search the working tree (Read/Glob/Grep) but
                       cannot modify files or run commands (review/analysis).
- ``Mode.WRITE``     — full coding: read, write, edit, run commands, autonomously
                       (Phase 2 build work). Runs with bypassed permission prompts.

Auth follows the locally installed ``claude`` binary (subscription/CLI login);
no ANTHROPIC_API_KEY is required. The SDK is imported lazily so the rest of the
CLI keeps working even if it (or the ``claude`` binary) is missing.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional, Sequence


class Mode(str, Enum):
    """How much of the toolset an invocation is allowed to use."""

    TEXT = "text"
    READ_ONLY = "read_only"
    WRITE = "write"


# Tool buckets, by capability. Names match the Agent SDK's built-in tools.
_READ_TOOLS = ["Read", "Glob", "Grep"]
_MUTATE_TOOLS = ["Write", "Edit", "MultiEdit", "NotebookEdit"]
_EXEC_TOOLS = ["Bash", "BashOutput", "KillShell"]
# Everything a TEXT run must be denied so it answers from the prompt alone.
_NON_TEXT_TOOLS = _READ_TOOLS + _MUTATE_TOOLS + _EXEC_TOOLS + [
    "WebFetch",
    "WebSearch",
    "Task",
    "Agent",
]

# claude_code preset = the same system prompt the `claude` CLI uses, so coding
# runs behave like the old `claude -p`. TEXT runs get no preset (clean context).
_CLAUDE_CODE_PRESET = {"type": "preset", "preset": "claude_code"}

# Sentinel: "caller did not override this, pick a per-mode default".
_UNSET = object()


@dataclass
class Result:
    """Outcome of a single invocation, distilled from the SDK's ResultMessage."""

    text: str
    is_error: bool
    subtype: Optional[str] = None
    num_turns: Optional[int] = None
    cost_usd: Optional[float] = None


class ClaudeUnavailable(RuntimeError):
    """The SDK package or the `claude` binary could not be found/launched."""


def _build_options(
    mode: Mode,
    *,
    cwd: Optional[Path],
    system_prompt,
    model: Optional[str],
    max_turns: Optional[int],
    allowed_tools: Optional[Sequence[str]],
    disallowed_tools: Optional[Sequence[str]],
    setting_sources: Optional[Sequence[str]],
):
    """Translate a Mode (+ overrides) into a ClaudeAgentOptions instance."""
    from claude_agent_sdk import ClaudeAgentOptions

    # Per-mode defaults; any explicit argument wins over them.
    if mode is Mode.TEXT:
        default_allowed: Sequence[str] = []
        default_disallowed: Sequence[str] = _NON_TEXT_TOOLS
        permission_mode = "default"
        default_system = None
    elif mode is Mode.READ_ONLY:
        default_allowed = _READ_TOOLS
        default_disallowed = _MUTATE_TOOLS + _EXEC_TOOLS
        permission_mode = "default"
        default_system = _CLAUDE_CODE_PRESET
    elif mode is Mode.WRITE:
        default_allowed = []  # empty + bypass = every tool auto-approved
        default_disallowed = []
        permission_mode = "bypassPermissions"
        default_system = _CLAUDE_CODE_PRESET
    else:  # pragma: no cover - exhaustive
        raise ValueError(f"Unknown mode: {mode!r}")

    resolved_system = default_system if system_prompt is _UNSET else system_prompt

    kwargs = dict(
        allowed_tools=list(allowed_tools if allowed_tools is not None else default_allowed),
        disallowed_tools=list(
            disallowed_tools if disallowed_tools is not None else default_disallowed
        ),
        permission_mode=permission_mode,
        # Empty by default: khazad-dum assembles the whole prompt, so we don't
        # want ambient CLAUDE.md / settings / skills leaking into a run.
        setting_sources=list(setting_sources if setting_sources is not None else []),
    )
    if resolved_system is not None:
        kwargs["system_prompt"] = resolved_system
    if cwd is not None:
        kwargs["cwd"] = str(cwd)
    if model is not None:
        kwargs["model"] = model
    if max_turns is not None:
        kwargs["max_turns"] = max_turns

    return ClaudeAgentOptions(**kwargs)


async def _run_async(prompt: str, options, *, stream: bool) -> Result:
    from claude_agent_sdk import (
        AssistantMessage,
        ResultMessage,
        TextBlock,
        ToolUseBlock,
        query,
    )

    final: Optional[ResultMessage] = None
    printed_any = False

    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock) and stream and block.text:
                    print(block.text, end="", flush=True)
                    printed_any = True
                elif isinstance(block, ToolUseBlock) and stream:
                    print(f"\n  → {block.name}", flush=True)
        elif isinstance(message, ResultMessage):
            final = message

    if stream and printed_any:
        print()

    if final is None:
        raise ClaudeUnavailable("claude returned no result message")

    return Result(
        text=getattr(final, "result", "") or "",
        is_error=bool(getattr(final, "is_error", False)),
        subtype=getattr(final, "subtype", None),
        num_turns=getattr(final, "num_turns", None),
        cost_usd=getattr(final, "total_cost_usd", None),
    )


def run_prompt(
    prompt: str,
    *,
    mode: Mode = Mode.WRITE,
    cwd: Optional[Path] = None,
    system_prompt=_UNSET,
    model: Optional[str] = None,
    max_turns: Optional[int] = None,
    allowed_tools: Optional[Sequence[str]] = None,
    disallowed_tools: Optional[Sequence[str]] = None,
    setting_sources: Optional[Sequence[str]] = None,
    stream: bool = True,
) -> Result:
    """Run a single prompt through the Agent SDK and return its Result.

    Streams the agent's text (and tool activity) to stdout as it arrives so the
    CLI keeps the live-progress feel of the old subprocess call. Raises
    ``ClaudeUnavailable`` if the SDK package or the ``claude`` binary is missing;
    other SDK errors propagate so genuine failures stay visible.
    """
    try:
        from claude_agent_sdk import ClaudeAgentOptions  # noqa: F401  (probe import)
    except ImportError as exc:
        raise ClaudeUnavailable(
            "claude-agent-sdk is not installed. Install it with "
            "`pip install claude-agent-sdk`."
        ) from exc

    options = _build_options(
        mode,
        cwd=cwd,
        system_prompt=system_prompt,
        model=model,
        max_turns=max_turns,
        allowed_tools=allowed_tools,
        disallowed_tools=disallowed_tools,
        setting_sources=setting_sources,
    )

    try:
        return asyncio.run(_run_async(prompt, options, stream=stream))
    except ClaudeUnavailable:
        raise
    except Exception as exc:  # surface SDK launch failures as ClaudeUnavailable
        # CLINotFoundError / connection errors mean the `claude` binary is the
        # problem; map those, but let other (real) errors carry their own type.
        name = type(exc).__name__
        if name in {"CLINotFoundError", "CLIConnectionError", "ProcessError"}:
            raise ClaudeUnavailable(str(exc) or name) from exc
        raise
