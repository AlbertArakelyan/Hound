---
name: commit
description: Write a git commit for this project using its message convention, type(branch number). Use whenever the user asks to commit, or asks how a commit message should read here.
---

# Commit

First rule, from `CLAUDE.md`: never commit unless the user asked for it explicitly.

## Format

```
<type>(<branch number>): <what you did>
```

The scope is the number the branch name starts with. On
`1-create-email-scrapper-tool` the scope is `1`.

```bash
git branch --show-current | grep -oE '^[0-9]+'
```

If the branch has no leading number, on `master` for example, drop the scope and write
`type: what you did`. Do not invent a number.

## Types

| type | for |
|---|---|
| `feat` | new behavior a user can see |
| `fix` | a bug fix |
| `docs` | README, SPEC, CLAUDE.md, comments only |
| `chore` | dependencies, gitignore, config, tooling |
| `refactor` | code moves or restructures, behavior unchanged |
| `test` | tests only |
| `style` | formatting only, no logic change |

Pick by what the change does, not by which file it touches. Adding a site to
`sites.py` is `feat`. Fixing a site that reported the wrong status is `fix`.

## Subject

- Say what you did, in plain words, no period at the end.
- Imperative: "add the Email Scraper tool", not "added" or "adds".
- Keep it under about 70 characters, and never stretch past 80.
- No file lists. That is what the diff is for.

## Body

Include one when the change needs explaining, which is most of the time. Say what
changed and why. Mention anything that surprised you, anything deliberately left out,
and any deviation from a reference or a spec.

Skip the body for a change that is fully described by its subject, such as a typo fix.

Follow the writing style in `CLAUDE.md`: short, plain words, no em dashes.

## Attribution

End the message with the attribution lines the session provides. They go last, after
the body, separated by a blank line.

## Examples

```
feat(1): add Email Scraper tool
fix(4): decode Cloudflare obfuscated addresses
docs(7): document the tool registry contract
chore(2): pin beautifulsoup4 and lxml
refactor(9): move link resolution out of the crawl loop
```

## Before committing

- `git status --short` to see what is actually pending.
- `git add -A`, unless the user asked for part of the change.
- Say the short hash and the file count afterwards, then whether the tree is clean.
