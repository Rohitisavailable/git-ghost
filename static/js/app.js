const $ = (id) => document.getElementById(id);
let activeRepo = "";

function toast(message) {
  const el = $("toast");
  el.textContent = message;
  el.classList.add("show");
  setTimeout(() => el.classList.remove("show"), 3500);
}
function terminalLine(message, type = "SYSTEM") {
  const p = document.createElement("p");
  const em = document.createElement("em");
  em.textContent = `[${type}] `;
  p.append(em, document.createTextNode(message));
  $("terminalLines").appendChild(p);
  $("terminalLines").scrollTop = $("terminalLines").scrollHeight;
}
function safeText(value) { return String(value ?? ""); }
function formatDate(value) {
  if (!value) return "Date unknown";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString();
}
async function postJSON(url, body) {
  const response = await fetch(url, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(body)
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "The entity could not complete the request.");
  return data;
}
async function summon() {
  const path = $("repoPath").value.trim();
  if (!path) return toast("Enter a repository path first.");
  $("summonBtn").disabled = true;
  $("summonBtn").textContent = "SUMMONING...";
  $("terminalLines").innerHTML = "";
  $("dashboard").classList.add("hidden");
  terminalLine("Opening a channel to the repository...");
  try {
    const data = await postJSON("/api/scan", {repo_path: path});
    activeRepo = data.repo_path;
    terminalLine(`Found ${data.commit_count} commits and ${data.file_count} tracked files.`);
    terminalLine(`${data.deleted_count} deletion event(s) detected.`);
    terminalLine("The entity has awakened.", "GHOST");
    renderDashboard(data);
    $("dashboard").classList.remove("hidden");
    $("intro").querySelector(".terminal").scrollIntoView({behavior:"smooth", block:"nearest"});
    if (data.truncated) toast("Showing the latest scan window. Increase GHOST_MAX_COMMITS to inspect more history.");
  } catch (error) {
    terminalLine(error.message, "ERROR");
    toast(error.message);
  } finally {
    $("summonBtn").disabled = false;
    $("summonBtn").innerHTML = "<span>☠</span> SUMMON";
  }
}
function renderDashboard(data) {
  $("repoName").textContent = data.repo_name;
  $("repoMeta").textContent = `${data.repo_path}  ·  ${data.branch}`;
  $("commitCount").textContent = data.commit_count;
  $("deletedCount").textContent = data.deleted_count;
  $("fileCount").textContent = data.file_count;
  $("branchName").textContent = data.branch;
  $("branchCount").textContent = `${data.branches.length} branch(es) discovered`;
  const graveyard = $("graveyard");
  graveyard.innerHTML = "";
  if (!data.deleted_files.length) graveyard.innerHTML = '<div class="empty">No tombstones in the scanned history. The graveyard is silent.</div>';
  data.deleted_files.forEach(item => {
    const div = document.createElement("div");
    div.className = "grave-item";
    const strong = document.createElement("strong");
    strong.textContent = "✝ " + item.path;
    const p = document.createElement("p");
    p.textContent = item.message;
    const small = document.createElement("small");
    small.textContent = `${item.commit} · ${formatDate(item.date)}`;
    div.append(strong, p, small);
    graveyard.append(div);
  });
  const timeline = $("timeline");
  timeline.innerHTML = "";
  if (!data.commits.length) timeline.innerHTML = '<div class="empty">No commits found in this repository.</div>';
  data.commits.forEach(item => {
    const div = document.createElement("div");
    div.className = "commit-item";
    const strong = document.createElement("strong");
    strong.textContent = item.hash;
    const p = document.createElement("p");
    p.textContent = item.message;
    const small = document.createElement("small");
    small.textContent = `${item.author} · ${formatDate(item.date)} · +${item.insertions}/-${item.deletions}`;
    div.append(strong, p, small);
    timeline.append(div);
  });
}
function addBubble(kind, title, text) {
  const div = document.createElement("div");
  div.className = `bubble ${kind}-bubble`;
  const b = document.createElement("b"); b.textContent = title;
  const p = document.createElement("p"); p.textContent = text;
  div.append(b, p);
  $("chatLog").append(div);
  $("chatLog").scrollTop = $("chatLog").scrollHeight;
}
async function askGhost(event) {
  event.preventDefault();
  const question = $("question").value.trim();
  if (!question || !activeRepo) return;
  $("question").value = "";
  addBubble("user", "YOU", question);
  addBubble("ghost", "GIT GHOST", "The spirit is searching its memories...");
  const pending = $("chatLog").lastElementChild;
  try {
    const data = await postJSON("/api/ask", {repo_path: activeRepo, question});
    pending.querySelector("p").textContent = data.answer.text + (data.answer.used_ai ? `\n\n[${data.answer.model} · LOCAL AI]` : "\n\n[OFFLINE FALLBACK]");
  } catch (error) {
    pending.querySelector("p").textContent = error.message;
  }
  $("chatLog").scrollTop = $("chatLog").scrollHeight;
}
$("summonBtn").addEventListener("click", summon);
$("repoPath").addEventListener("keydown", e => { if (e.key === "Enter") summon(); });
$("newScan").addEventListener("click", summon);
$("chatForm").addEventListener("submit", askGhost);
