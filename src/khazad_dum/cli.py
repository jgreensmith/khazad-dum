from __future__ import annotations

import argparse
import subprocess
import sys
from importlib import resources
from pathlib import Path

from .state import State, STATE_DIR_NAME
from .steps import STEPS, Step, get_step
from .tokens import assert_within_limit, count_tokens, MAX_TOKENS


DOCS_DIR = "documentation"
NOTES_PROJECTS_DIR = Path.home() / "Notes" / "Projects"


def _template_text(relative: str) -> str:
    return (resources.files("khazad_dum.workflows") / relative).read_text()


def _project_root() -> Path:
    return Path.cwd()


def _docs_root(project_root: Path) -> Path:
    return project_root / DOCS_DIR


def _is_initialised(project_root: Path) -> bool:
    return (project_root / STATE_DIR_NAME).exists() and _docs_root(project_root).exists()


def _require_init(project_root: Path) -> None:
    if not _is_initialised(project_root):
        sys.exit("khazad-dum is not initialised here. Run `khazad-dum init` first.")


def cmd_init(args: argparse.Namespace) -> None:
    project_root = _project_root()
    docs = _docs_root(project_root)

    if docs.exists() and not docs.is_symlink() and any(docs.iterdir()):
        if not args.force:
            sys.exit(f"{docs} already exists and is not empty. Use --force to proceed.")

    docs.mkdir(parents=True, exist_ok=True)

    for step in STEPS:
        step_dir = docs / step.dir_name
        (step_dir / "input").mkdir(parents=True, exist_ok=True)
        (step_dir / "process").mkdir(parents=True, exist_ok=True)
        (step_dir / "output").mkdir(parents=True, exist_ok=True)
        scope_path = step_dir / "input" / "scope.md"
        if not scope_path.exists():
            scope_template = _template_text(step.scope_template_path)
            scope_path.write_text(f"# {step.name} — Scope\n\n{scope_template}")

    (project_root / STATE_DIR_NAME).mkdir(exist_ok=True)
    State.load(project_root).save(project_root)

    _create_notes_symlink(project_root, docs)

    print(f"Initialised khazad-dum in {project_root}")
    print(f"  documentation/  ({len(STEPS)} steps)")
    print(f"  {STATE_DIR_NAME}/state.json")


def _create_notes_symlink(project_root: Path, docs: Path) -> None:
    if not NOTES_PROJECTS_DIR.exists():
        print(f"  (skipped symlink: {NOTES_PROJECTS_DIR} does not exist)")
        return
    link = NOTES_PROJECTS_DIR / project_root.name
    if link.exists() or link.is_symlink():
        if link.is_symlink() and link.resolve() == docs.resolve():
            print(f"  symlink already in place: {link} -> {docs}")
            return
        print(f"  (skipped symlink: {link} already exists)")
        return
    link.symlink_to(docs, target_is_directory=True)
    print(f"  linked {link} -> {docs}")


def cmd_status(args: argparse.Namespace) -> None:
    project_root = _project_root()
    if not _is_initialised(project_root):
        print("khazad-dum is not initialised here. Run `khazad-dum init`.")
        return
    state = State.load(project_root)
    print(f"Project: {project_root}")
    print("Steps:")
    for step in STEPS:
        if step.dir_name in state.completed:
            marker = "[x]"
        elif state.current == step.dir_name:
            marker = "[~]"
        else:
            marker = "[ ]"
        print(f"  {marker} {step.index}. {step.name}  ({step.dir_name})")
        if step.sub_prompts:
            done_subs = state.sub_completed.get(step.dir_name, [])
            for sub in step.sub_prompts:
                sub_marker = "[x]" if sub in done_subs else "[ ]"
                print(f"       {sub_marker} {sub}")
    nxt = _next_pending(state)
    if nxt:
        print(f"\nNext pending: {nxt.index}. {nxt.name}")
        print(f"Run with: khazad-dum run {nxt.slug}")
    else:
        print("\nAll steps completed.")


def _next_pending(state: State) -> Step | None:
    for step in STEPS:
        if step.dir_name not in state.completed:
            return step
    return None


# Maps research sub-prompt name → template file stems to inject into the prompt.
_SUB_PROMPT_TEMPLATES: dict[str, tuple[str, ...]] = {
    "create-pre-literature-review-questionnaire": ("questionnaire",),
    "literature-review-decision": ("literature-review",),
    "create-post-literature-review-questionnaire": ("questionnaire",),
    "next-steps": (),
}


def _build_prompt(step: Step, project_root: Path) -> str:
    prompt = _template_text(f"{step.dir_name}/prompts/prompt.md")
    scope_path = _docs_root(project_root) / step.dir_name / "input" / "scope.md"
    scope = scope_path.read_text() if scope_path.exists() else ""
    parts = [prompt]
    if scope:
        parts.append(f"---\n\n## Scope\n\n{scope}")
    return "\n\n".join(parts)


