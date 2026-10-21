const questionsRoot = document.getElementById("questions");
const scoreRoot = document.getElementById("score");
const disclaimer = document.getElementById("disclaimer");

let catalog = [];
let answers = {};
let requestId = 0;

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text != null) node.textContent = text;
  return node;
}

function allQuestions() {
  return catalog.flatMap((section) => section.questions);
}

function renderQuestions() {
  questionsRoot.replaceChildren();
  catalog.forEach((section) => {
    const block = el("section", "section");
    block.append(el("h2", "section-title", section.title));
    section.questions.forEach((question) => {
      const card = el("fieldset", "question");
      card.append(el("legend", "prompt", question.prompt));
      const choices = el("div", "choices");
      [
        ["yes", "Yes"],
        ["partial", "Partial"],
        ["no", "No"],
      ].forEach(([value, label]) => {
        const choice = el("label", `choice ${value}`);
        const input = document.createElement("input");
        input.type = "radio";
        input.name = question.key;
        input.value = value;
        input.setAttribute("aria-label", `${question.prompt}: ${label}`);
        input.addEventListener("change", () => {
          answers[question.key] = value;
          refresh();
        });
        choice.append(input, document.createTextNode(label));
        choices.append(choice);
      });
      card.append(choices);
      block.append(card);
    });
    questionsRoot.append(block);
  });
}

function listBlock(title, className, items) {
  if (!items.length) return null;
  const wrap = el("div");
  wrap.append(el("p", `list-title ${className}`, title));
  const list = el("ul");
  items.forEach((item) => list.append(el("li", "", item)));
  wrap.append(list);
  return wrap;
}

function renderScore(result, report) {
  const questions = allQuestions();
  const byPrompt = new Map(questions.map((question) => [question.prompt, answers[question.key]]));
  const answered = questions.filter((question) => answers[question.key]).length;
  const complete = questions.length > 0 && answered === questions.length;
  const gaps = result.gaps.filter((prompt) => byPrompt.get(prompt) === "no");
  const untouched = result.gaps.filter((prompt) => !byPrompt.get(prompt));

  scoreRoot.replaceChildren();
  scoreRoot.append(el("p", "score-label", complete ? "Overall" : "Score so far"));
  scoreRoot.append(el("p", "score-number", `${result.percent}%`));
  scoreRoot.append(el("p", "score-detail", `${result.earned} / ${result.possible} · ${answered} of ${questions.length} answered`));

  const bars = el("div", "bars");
  result.sections.forEach((section) => {
    const row = el("div", "bar-row");
    const name = el("div", "bar-name");
    name.append(el("span", "", section.title), el("span", "", `${section.percent}%`));
    const track = el("div", "track");
    const fill = el("div", "fill");
    fill.style.width = `${section.percent}%`;
    track.append(fill);
    row.append(name, track);
    bars.append(row);
  });
  scoreRoot.append(bars);

  if (untouched.length) {
    scoreRoot.append(el("p", "note", "Unanswered items are recorded as gaps when you save."));
  }
  const partials = listBlock("Partial", "partial", result.partials);
  const gapList = listBlock("Gaps", "gaps", gaps);
  if (partials) scoreRoot.append(partials);
  if (gapList) scoreRoot.append(gapList);
  if (complete && gaps.length === 0) {
    scoreRoot.append(el("p", "empty", "No open gaps in this checklist."));
  }

  const save = el("button", "save", "Save report");
  save.type = "button";
  save.addEventListener("click", () => saveReport(save));
  scoreRoot.append(save);
  scoreRoot.append(el("p", "status", ""));

  const details = el("details");
  details.append(el("summary", "", "Report preview"));
  details.append(el("pre", "", report));
  scoreRoot.append(details);
}

async function refresh() {
  const id = ++requestId;
  const response = await fetch("/api/assess", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ answers }),
  });
  if (!response.ok) throw new Error("score");
  const data = await response.json();
  if (id !== requestId) return;
  renderScore(data.result, data.report);
}

async function saveReport(button) {
  button.disabled = true;
  const status = scoreRoot.querySelector(".status");
  try {
    const response = await fetch("/api/save", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ answers }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "save");
    status.textContent = `Saved ${data.saved} in this folder.`;
    renderScore(data.result, data.report);
    scoreRoot.querySelector(".status").textContent = `Saved ${data.saved} in this folder.`;
  } catch (error) {
    if (status) status.textContent = "Could not save the report.";
  } finally {
    const current = scoreRoot.querySelector(".save");
    if (current) current.disabled = false;
  }
}

async function load() {
  const response = await fetch("/api/questions");
  if (!response.ok) throw new Error("load");
  const data = await response.json();
  disclaimer.textContent = data.disclaimer;
  catalog = data.sections;
  renderQuestions();
  await refresh();
}

load().catch(() => {
  questionsRoot.textContent = "Double-click Open Fiduciary Cyber Program.bat to open this app.";
});
