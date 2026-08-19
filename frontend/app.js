/* Signal Desk: behavior stays local, marks each state explicitly, and turns deterministic findings into concise evidence strips. */
const state = { configured: false, report: null, stages: ["Checking TLS transport…", "Inspecting HTTP response headers…", "Probing a fixed list of common ports…", "Checking bounded public web exposures…"] };

const elements = {
  authPanel: document.querySelector("#auth-panel"), scannerShell: document.querySelector("#scanner-shell"), authForm: document.querySelector("#auth-form"), authMode: document.querySelector("#auth-mode-label"), authTitle: document.querySelector("#auth-form-title"), authSubmit: document.querySelector("#auth-submit"), password: document.querySelector("#password"), passwordHint: document.querySelector("#password-hint"), authError: document.querySelector("#auth-error"), sessionName: document.querySelector("#session-name"), logout: document.querySelector("#logout-button"), scanForm: document.querySelector("#scan-form"), target: document.querySelector("#target"), scanButton: document.querySelector("#scan-button"), scanError: document.querySelector("#scan-error"), scanning: document.querySelector("#scanning-state"), scanStage: document.querySelector("#scan-stage"), results: document.querySelector("#results-shell"), reportTarget: document.querySelector("#report-target"), reportTime: document.querySelector("#report-time"), grade: document.querySelector("#grade-letter"), score: document.querySelector("#score-value"), scoreDescription: document.querySelector("#score-description"), posture: document.querySelector("#posture-message"), summary: document.querySelector("#summary-ribbon"), count: document.querySelector("#finding-count"), findingList: document.querySelector("#finding-list"), findingTemplate: document.querySelector("#finding-template"), jsonExport: document.querySelector("#export-json"), htmlExport: document.querySelector("#export-html"), pdfExport: document.querySelector("#export-pdf"), themeToggle: document.querySelector("#theme-toggle"), themeLabel: document.querySelector("#theme-label")
};

async function request(path, options = {}) {
  const response = await fetch(path, { headers: { "Content-Type": "application/json", ...(options.headers || {}) }, ...options });
  const contentType = response.headers.get("content-type") || "";
  const body = contentType.includes("application/json") ? await response.json() : null;
  if (!response.ok) throw new Error(body?.error || "The local server could not complete that request.");
  return body;
}

function setError(node, message) { node.textContent = message; node.hidden = !message; }

function setTheme(theme) {
  const dark = theme === "dark";
  document.documentElement.dataset.theme = theme;
  elements.themeToggle.setAttribute("aria-pressed", String(dark));
  elements.themeLabel.textContent = dark ? "Night mode" : "Paper mode";
  localStorage.setItem("sitesentry-theme", theme);
}