def _build_sub_prompt(step: Step, sub_prompt: str, project_root: Path) -> str:
    process = _template_text(f"{step.dir_name}/prompts/{sub_prompt}.md")
    scope_path = _docs_root(project_root) / step.dir_name / "input" / "scope.md"
    scope = scope_path.read_text() if scope_path.exists() else ""
    parts = [process]
    if scope:
        parts.append(f"---\n\n## Project Description\n\n{scope}")
    for tname in _SUB_PROMPT_TEMPLATES.get(sub_prompt, ()):
        tmpl = _template_text(f"{step.dir_name}/templates/{tname}.md")
        parts.append(f"---\n\n## Template\n\n{tmpl}")
    return "\n\n".join(parts)


def _next_pending_sub_prompt(step: Step, state: State) -> str | None:
    done = state.sub_completed.get(step.dir_name, [])
    for sub in step.sub_prompts:
        if sub not in done:
            return sub
    return None


def cmd_run(args: argparse.Namespace) -> None:
    project_root = _project_root()
    _require_init(project_root)
    state = State.load(project_root)

    if args.step:
        step = get_step(args.step)
        if step is None:
            sys.exit(f"Unknown step: {args.step}")
    else:
        step = _next_pending(state)
        if step is None:
            print("All steps completed.")
            return

    if step.sub_prompts:
        sub = _next_pending_sub_prompt(step, state)
        if sub is None:
            print(f"[khazad-dum] Step {step.index} already complete.")
            return
        prompt = _build_sub_prompt(step, sub, project_root)
        tokens = assert_within_limit(prompt)
        sub_idx = list(step.sub_prompts).index(sub) + 1
        print(f"[khazad-dum] Step {step.index}: {step.name} ({sub_idx}/{len(step.sub_prompts)}): {sub}")
        print(f"[khazad-dum] Prompt size: {tokens} tokens (limit {MAX_TOKENS})")

        if args.dry_run:
            print("---\n" + prompt + "\n---")
            return

        state.current = step.dir_name
        state.save(project_root)

        result = subprocess.run(["claude", "-p", prompt])

        if result.returncode == 0:
            state.mark_sub_completed(step.dir_name, sub)
            if _next_pending_sub_prompt(step, state) is None:
                state.mark_completed(step.dir_name)
                print(f"[khazad-dum] Step {step.index} complete.")
            else:
                remaining = len(step.sub_prompts) - len(state.sub_completed.get(step.dir_name, []))
                print(f"[khazad-dum] Sub-step complete. {remaining} sub-step(s) remaining.")
            state.save(project_root)
        else:
            print(f"[khazad-dum] claude exited with code {result.returncode}. Sub-step not marked complete.")
            sys.exit(result.returncode)
        return

    prompt = _build_prompt(step, project_root)
    tokens = assert_within_limit(prompt)
    print(f"[khazad-dum] Step {step.index}: {step.name}")
    print(f"[khazad-dum] Prompt size: {tokens} tokens (limit {MAX_TOKENS})")

    if args.dry_run:
        print("---\n" + prompt + "\n---")
        return

    state.current = step.dir_name
    state.save(project_root)

    result = subprocess.run(["claude", "-p", prompt])

    if result.returncode == 0:
        state.mark_completed(step.dir_name)
        state.save(project_root)
        print(f"[khazad-dum] Step {step.index} marked complete.")
    else:
        print(f"[khazad-dum] claude exited with code {result.returncode}. Step not marked complete.")
        sys.exit(result.returncode)


def cmd_tokens(args: argparse.Namespace) -> None:
    text = Path(args.file).read_text() if args.file else sys.stdin.read()
    print(count_tokens(text))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="khazad-dum", description="Walk a project through Research → Delivery using claude.")
    sub = p.add_subparsers(dest="command")

    p_init = sub.add_parser("init", help="Create documentation/ scaffold in the current directory.")
    p_init.add_argument("--force", action="store_true", help="Proceed even if documentation/ exists.")
    p_init.set_defaults(func=cmd_init)

    p_status = sub.add_parser("status", help="Show step progress.")
    p_status.set_defaults(func=cmd_status)

    p_run = sub.add_parser("run", help="Invoke claude on a step (default: next pending).")
    p_run.add_argument("step", nargs="?", help="Step slug or number (e.g. research, 1).")
    p_run.add_argument("--dry-run", action="store_true", help="Print prompt without invoking claude.")
    p_run.set_defaults(func=cmd_run)

    p_tokens = sub.add_parser("tokens", help="Count tokens in a file or stdin.")
    p_tokens.add_argument("file", nargs="?", help="Path to a file. If omitted, reads stdin.")
    p_tokens.set_defaults(func=cmd_tokens)

    return p


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.command:
        cmd_status(args)
        return
    args.func(args)


if __name__ == "__main__":
    main()
