#!/usr/bin/env python3
"""
auto_tag.py — Git pre-commit hook helper
Automatically generates tags and categories for staged Hugo blog posts using Claude API.

Usage (standalone):  python scripts/auto_tag.py [file1.md file2.md ...]
Usage (as hook):     called automatically by .git/hooks/pre-commit

Requirements:
    pip install anthropic python-frontmatter
"""

import os
import re
import sys
import subprocess
import json
import frontmatter  # python-frontmatter

import anthropic

# ── Configuration ──────────────────────────────────────────────────────────────

MODEL = "claude-haiku-4-5"   # fast & cheap; switch to claude-opus-4-7 for quality

SYSTEM_PROMPT = """\
You are a professional blog taxonomy assistant. Given a blog post, you will return
ONLY a JSON object with two keys:
  "tags"       — a list of 3-6 specific, descriptive tags (lowercase, use hyphens for spaces)
  "categories" — a list of 1-2 broad categories (Title Case)

Rules:
- Match the language of the article. Chinese article → Chinese tags/categories; English → English.
- Tags should be specific (e.g. "机器学习", "python", "git-workflow").
- Categories should be broad (e.g. "技术", "生活", "Technology", "Lifestyle").
- Output ONLY the raw JSON object, no markdown fences, no explanation.
"""

# ── Helpers ────────────────────────────────────────────────────────────────────

def get_staged_post_files() -> list[str]:
    """Return paths of staged content/posts/*.md files."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        capture_output=True, text=True, check=True
    )
    files = [
        f for f in result.stdout.splitlines()
        if re.match(r"content/posts/.+\.md$", f)
    ]
    return files


def needs_tagging(post: frontmatter.Post) -> bool:
    """Return True if tags or categories are empty (None, [], or [''])."""
    def empty(val):
        if val is None:
            return True
        if isinstance(val, list):
            return len(val) == 0 or val == [""]
        return str(val).strip() == ""

    return empty(post.get("tags")) or empty(post.get("categories"))


def call_claude(client: anthropic.Anthropic, content: str) -> dict:
    """Call Claude to get tags and categories for the given content."""
    # Truncate very long posts to ~3000 chars to keep costs down
    excerpt = content[:3000] + ("\n...[truncated]" if len(content) > 3000 else "")

    message = client.messages.create(
        model=MODEL,
        max_tokens=256,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                # Cache the stable system prompt across hook invocations
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[
            {
                "role": "user",
                "content": f"Please generate tags and categories for this blog post:\n\n{excerpt}",
            }
        ],
    )

    raw = message.content[0].text.strip()

    # Strip accidental markdown fences
    raw = re.sub(r"^```[a-z]*\n?", "", raw)
    raw = re.sub(r"\n?```$", "", raw)

    return json.loads(raw)


def update_file(filepath: str, client: anthropic.Anthropic) -> bool:
    """
    Read the file, call Claude if needed, write back updated front matter.
    Returns True if the file was modified.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        post = frontmatter.load(f)

    if not needs_tagging(post):
        return False

    print(f"  → auto-tagging: {filepath}")

    try:
        result = call_claude(client, post.content)
    except (json.JSONDecodeError, anthropic.APIError) as e:
        print(f"  ✗ Claude API error for {filepath}: {e}", file=sys.stderr)
        return False

    tags = result.get("tags", [])
    categories = result.get("categories", [])

    # Only overwrite the keys that are actually empty
    if empty_field(post.get("tags")):
        post["tags"] = tags
    if empty_field(post.get("categories")):
        post["categories"] = categories

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(frontmatter.dumps(post))

    print(f"     tags={tags}")
    print(f"     categories={categories}")
    return True


def empty_field(val) -> bool:
    if val is None:
        return True
    if isinstance(val, list):
        return len(val) == 0 or val == [""]
    return str(val).strip() == ""


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print(
            "auto_tag.py: ANTHROPIC_API_KEY not set — skipping auto-tagging.",
            file=sys.stderr,
        )
        sys.exit(0)   # Don't block the commit

    client = anthropic.Anthropic(api_key=api_key)

    # Accept explicit file list (for standalone usage) or detect from git
    if len(sys.argv) > 1:
        files = sys.argv[1:]
    else:
        try:
            files = get_staged_post_files()
        except subprocess.CalledProcessError as e:
            print(f"auto_tag.py: git error: {e}", file=sys.stderr)
            sys.exit(0)

    if not files:
        sys.exit(0)

    modified = []
    for filepath in files:
        if not os.path.isfile(filepath):
            continue
        if update_file(filepath, client):
            modified.append(filepath)

    # Re-stage any files we modified so the commit includes our changes
    if modified:
        subprocess.run(["git", "add", "--"] + modified, check=True)
        print(f"auto_tag.py: re-staged {len(modified)} file(s) with generated tags.")

    sys.exit(0)   # Never block the commit


if __name__ == "__main__":
    main()
