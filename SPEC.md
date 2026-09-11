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

For authorized security testing only. The tool reads public pages, it does not attempt
logins or bypass access controls.

## Open questions

- Which sites to cover first, and where the list lives (JSON, YAML, Python).
- How to tell "profile does not exist" from "page blocked us", per site.
- Whether results get exported, and in what format.
- Rate limiting and whether requests go through a proxy.
- What a tool declares to the registry, and where the registry file lives.
