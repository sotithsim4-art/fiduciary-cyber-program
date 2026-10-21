SECTIONS = (
    {
        "title": "Governance",
        "questions": (
            ("owner", "A named person owns the cybersecurity program"),
            ("policy", "The firm has a written information security policy"),
            ("review", "That policy was reviewed in the last 12 months"),
        ),
    },
    {
        "title": "Safeguards",
        "questions": (
            ("mfa", "Email and systems that hold client information require MFA"),
            ("encryption", "Client information is encrypted where it is stored and while it is sent"),
            ("backups", "Backups of client information were tested in the last 12 months"),
            ("admins", "Administrator access is limited to named people"),
        ),
    },
    {
        "title": "Vendors",
        "questions": (
            ("vendor_list", "The firm keeps a list of vendors that hold client information"),
            ("vendor_review", "Those vendors are reviewed against the firm's security expectations"),
        ),
    },
    {
        "title": "Response",
        "questions": (
            ("incident_plan", "The firm has a written incident response plan"),
            ("notification", "The plan says how affected clients will be notified after unauthorized access"),
            ("incident_owner", "A named person is responsible for running the plan"),
        ),
    },
    {
        "title": "People and evidence",
        "questions": (
            ("training", "Staff completed cybersecurity training in the last 12 months"),
            ("attestation", "Staff attested that they read the security policy"),
            ("risk_assessment", "A written risk assessment was completed in the last 12 months"),
        ),
    },
)

DISCLAIMER = (
    "This is a starting record for a fiduciary firm. It is not legal advice, "
    "an examination, or a substitute for policies written for the firm."
)


def points_for(answer):
    value = str(answer).strip().casefold() if answer is not None else ""
    if value in ("y", "yes"):
        return 1
    if value in ("p", "partial"):
        return 0.5
    return 0


def assess(answers):
    if not isinstance(answers, dict):
        answers = {}
    sections = []
    gaps = []
    partials = []
    earned = 0
    possible = 0
    for section in SECTIONS:
        section_earned = 0
        for key, prompt in section["questions"]:
            score = points_for(answers.get(key))
            section_earned += score
            possible += 1
            if score == 0:
                gaps.append(prompt)
            elif score == 0.5:
                partials.append(prompt)
        earned += section_earned
        count = len(section["questions"])
        sections.append({
            "title": section["title"],
            "earned": section_earned,
            "possible": count,
            "percent": round(100 * section_earned / count),
        })
    percent = round(100 * earned / possible) if possible else 0
    return {
        "earned": earned,
        "possible": possible,
        "percent": percent,
        "sections": sections,
        "gaps": gaps,
        "partials": partials,
    }


def format_report(result):
    lines = [
        "Fiduciary Cyber Program",
        "-----------------------",
        f"Overall: {result['percent']}% ({result['earned']:g}/{result['possible']})",
        "",
    ]
    for section in result["sections"]:
        lines.append(f"{section['title']}: {section['percent']}%")
    if result["partials"]:
        lines.append("")
        lines.append("Partial:")
        lines.extend(f"  - {item}" for item in result["partials"])
    lines.append("")
    if result["gaps"]:
        lines.append("Gaps:")
        lines.extend(f"  - {item}" for item in result["gaps"])
    else:
        lines.append("No open gaps in this checklist.")
    lines.extend(["", DISCLAIMER])
    return "\n".join(lines)


def read_answer(prompt):
    try:
        return input(f"{prompt}? [y/n/partial] ").strip()
    except EOFError:
        return None


def ask():
    answers = {}
    print("Fiduciary Cyber Program")
    print("Answer y, n, or partial.\n")
    for section in SECTIONS:
        print(section["title"])
        for key, prompt in section["questions"]:
            reply = read_answer(prompt)
            if reply is None:
                return None
            answers[key] = reply
        print()
    return answers


if __name__ == "__main__":
    answers = ask()
    if answers is None:
        print("Enter an answer for each item.")
    else:
        report = format_report(assess(answers))
        print(report)
        with open("cyber-program-report.txt", "w", encoding="utf-8") as handle:
            handle.write(report + "\n")
        print("\nSaved cyber-program-report.txt")
