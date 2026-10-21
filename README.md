# Fiduciary Cyber Program

A local checklist for a fiduciary firm's cybersecurity program.

It covers the same kind of work a firm has to show for a program: a written policy, safeguards for client information, vendor oversight, an incident response plan, training, and a dated risk assessment. You answer yes, no, or partial. It prints a score, lists the gaps, and saves `cyber-program-report.txt`.

It does not install anything on computers, collect client files, or update itself when rules change. It is not legal advice and it does not replace policies written for your firm.

## How to run

```
python fiduciary_cyber.py
```

## Example

```
Overall: 87% (13/15)

Governance: 100%
Safeguards: 75%
Vendors: 100%
Response: 67%
People and evidence: 100%

Gaps:
  - Backups of client information were tested in the last 12 months
  - The plan says how affected clients will be notified after unauthorized access
```

Built with Grok Build.