const savedTheme = localStorage.getItem("sitesentry-theme");
setTheme(savedTheme || (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light"));
elements.themeToggle.addEventListener("click", () => setTheme(document.documentElement.dataset.theme === "dark" ? "light" : "dark"));

async function refreshSession() {
  const status = await request("/api/auth/status");
  state.configured = status.configured;
  elements.sessionName.textContent = status.authenticated ? status.username : "Not signed in";
  elements.logout.hidden = !status.authenticated;
  elements.authPanel.hidden = status.authenticated;
  elements.scannerShell.hidden = !status.authenticated;
  if (!status.authenticated) {
    const loginMode = status.configured;
    elements.authMode.textContent = loginMode ? "Local sign in" : "Set up local access";
    elements.authTitle.textContent = loginMode ? "Open your inspection desk" : "Create your local credential";
    elements.authSubmit.innerHTML = `${loginMode ? "Sign in" : "Create local credential"} <span aria-hidden="true">→</span>`;
    elements.password.autocomplete = loginMode ? "current-password" : "new-password";
    elements.passwordHint.textContent = loginMode ? "This is checked only against the password hash stored on this device." : "Use at least 12 characters. This password stays on this device.";
  }
}

elements.authForm.addEventListener("submit", async (event) => {
  event.preventDefault(); setError(elements.authError, "");
  const username = document.querySelector("#username").value.trim();
  const password = elements.password.value;
  if (!username || !password) return setError(elements.authError, "Enter both a username and password.");
  elements.authSubmit.disabled = true;
  try {
    await request(state.configured ? "/api/auth/login" : "/api/auth/setup", { method: "POST", body: JSON.stringify({ username, password }) });
    elements.authForm.reset(); await refreshSession(); elements.target.focus();
  } catch (error) { setError(elements.authError, error.message); } finally { elements.authSubmit.disabled = false; }
});

elements.logout.addEventListener("click", async () => { await request("/api/auth/logout", { method: "POST" }); elements.results.hidden = true; await refreshSession(); });

function startStageCycle() {
  let index = 0; elements.scanStage.textContent = state.stages[index];
  return window.setInterval(() => { index = (index + 1) % state.stages.length; elements.scanStage.textContent = state.stages[index]; }, 1300);
}

elements.scanForm.addEventListener("submit", async (event) => {
  event.preventDefault(); setError(elements.scanError, "");
  const target = elements.target.value.trim();
  const authorized = document.querySelector("#authorized").checked;
  if (!target) return setError(elements.scanError, "Enter a website domain or URL.");
  if (!authorized) return setError(elements.scanError, "Confirm that you are authorized to inspect this target.");
  elements.scanButton.disabled = true; elements.scanButton.textContent = "Scanning…"; elements.scanning.hidden = false; elements.results.hidden = true;
  const timer = startStageCycle();
  try { state.report = await request("/api/scan", { method: "POST", body: JSON.stringify({ target, authorized }) }); renderReport(state.report); } catch (error) { setError(elements.scanError, error.message); } finally { window.clearInterval(timer); elements.scanning.hidden = true; elements.scanButton.disabled = false; elements.scanButton.innerHTML = "Run scan <span aria-hidden='true'>→</span>"; }
});

function describeScore(score) {
  if (score >= 90) return "Strong baseline, with any findings documented below.";
  if (score >= 70) return "Useful protections are present; review the open findings.";
  if (score >= 40) return "Material gaps need deliberate remediation.";
  return "Prioritize critical and high-severity exposures before routine work.";
}

function postureMessage(report) {
  const { grade, open_findings: open } = report.score;
  return `Grade ${grade} reflects ${open} open ${open === 1 ? "finding" : "findings"} under SiteSentry’s fixed weighted rubric.`;
}

function renderReport(report) {
  const { score, grade, summary } = report.score;
  elements.reportTarget.textContent = report.target;
  elements.reportTime.textContent = `Scanned ${new Date(report.scanned_at).toLocaleString()}`;
  elements.grade.textContent = grade; elements.score.textContent = score; elements.scoreDescription.textContent = describeScore(score); elements.posture.textContent = postureMessage(report);
  elements.summary.innerHTML = "";
  ["critical", "high", "medium", "low", "info"].forEach((severity) => { const count = summary[severity] || 0; const token = document.createElement("span"); token.className = `summary-token ${severity}`; token.textContent = `${count} ${severity}`; elements.summary.append(token); });
  const openFindings = report.findings.filter((finding) => finding.status !== "pass");
  const ordered = [...openFindings, ...report.findings.filter((finding) => finding.status === "pass")];
  elements.count.textContent = `${openFindings.length} needs attention · ${report.score.passed_checks} baseline checks passed`;
  elements.findingList.innerHTML = "";
  ordered.forEach((finding) => { const node = elements.findingTemplate.content.cloneNode(true); const article = node.querySelector("article"); article.classList.add(finding.severity); article.querySelector(".finding-meta").textContent = `${finding.status === "pass" ? "Pass" : capitalize(finding.severity)} · ${finding.check}`; article.querySelector("h3").textContent = finding.title; article.querySelector(".finding-summary").textContent = finding.summary; article.querySelector(".finding-remediation").textContent = finding.remediation; elements.findingList.append(node); });
  [elements.jsonExport, elements.htmlExport, elements.pdfExport].forEach((node) => { const format = node.textContent.toLowerCase(); node.href = `/api/reports/${report.id}?format=${format}`; });
  elements.results.hidden = false; elements.results.scrollIntoView({ behavior: "smooth", block: "start" });
}

function capitalize(value) { return value.charAt(0).toUpperCase() + value.slice(1); }
refreshSession().catch((error) => setError(elements.authError, `Could not reach the local server: ${error.message}`));
