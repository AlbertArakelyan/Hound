# Security

## What Hound is

Hound is a penetration testing toolkit. It is dual-use by nature: the same features that
help someone audit their own exposure can be pointed at a target without permission.

It reads publicly served pages. It does not attempt logins, defeat authentication, or
exploit anything. It sends ordinary HTTP GET requests, the same ones a browser sends,
and reads what comes back.

## Reporting a vulnerability in Hound

Use GitHub's private vulnerability reporting on this repository: the Security tab, then
"Report a vulnerability". That keeps the report private until there is a fix.

For anything not sensitive, a normal issue is fine.

## Reporting abuse

If someone is using Hound against you or your systems without permission, open a report
through the same private channel above. Include the behaviour you saw. Note that Hound
runs entirely on the user's own machine, so there is no service to suspend and no logs
to hand over. What can be done is fixing the tool if a feature makes abuse easier than
it needs to be.

## Intended use

For authorized security testing, your own infrastructure, and research.

Not for collecting personal data at scale, evading rate limits, unsolicited outreach, or
testing systems you have no permission to test.

Email addresses collected with this tool are personal data in most jurisdictions.
Collecting an address is not permission to use it.
