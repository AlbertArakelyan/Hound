# SPEC

## What Hound is

A penetration testing tool with a desktop GUI. It will hold many functionalities over
time, each one a separate module.

## Screens and navigation

Two levels.

1. Home screen. Renders the available tools as a grid of cards. Each card shows the tool
   name and a short description. Clicking a card opens that tool.
2. Tool page. One page per tool, holding that tool's own inputs, controls, and results.
   It can navigate back to the home screen.

New tools appear on the home screen by registering themselves, not by editing the home
screen.

## First feature: social account discovery

Given a username, find social media accounts that use it.

Input: one username.
Output: a list of sites, each with a status (found, not found, unknown) and a profile URL
when found.

## Requirements

- Check many sites per run, concurrently. One slow or dead site must not block the rest.
- Report per-site status honestly. A site that times out or blocks the request is
  "unknown", not "not found".
- Show results in the GUI as they arrive, do not wait for every site to finish.
- The site list is data, not code, so sites can be added without touching the engine.

## Planned tools

The social account search is the first of many. Others on the list are theHarvester
(emails, subdomains, and hosts from public sources) and hunter.io (email lookup by
domain), with more to follow.

These bring shapes the first tool does not have:

- Wrappers around an external binary. The tool has to cope with the binary missing and
  read its output as it runs.
- Clients for a third party API that needs a key. Keys stay out of the repo and are
  entered in the app.

Both still follow the structure rules below: own directory, Qt free logic, one registry
entry. A tool that cannot run yet, because a binary or key is missing, says so on its
page instead of failing silently.

## Structure

The file layout must match the two level design above. Each tool is self contained, so
adding or removing one touches only its own directory plus the registry entry.

- One directory per tool. It holds that tool's logic and its page.
- Inside a tool, logic and UI stay in separate files. Logic is plain Python with no Qt
  imports, so it can be tested without a display.
- Shared UI pieces (the card widget, page shell, navigation) live in one common UI place,
  not copied into each tool.
- A registry lists the tools. The home screen builds its cards from the registry, so it
  never imports tools one by one.
- `main.py` only starts the app and mounts the home screen.

## Scope and use

For authorized security testing only. The tool reads publicly served pages. It does not
attempt logins, and it does not defeat authentication or any other access control.

Decoding an email obfuscation scheme is reading something the site already serves to
every visitor, not crossing a security boundary. Describe it that way. A tool that
overstates what it does invites people to use it as if the overstatement were true.

Respecting the target's terms, its rate limits, and the privacy law covering whatever is
collected is the user's responsibility, and the app should not make that harder.

Hound is dual-use, so it says so plainly. `README.md` carries the disclaimer and
`SECURITY.md` the contact channel, which is what GitHub's acceptable use policy asks of
a project like this. Keep both current as tools are added.

Not for collecting personal data at scale, evading rate limits, or unsolicited outreach.
A feature that only makes sense for one of those does not belong here.

## Open questions

- Which sites to cover first, and where the list lives (JSON, YAML, Python).
- How to tell "profile does not exist" from "page blocked us", per site.
- Whether results get exported, and in what format.
- Rate limiting and whether requests go through a proxy.
- What a tool declares to the registry, and where the registry file lives.
- Where API keys live, and how a tool reports that it is missing a key or a binary.
