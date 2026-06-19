# Global Rules — GitNexus + CGC Combo

## Behavioral Standards
- Execute the task. No preamble, no recap of what was asked.
- If a task requires multiple steps, do them all. Summarize what was done at the end.
- State assumptions explicitly when requirements are ambiguous. Then proceed.
- NEVER end responses with questions or offers for further assistance.

## Git Discipline
- NEVER commit changes unless the user explicitly asks you to.
- NEVER run destructive/irreversible git commands unless explicitly requested.
- NEVER skip hooks unless explicitly requested.

## File Operations
- Use `edit` for modifications. Use `replaceAll` when renaming across a file.
- `pathlib.Path` over `os.path`.
- f-strings over `.format()` or `%`.

## Code Intelligence Protocol (CRITICAL)
- **Before editing any symbol:** run impact analysis via GitNexus `impact` or CGC `analyze_code_relationships`.
- **Before committing:** run `gitnexus_detect_changes` to verify affected scope.
- **For code exploration:** use `gitnexus_query` or `cgc find` instead of grep.
- **Keep indexes fresh:** `npx gitnexus status` + `cgc stats` at session start.
