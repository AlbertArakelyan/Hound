# Beautify the tool pages

## Context

The home screen and its cards were restyled. The tool pages were not, so they still look
like raw Qt widgets while the screen that leads to them looks designed. This plan brings
the two pages up to the same standard and puts the shared styling in one place, so the
third tool inherits it instead of reinventing it.

Written after rendering both pages offscreen in a dark palette. The items below are
things visible in those screenshots, not guesses.

## What is wrong now

### Both pages

1. **Back button** is a default push button. It reads as a form control, not navigation.
2. **Page title** has no icon, while the card that opens it does. The two screens do not
   look related.
3. **Inputs and buttons** are stock Qt. No rounded corners, no focus accent, nothing
   tying them to the card styling.
4. **Result areas** are bordered boxes with content flush against the edge. No padding,
   no row separation, no empty state before a run.
5. **Colors are ad hoc.** `#9a9a9a`, `#2e9e4f`, `#c98a1b` and the card accent are
   scattered across four files with no shared source.

### Social Account Discovery

6. **Found links are barely readable.** They use Qt's default link blue on a dark
   background. This is a readability bug, not a preference. Fix it first.
7. Rows are cramped at 21px with no separation, so scanning a long list is hard.
8. `[+] [-] [?]` markers carry the meaning but are plain text in a fixed column.
9. The status line is one small grey sentence. Counts deserve more weight.
10. The "Found only" checkbox sits alone at the far right, detached from the search row.

### Email Scraper

11. The two panes have headings but no visual containment, so they read as one field.
12. Stop looks identical to Start when disabled, so the page does not show its state.
13. The emails pane, which is the point of the tool, has no count and no way to copy
    everything at once.
14. The splitter handle is nearly invisible.

## Approach

### 1. One source of truth for styling

New `hound/ui/style.py` holding the tokens already in use, plus the few the pages need:

```python
ACCENT = "124, 92, 255"       # already used by the cards
FOUND = "..."                 # today's #2e9e4f
UNKNOWN = "..."               # today's #c98a1b
MUTED = "127, 127, 127"
RADIUS = "8px"
```

Greys stay as alpha over the theme background, the trick the cards use, so both themes
keep working. Add small helpers for the repeated pieces: `panel_style()`,
`input_style()`, `primary_button_style()`, `quiet_button_style()`.

Then replace the hardcoded colors in `tool_card.py`, `result_row.py`,
`social_accounts/page.py` and `email_scraper/page.py` with the tokens. This is a
refactor with no visible change, so do it first and confirm the pages still render the
same before restyling anything.

### 2. Shared widgets

`hound/ui/widgets/`:

- **`tool_page.py`**: accept an optional icon, `ToolPage(title, icon="")`, and render it
  before the title so the page matches the card. Restyle Back as a quiet button reading
  `← Back`. Each page passes its own emoji constant, the same one as its `ToolSpec`.
- **`panel.py`** (new): a titled container with a heading, a rounded border, padding and
  a scroll area, returning the layout that rows go into. Both pages build their result
  areas from it. This removes the near duplicate `_build_results_area` and `_build_pane`
  that exist today.

### 3. Social Account Discovery page

- Style found links with the accent color and no underline until hover. Fixes item 6.
- Give each row 6px vertical padding and a hairline separator.
- Turn the marker into a small rounded badge coloured by status.
- Make the status line a row of counts, found, not found, unknown, with the found count
  in the accent color.
- Move "Found only" next to the Search button.
- Show "Results will appear here" in the empty panel before the first search.

### 4. Email Scraper page

- Build both panes from `panel.py`, with the email count in the pane heading.
- Add a "Copy all" quiet button to the emails pane heading, disabled while empty.
- Style Start as the primary button and Stop as quiet, so the disabled state is obvious.
- Give the splitter handle a visible hairline.
- Empty states in both panes.

## Out of scope

- No change to any engine, worker or model. This is presentation only.
- No new dependency. Qt stylesheets are enough.
- No custom theme switcher. The app keeps following the system palette.

## Files

| file | change |
|---|---|
| `hound/ui/style.py` | new, the tokens and helpers |
| `hound/ui/widgets/panel.py` | new, the titled result panel |
| `hound/ui/widgets/tool_page.py` | icon, styled back button |
| `hound/ui/widgets/tool_card.py` | use the shared tokens |
| `hound/tools/social_accounts/result_row.py` | badge, link color, padding |
| `hound/tools/social_accounts/page.py` | panel, counts, control row |
| `hound/tools/email_scraper/page.py` | panels, copy all, button roles |
| `hound/ui/CLAUDE.md` | note that colors come from `style.py` |

## Verification

Render both pages offscreen in a light and a dark palette and look at the images, the
same way this plan was written. Checks that must pass:

- Link text in the social results is legible against a dark background. This is the one
  item with a right answer rather than a taste answer.
- Both pages render correctly under a light palette and a dark one.
- A tool page with no icon still renders, since the icon is optional.
- Clicking a card still opens its page, and Back still returns home.
- `architecture-guard` grep stays clean. No engine file gains a Qt import.

**Screenshot gotcha:** `grab()` after a single `processEvents()` catches the layout
before it activates, and result rows come out invisible. Call `processEvents()` a few
times before grabbing, or the screenshot shows an empty panel and looks like a bug that
is not there. Worth adding to the `run-app` skill.
