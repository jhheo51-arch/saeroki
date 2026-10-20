/* 새록 지원서 화면. 순서는 skills/ledger·analyze·write/SKILL.md와 같고, 점검·검사·제출본은 apply-core.js(= saerok_apply.core)가 냅니다.
   브라우저 모드: 키와 장부·공고·초안은 이 브라우저에만, Claude는 api.anthropic.com을 바로 부릅니다. 제출본은 파일로 내려받습니다.
   내 PC 모드(saerok-apply): 글은 지원 폴더(~/.saerok/apply)에, 제출본은 19번 서류 폴더로 넘기고, Claude 호출은 내 PC 서버가 넘깁니다. */
"use strict";

const A = window.SaerokApply;
const $ = (sel, el = document) => el.querySelector(sel);
const $$ = (sel, el = document) => Array.from(el.querySelectorAll(sel));
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const pad = (n) => String(n).padStart(2, "0");
const today = () => { const d = new Date(); return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`; };
const slug = (name) => name.trim().replace(/[\\/:*?"<>|\s]+/g, "-").replace(/^[-.]+|[-.]+$/g, "").slice(0, 40);

const MODELS = [
  ["claude-sonnet-5-5", "Claude Sonnet 5.5"],
  ["claude-opus-5-5", "Claude Opus 5.5"],
  ["claude-haiku-5-5", "Claude Haiku 5.5"],
];
const PREFS = "saerok-apply:prefs";
const KEY = "saerok-apply:key";
const STORE = "saerok-apply:files";
const LEVEL = { error: "오류", warn: "경고" };
const FIT = { ok: "적정", over: "초과", short: "부족", "no-limit": "제한 없음" };
const BASIS = { with_spaces: "공백 포함", without_spaces: "공백 제외", bytes: "바이트" };

// ---------- 브라우저 저장소(실패해도 화면은 돕니다) ----------
const local = {
  get(k, fallback, where = localStorage) {
    try { const v = where.getItem(k); return v === null ? fallback : JSON.parse(v); } catch (e) { return fallback; }
  },
  set(k, v, where = localStorage) {
    try { where.setItem(k, JSON.stringify(v)); return true; } catch (e) { return false; }
  },
  del(k, where = localStorage) { try { where.removeItem(k); } catch (e) { /* 저장소를 못 쓰면 지울 것도 없습니다 */ } },
};
const model = () => { const m = (local.get(PREFS, {}) || {}).model; return MODELS.some(([id]) => id === m) ? m : MODELS[0][0]; };
const browserKey = () => local.get(KEY, "", sessionStorage) || local.get(KEY, "");

// ---------- 화면 상태 ----------
const state = {
  terms: null,        // data/terms-lite.json
  templates: null,    // data/templates.json
  companies: [],      // 다른 회사 이름 검사용 [{name, from}]
  postingStatus: "확인함",
  postingImage: "",
  draftName: "",      // 불러온 초안 파일 이름. 새 초안이면 ""
  base: "",           // 불러온 판의 글. 확정 문항 보호(previous)에 씁니다.
};
const company = () => $("#f-company").value.trim();

// ---------- 백엔드: 브라우저 모드 / 내 PC 모드 ----------
const API_HEADERS = { "Content-Type": "application/json", "X-Saerok-Apply": "1" };

const B = {
  mode: "browser",
  info: null,

  async init() {
    try {
      const r = await fetch("api/info", { headers: API_HEADERS });
      if (r.ok) {
        const j = await r.json();
        if (j.mode === "local") { this.mode = "local"; this.info = j; }
      }
    } catch (e) { /* 정적 사이트(GitHub Pages)면 api가 없습니다 */ }
  },

  async api(path, body) {
    const r = await fetch(path, { method: body === undefined ? "GET" : "POST", headers: API_HEADERS,
      body: body === undefined ? undefined : JSON.stringify(body) });
    const j = await r.json().catch(() => ({ error: `응답을 읽지 못했습니다(${r.status})` }));
    if (!r.ok) throw new Error(j.error || `요청 실패(${r.status})`);
    return j;
  },

  async send(body) {
    let r;
    if (this.mode === "local") {
      r = await fetch("api/claude", { method: "POST", headers: API_HEADERS, body: JSON.stringify(body) });
    } else {
      const key = browserKey();
      if (!key) throw new Error("Claude API 키를 먼저 넣어 주세요(오른쪽 위 '키·설정').");
      r = await fetch("https://api.anthropic.com/v1/messages", { method: "POST", body: JSON.stringify(body), headers: {
        "content-type": "application/json", "x-api-key": key, "anthropic-version": "2023-06-01",
        "anthropic-dangerous-direct-browser-access": "true" } });
    }
    const j = await r.json().catch(() => null);
    if (!r.ok) {
      const msg = (j && j.error && (j.error.message || j.error)) || `HTTP ${r.status}`;
      throw new Error(r.status === 401 ? `키가 없거나 맞지 않습니다: ${msg}` : `Claude 호출 실패(${r.status}): ${msg}`);
    }
    return (j.content || []).filter((c) => c.type === "text").map((c) => c.text).join("");
  },

  // 브라우저 모드의 파일: {"ledger.md": 글, "style.md": 글, companies: {회사: {"posting.md": 글, ..., "draft-…md": 글}}}
  files() { const f = local.get(STORE, {}) || {}; f.companies = f.companies || {}; return f; },
  keep(files) {
    if (!local.set(STORE, files)) throw new Error("브라우저 저장 공간에 쓰지 못했습니다. 오래된 초안을 내려받은 뒤 지워 주세요.");
  },

  async read(name, co = "") {
    if (this.mode === "local") {
      const q = new URLSearchParams({ name, company: co });
      return (await this.api(`api/file?${q}`)).text;
    }
    const f = this.files();
    return (co ? (f.companies[slug(co)] || {})[name] : f[name]) || "";
  },

  async write(name, text, co = "") {
    if (this.mode === "local") return this.api("api/file", { name, text, company: co });
    const f = this.files();
    if (co) { f.companies[slug(co)] = f.companies[slug(co)] || {}; f.companies[slug(co)][name] = text; } else f[name] = text;
    this.keep(f);
    return { path: "이 브라우저", privacy: A.scan(text) };
  },

  async drafts(co) {
    if (!co) return [];
    if (this.mode === "local") return this.api(`api/drafts?${new URLSearchParams({ company: co })}`);
    return Object.keys(this.files().companies[slug(co)] || {}).filter((n) => n.startsWith("draft-")).sort();
  },

  // 같은 날짜 초안이 있으면 -2, -3…을 붙입니다(store.new_draft_path와 같음). 이전 판은 덮어쓰지 않습니다.
  async newDraft(co, text) {
    if (this.mode === "local") return this.api("api/draft/new", { company: co, text });
    const f = this.files();
    const folder = f.companies[slug(co)] = f.companies[slug(co)] || {};
    let name = `draft-${today()}.md`;
    for (let n = 2; name in folder; n++) name = `draft-${today()}-${n}.md`;
    folder[name] = text;
    this.keep(f);
    return { name, path: "이 브라우저", privacy: A.scan(text) };
  },

  async companies() {
    if (this.mode === "local") return this.api("api/companies");
    const out = [], seen = new Set();
    for (const name of Object.keys(this.files().companies)) if (!seen.has(name.toLowerCase())) { seen.add(name.toLowerCase()); out.push({ name, from: "folder" }); }
    for (const name of (state.terms && state.terms.companies) || []) if (!seen.has(name.toLowerCase())) { seen.add(name.toLowerCase()); out.push({ name, from: "dictionary" }); }
    return out;
  },
};

async function loadJSON(path) {
  const r = await fetch(path);
  if (!r.ok) throw new Error(`${path}를 읽지 못했습니다.`);
  return r.json();
}

// ---------- 공통 화면 도구 ----------
function busy(button, on, label) {
  if (on) { button.dataset.label = button.textContent; button.innerHTML = `<span class="spin"></span> ${esc(label || "처리 중")}`; }
  else button.textContent = button.dataset.label || button.textContent;
  button.disabled = on;
}

function issueList(issues) {
  if (!issues.length) return `<li>문제가 없습니다.</li>`;
  return issues.map((i) => `<li class="${i.level === "error" ? "err" : "warn"}"><span class="lv">[${LEVEL[i.level]}]</span>` +
    `${esc(i.where)} · ${esc(i.message)}${i.text ? `<div class="q">› ${esc(i.text)}</div>` : ""}</li>`).join("");
}

function privacyNote(found) {
  if (!found || !found.length) return "";
  return ` 개인정보 꼴이 보입니다: ${found.map((f) => `${f.line}줄 ${f.kind}(${f.masked})`).join(", ")}. 지워 주세요.`;
}

function selectTab(name) {
  for (const t of $$(".tab")) t.setAttribute("aria-selected", String(t.dataset.tab === name));
  for (const s of $$("main > section")) s.classList.toggle("hidden", s.id !== `tab-${name}`);
  if (name === "check") runCheck();
}

function pickFile(onText) {
  const input = $("#file-pick");
  input.value = "";
  input.onchange = async () => { if (input.files[0]) onText(await input.files[0].text()); };
  input.click();
}

// ---------- ① 장부 ----------
function checkLedger() {
  const text = $("#t-ledger").value;
  const r = A.ledgerReport(text);
  const rows = r.experiences.map((e) => `<tr><td>${esc(e.id)}</td><td>${esc(e.title)}</td><td>${esc(e.period)}</td>` +
    `<td>${esc(e.competencies.join(", "))}</td><td class="num">${e.actions["한 일"]}·${e.actions["설계안(도입 가정)"]}·${e.actions["계획"]}</td>` +
    `<td class="num">${e.metrics}</td><td>${esc(e.unconfirmed.join(", ") || "-")}</td></tr>`).join("");
  const found = A.scan(text + "\n" + $("#t-style").value);
  $("#ledger-result").innerHTML = `<h3>경험 ${r.summary.experiences}개 · 오류 ${r.summary.errors}개 · 확인 전 칸이 있는 경험 ${r.summary.unconfirmed}개</h3>` +
    (found.length ? `<p class="note">${esc(privacyNote(found))}</p>` : "") +
    `<div class="scroll"><table><thead><tr><th>ID</th><th>경험</th><th>기간</th><th>역량</th><th>한 일·설계안·계획</th><th>수치</th><th>확인 전 칸</th></tr></thead>` +
    `<tbody>${rows}</tbody></table></div><ul class="issues">${issueList(r.issues)}</ul>`;
}

async function saveLedger() {
  const msg = $("#ledger-msg");
  try {
    const a = await B.write("ledger.md", $("#t-ledger").value);
    let note = privacyNote(a.privacy);
    if ($("#t-style").value.trim()) note += privacyNote((await B.write("style.md", $("#t-style").value)).privacy);
    msg.textContent = `저장했습니다(${a.path}).${note}`;
    checkLedger();
  } catch (e) { msg.textContent = e.message; }
}

// ---------- ② 공고 ----------
function postingText() {
  const co = company();
  const lines = [`# 공고 · ${co}`, "", `- 회사: ${co}`, `- 출처: ${$("#f-source").value.trim()}`, `- 확인 날짜: ${$("#f-date").value.trim()}`,
    `- 상태: ${state.postingStatus}`];
  if (state.postingImage) lines.push(`- 원본 이미지: ${state.postingImage}`);
  return lines.join("\n") + `\n\n## 원문\n\n${$("#t-posting-body").value.trim()}\n`;
}

function showPosting(text) {
  const p = A.parsePosting(text || "");
  $("#f-source").value = p.source || "";
  $("#f-date").value = p.checked_at || "";
  $("#t-posting-body").value = p.body || "";
  state.postingImage = p.image || "";
  setPostingStatus(text ? p.status : "확인함");
}

function setPostingStatus(status) {
  state.postingStatus = status;
  const badge = $("#posting-status");
  badge.textContent = `상태: ${status}`;
  badge.className = `badge ${status === "확인함" ? "b-ok" : "b-stop"}`;
  $("#posting-confirm").classList.toggle("hidden", status === "확인함");
}

const readAsBase64 = (file) => new Promise((resolve, reject) => {
  const fr = new FileReader();
  fr.onload = () => resolve(String(fr.result).split(",")[1]);
  fr.onerror = () => reject(new Error("이미지를 읽지 못했습니다."));
  fr.readAsDataURL(file);
});

async function fromImage() {
  const file = $("#image-pick").files[0];
  const msg = $("#posting-msg");
  if (!file) return;
  if (B.mode === "local" && B.info.engine === "subscription") {
    msg.textContent = "구독 방식은 이미지를 넘기지 못합니다. 본문을 붙여 넣거나 '키·설정'에서 API 키 방식을 골라 주세요.";
    return;
  }
  msg.innerHTML = `<span class="spin"></span> 이미지에서 글을 옮기는 중입니다…`;
  try {
    const data = await readAsBase64(file);
    const text = await B.send({ model: model(), max_tokens: 4000,
      system: "채용 공고 캡처 이미지의 글을 빠짐없이 그대로 옮겨 적습니다. 요약·해석·보충을 하지 않고, 읽을 수 없는 글자는 [읽을 수 없음]으로 둡니다. 옮긴 글만 출력합니다.",
      messages: [{ role: "user", content: [
        { type: "image", source: { type: "base64", media_type: file.type, data } },
        { type: "text", text: "이 공고 이미지의 글을 옮겨 적어 주세요." }] }] });
    $("#t-posting-body").value = text.trim();
    $("#f-source").value = $("#f-source").value.trim() || "이미지";
    state.postingImage = file.name;
    setPostingStatus(A.IMAGE_MARK);
    msg.textContent = "옮긴 글을 이미지와 한 줄씩 대조한 뒤 '확인함'을 눌러 주세요. 그 전에는 분석하지 않습니다.";
  } catch (e) { msg.textContent = e.message; }
}

async function savePosting() {
  const msg = $("#posting-msg");
  if (!company()) { msg.textContent = "회사 이름을 먼저 적어 주세요."; return; }
  try {
    const r = await B.write("posting.md", postingText(), company());
    msg.textContent = `공고를 저장했습니다(${r.path}).${privacyNote(r.privacy)}`;
    refreshCompanies();
  } catch (e) { msg.textContent = e.message; }
}

// 웹 화면은 회사 조사를 하지 않습니다. Claude가 무엇을 쓰든 '회사 조사' 칸은 '조사 안 됨'으로 바꿉니다.
function forceNoResearch(text) {
  const lines = text.replace(/\r\n/g, "\n").split("\n");
  const out = [];
  let skip = false, done = false;
  for (const line of lines) {
    if (line.startsWith("### 회사 조사")) { out.push(line, "", "- 조사 안 됨", ""); skip = true; done = true; continue; }
    if (skip && (line.startsWith("## ") || line.startsWith("### "))) skip = false;
    if (!skip) out.push(line);
  }
  if (!done) return text;
  return out.join("\n").replace(/\n{3,}/g, "\n\n");
}

function analysisFlags(r) {
  const f = r.flags;
  const chip = (on, label) => `<span class="badge ${on ? "b-stop" : "b-ok"}">${esc(label)}: ${on ? "예" : "아니요"}</span>`;
  $("#analysis-flags").innerHTML = chip(f.posting_failed, "공고 읽기 실패") + chip(f.image_unconfirmed, "이미지 확인 전") +
    chip(f.research_none, "회사 조사 없음") +
    `<span class="badge ${f.terms_missing.length ? "b-warn" : "b-ok"}">사전에 없는 용어: ${esc(f.terms_missing.join(", ") || "없음")}</span>`;
}

function checkAnalysisNow() {
  const r = A.checkAnalysis(postingText(), $("#t-analysis").value, state.terms);
  analysisFlags(r);
  $("#analysis-issues").innerHTML = issueList(r.issues);
  return r;
}

async function analyze() {
  const button = $("#analyze"), msg = $("#analysis-msg");
  if (!company()) { $("#posting-msg").textContent = "회사 이름을 먼저 적어 주세요."; return; }
  const pre = A.checkAnalysis(postingText(), "", state.terms);
  analysisFlags(pre);
  if (pre.blocked || pre.summary.errors) {
    $("#analysis-issues").innerHTML = issueList(pre.issues);
    msg.textContent = "공고를 먼저 고쳐 주세요. 빈 공고나 확인 전 이미지 공고로는 분석하지 않습니다.";
    return;
  }
  const ledger = $("#t-ledger").value;
  const found = A.matchTerms($("#t-posting-body").value, state.terms);
  busy(button, true, "분석하는 중");
  try {
    const system = [
      "채용 공고를 지원자의 경험 장부와 잇는 분석 초안을 마크다운으로 씁니다. 아래 형식만 출력합니다.",
      `# 분석 · ${company()}`, "", "## 요구·우대 역량", "", "| 역량 | 구분 | 공고 원문 줄 | 장부 경험 | 빈 칸 |", "|---|---|---|---|---|",
      "(구분은 필수·우대. 공고 원문 줄은 공고에서 그대로 옮김. 장부 경험은 장부에 실제로 있는 E01 같은 ID만. 맞는 경험이 없으면 장부 경험을 비우고 빈 칸에 '경험 없음')",
      "", "## 세부 업무", "", "- (공고의 주요 업무를 한 줄씩)", "", "## 숨은 키워드 (AI 해석)", "", "- 키워드: 공고 문장에서 읽은 뜻(추측임을 밝혀서)",
      "", "## 회사·직무 맥락", "", "### 공고 안 정보", "", "- (공고에 적힌 회사·직무 정보만)", "", "### 회사 조사", "", "- 조사 안 됨",
      "", "## 용어", "", "| 용어 | 뜻 |", "|---|---|",
      "(용어 표에는 아래 '사전 용어'에 있는 용어만 그 뜻으로 넣습니다. 공고의 다른 전문 용어는 뜻 칸에 '사전에 없음'이라고만 씁니다.)",
      "규칙: 공고와 장부에 없는 사실을 지어내지 않습니다. 회사 조사는 하지 않습니다.",
    ].join("\n");
    const user = `## 공고\n\n${$("#t-posting-body").value}\n\n## 경험 장부\n\n${ledger || "(장부 없음)"}\n\n## 사전 용어\n\n` +
      (found.map((t) => `- ${t.term}: ${t.definition}`).join("\n") || "(없음)");
    const text = await B.send({ model: model(), max_tokens: 4000, system, messages: [{ role: "user", content: user }] });
    $("#t-analysis").value = forceNoResearch(text.trim()) + "\n";
    const r = checkAnalysisNow();
    msg.textContent = `분석 초안입니다. 오류 ${r.summary.errors}개. 장부 경험 ID와 숨은 키워드를 직접 확인한 뒤 저장해 주세요.`;
  } catch (e) { msg.textContent = e.message; }
  finally { busy(button, false); }
}

async function saveAnalysis() {
  const msg = $("#analysis-msg");
  if (!company()) { msg.textContent = "회사 이름을 먼저 적어 주세요."; return; }
  try {
    const r = await B.write("analysis.md", $("#t-analysis").value, company());
    checkAnalysisNow();
    msg.textContent = `분석을 저장했습니다(${r.path}).`;
  } catch (e) { msg.textContent = e.message; }
}

// ---------- ③ 작성 ----------
function setDraft(name, text) {
  state.draftName = name;
  state.base = name ? text : "";
  $("#t-draft").value = text;
  $("#draft-name").textContent = name || "새 초안";
}

function draftHead() {
  return `# 자기소개서 · ${company()}\n\n- 회사: ${company()}\n- 모드: ${$("#edit-box").open && $("#q-original").value.trim() ? "첨삭" : "초안"}\n- 날짜: ${today()}\n`;
}

async function writeQuestion() {
  const button = $("#q-write"), msg = $("#q-msg");
  const title = $("#q-title").value.trim();
  if (!company()) { msg.textContent = "② 공고 탭에서 회사 이름을 먼저 적어 주세요."; return; }
  if (!title) { msg.textContent = "문항을 적어 주세요."; return; }
  const ledger = $("#t-ledger").value;
  if (!A.parseLedger(ledger).experiences.length) { msg.textContent = "① 장부에 경험이 없습니다. 장부부터 채워 주세요."; return; }
  const draft = $("#t-draft").value.trim() ? $("#t-draft").value : draftHead();
  const no = A.parseDraft(draft).questions.length + 1;
  const limit = parseInt($("#q-limit").value, 10) || 0;
  const unit = $("#q-basis").value === "바이트" ? "바이트" : "자";
  const limitText = limit ? `${limit}${unit}${unit === "자" ? `(${$("#q-basis").value})` : ""}` : "없음";
  const original = $("#edit-box").open ? $("#q-original").value.trim() : "";
  const analysis = $("#t-analysis").value;
  busy(button, true, "쓰는 중");
  try {
    const system = [
      "지원자의 경험 장부만 근거로 자기소개서 한 문항을 씁니다. 아래 형식의 마크다운만 출력합니다.",
      `## 문항 ${no}. ${title}`, `- 유형: ${$("#q-type").value}`, `- 제한: ${limitText}`, `- 판: v1 · 첫 판`, "- 상태: 작성 중",
      "- 연결: (이 문항이 보여 주는 분석의 역량·세부 업무 이름을 쉼표로)", "", "(본문: 한 줄에 한 문장)",
      "규칙:",
      "- 문장마다 끝에 근거 주석을 답니다. 장부 경험이면 <!-- E01 행동 -->처럼 ID와 칸(상황·과제·행동·결과·연결)을, 공고 내용이면 <!-- 공고 -->, 내 생각·포부면 <!-- 의견 -->.",
      "- 숫자·기간·직함·성과는 장부에 있는 그대로만 씁니다. '(AI 정리, 확인 전)' 칸은 근거로 쓰지 않습니다.",
      "- [설계안(도입 가정)]·[계획] 행동은 과거형 성과로 쓰지 않습니다.",
      "- 장부에 근거가 없는데 문항이 요구하는 내용은 지어내지 말고 그 줄에 [사용자 확인 필요: 무엇이 필요한지]를 남깁니다.",
      "- 상황·과제는 짧게, 내 행동과 판단 이유는 길게, 팀 성과 안에서 내가 한 일을 밝히고, 지원 직무와 잇는 문장으로 끝냅니다.",
      "- 회사 조사가 '조사 안 됨'·'자료 없음'이면 회사에 대한 사실을 쓰지 않습니다.",
      limit ? `- 본문 길이는 ${limitText}의 90~100%로 맞춥니다.` : "",
      original ? "- 첨삭 모드입니다. 원문의 내용과 말투를 살려 고치고, 원문에 없던 사실은 장부 근거가 있을 때만 더합니다." : "",
    ].filter(Boolean).join("\n");
    const user = `## 회사\n${company()}\n\n## 경험 장부\n\n${ledger}\n\n## 공고 분석\n\n${analysis || "(분석 없음)"}` +
      (original ? `\n\n## 첨삭할 원문\n\n${original}` : "");
    const text = await B.send({ model: model(), max_tokens: 4000, system, messages: [{ role: "user", content: user }] });
    let head = draft;
    if (original && !/^- 원문:/m.test(head)) head = head.replace(/^- 모드: .*$/m, "- 모드: 첨삭\n- 원문: 화면에 붙여 넣은 원문");
    $("#t-draft").value = head.trimEnd() + "\n\n" + text.trim() + "\n";
    const q = A.parseDraft($("#t-draft").value).questions.pop();
    const c = q ? A.count(A.bodyText(q.paras)) : null;
    msg.textContent = `문항 ${no} 초안을 붙였습니다${c ? `(공백 포함 ${c.with_spaces}자)` : ""}. 근거와 [사용자 확인 필요] 칸을 직접 고친 뒤 '새 판으로 저장'을 눌러 주세요.`;
  } catch (e) { msg.textContent = e.message; }
  finally { busy(button, false); }
}

async function saveDraft() {
  const msg = $("#draft-msg");
  const text = $("#t-draft").value;
  if (!company()) { msg.textContent = "회사 이름을 먼저 적어 주세요."; return; }
  if (!text.trim()) { msg.textContent = "초안이 비었습니다."; return; }
  try {
    // 확정 문항이 바뀌었으면 저장 전에 멈춥니다(write 스킬의 확정 문항 보호와 같음).
    if (state.base) {
      const changed = runCoreCheck().issues.filter((i) => i.code === "confirmed_changed");
      if (changed.length) { msg.textContent = `${changed.map((i) => i.where).join(", ")}: ${changed[0].message}`; return; }
    }
    const r = await B.newDraft(company(), text);
    await refreshDrafts(r.name);
    setDraft(r.name, text);
    msg.textContent = `${r.name}로 저장했습니다(${r.path}).${privacyNote(r.privacy)}`;
  } catch (e) { msg.textContent = e.message; }
}

async function refreshDrafts(selected = "") {
  const names = await B.drafts(company()).catch(() => []);
  $("#draft-pick").innerHTML = `<option value="">새 초안</option>` + names.map((n) => `<option>${esc(n)}</option>`).join("");
  $("#draft-pick").value = names.includes(selected) ? selected : "";
}

async function pickDraft() {
  const name = $("#draft-pick").value;
  if (!name) { setDraft("", ""); return; }
  try { setDraft(name, await B.read(name, company())); } catch (e) { $("#draft-msg").textContent = e.message; }
}

// ---------- ④ 검사·제출 ----------
function runCoreCheck() {
  return A.check($("#t-draft").value, $("#t-ledger").value, $("#t-analysis").value, postingText(), $("#t-style").value,
    state.companies, state.terms, state.base);
}

function runCheck() {
  const box = $("#check-result"), badge = $("#check-badge");
  if (!$("#t-draft").value.trim()) { box.innerHTML = `<p class="usage">③ 작성 탭에 초안이 없습니다.</p>`; badge.textContent = ""; return null; }
  const r = runCoreCheck();
  const s = r.summary;
  badge.textContent = s.submittable ? "제출 가능" : s.errors ? `오류 ${s.errors}개` : "확정 전";
  badge.className = `badge ${s.submittable ? "b-ok" : s.errors ? "b-stop" : "b-warn"}`;
  const qs = r.questions.map((q) => {
    const value = q.limit ? q.count[q.basis] : q.count.with_spaces;
    return `<tr><td>${q.no}. ${esc(q.title)}</td><td>${esc(q.type || "-")}</td><td>${esc(q.version || "-")}</td><td>${q.confirmed ? "확정" : "작성 중"}</td>` +
      `<td>${BASIS[q.basis]}</td><td class="num">${value}</td><td class="num">${q.limit || "-"}</td>` +
      `<td class="num">${q.ratio === null ? "-" : q.ratio + "%"}</td><td>${FIT[q.fit]}</td></tr>`;
  }).join("");
  const counts = r.questions.map((q) => `문항 ${q.no}: 공백 포함 ${q.count.with_spaces}자 · 공백 제외 ${q.count.without_spaces}자 · ${q.count.bytes}바이트`).join("<br>");
  const shorts = r.short_fields.length ? `<h3>짧은 칸</h3><div class="scroll"><table><thead><tr><th>칸</th><th>글자</th><th>제한</th><th>비율</th></tr></thead><tbody>` +
    r.short_fields.map((f) => `<tr><td>${esc(f.name)}</td><td class="num">${f.count.with_spaces}</td><td class="num">${f.limit || "-"}</td>` +
      `<td class="num">${f.ratio === null ? "-" : f.ratio + "%"}</td></tr>`).join("") + `</tbody></table></div>` : "";
  const cover = r.coverage.length ? `<h3>역량·세부 업무 커버리지</h3><div class="scroll"><table><thead><tr><th>항목</th><th>구분</th><th>문항</th></tr></thead><tbody>` +
    r.coverage.map((c) => `<tr><td>${esc(c.item)}</td><td>${esc(c.kind)}</td><td>${c.questions.join(", ") || "<b>빠짐</b>"}</td></tr>`).join("") + `</tbody></table></div>` : "";
  box.innerHTML = `<p>${esc(r.company || "회사 미정")} · 오류 ${s.errors}개 · 경고 ${s.warnings}개 · 확정 ${s.confirmed_all ? "모두" : "아직 아님"}` +
    `${state.draftName ? ` · 비교한 이전 판: ${esc(state.draftName)}` : ""}</p>` +
    `<h3>글자 수</h3><div class="scroll"><table><thead><tr><th>문항</th><th>유형</th><th>판</th><th>상태</th><th>기준</th><th>글자</th><th>제한</th><th>비율</th><th>판정</th></tr></thead>` +
    `<tbody>${qs}</tbody></table></div><p class="usage">${counts}<br>바이트는 UTF-8 기준(한글 3바이트)입니다.</p>${shorts}${cover}` +
    `<h3>문제</h3><ul class="issues">${issueList(r.issues)}</ul>`;
  $("#submit-go").disabled = true;
  return r;
}

async function previewSubmit() {
  const msg = $("#submit-msg"), pre = $("#submit-text");
  const r = runCheck();
  if (!r) return;
  if (!r.summary.submittable) {
    msg.textContent = r.summary.errors ? `검사 오류가 ${r.summary.errors}개 있습니다. 고친 뒤 넘겨 주세요.` : "아직 '상태: 확정'이 아닌 문항이 있습니다.";
    return;
  }
  const text = A.submission($("#t-draft").value);
  const found = A.scan(text);
  pre.textContent = text;
  pre.classList.remove("hidden");
  if (found.length) { msg.textContent = `제출본에${privacyNote(found)}`; return; }
  if (B.mode === "local") {
    if (!state.draftName || $("#t-draft").value !== state.base) { msg.textContent = "③ 작성 탭에서 '새 판으로 저장'을 먼저 눌러 주세요. 저장한 판만 넘깁니다."; return; }
    try {
      const j = await B.api("api/submit", { company: company(), draft: state.draftName, dry_run: true });
      msg.textContent = `넘길 곳: ${j.files.map((f) => `${f.kind} → ${f.path}`).join(" · ")}${j.warning ? ` · 경고: ${j.warning}` : ""}`;
    } catch (e) { msg.textContent = e.message; return; }
  } else {
    msg.textContent = `'넘기기'를 누르면 자기소개서-${slug(company())}.md로 내려받습니다. 19번 새록 면접관 화면에 그대로 붙여 넣을 수 있습니다.`;
  }
  $("#submit-go").disabled = false;
}

async function doSubmit() {
  const msg = $("#submit-msg");
  $("#submit-go").disabled = true;
  if (B.mode === "local") {
    try {
      const j = await B.api("api/submit", { company: company(), draft: state.draftName, dry_run: false });
      msg.textContent = `넘겼습니다: ${j.files.map((f) => f.path).join(", ")}. 다음: ${j.next}`;
    } catch (e) { msg.textContent = e.message; }
    return;
  }
  const blob = new Blob([A.submission($("#t-draft").value)], { type: "text/markdown;charset=utf-8" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = `자기소개서-${slug(company())}.md`;
  a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 1000);
  msg.textContent = "내려받았습니다. 19번 새록 면접관에서 서류 심사를 받아 보세요.";
}

// ---------- 회사 바꾸기 ----------
async function refreshCompanies() {
  state.companies = await B.companies().catch(() => []);
  $("#company-list").innerHTML = state.companies.filter((c) => c.from === "folder").map((c) => `<option value="${esc(c.name)}">`).join("");
}

async function loadCompany() {
  const co = company();
  if (!co) return;
  try {
    showPosting(await B.read("posting.md", co));
    $("#t-analysis").value = await B.read("analysis.md", co);
    if ($("#t-analysis").value) checkAnalysisNow(); else { $("#analysis-flags").innerHTML = ""; $("#analysis-issues").innerHTML = ""; }
    await refreshDrafts();
    setDraft("", "");
    $("#posting-msg").textContent = "";
  } catch (e) { $("#posting-msg").textContent = e.message; }
}

// ---------- 설정 ----------
function renderMode() {
  $("#mode").innerHTML = B.mode === "local"
    ? `<b>내 PC 모드</b> · 글은 <code>${esc(B.info.home)}</code>에만, 제출본은 <code>${esc(B.info.interview_docs)}</code>로 넘기고, Claude는 ` +
      (B.info.engine === "subscription" ? "내 구독(Claude Code)으로 부릅니다(이미지 공고는 API 키 방식에서만)" : `API 키로 부릅니다(키: ${esc(B.info.key_from || "아직 없음")})`)
    : `<b>브라우저 모드</b> · 키와 장부·공고·초안은 이 브라우저에만 저장되고, Claude는 Anthropic에 바로 연결합니다. ` +
      `내 PC 지원 폴더에 저장하려면 터미널에서 <code>saerok-apply</code>를 실행하세요.`;
  const warning = B.mode === "local" ? B.info.warning : "";
  $("#git-warning").textContent = warning;
  $("#git-warning").classList.toggle("hidden", !warning);
}

function openSettings() {
  $("#model").innerHTML = MODELS.map(([v, n]) => `<option value="${v}">${n}</option>`).join("");
  $("#model").value = model();
  $("#settings-msg").textContent = "";
  $("#key-browser").classList.toggle("hidden", B.mode === "local");
  $("#engine-local").classList.toggle("hidden", B.mode !== "local");
  $("#key-local").classList.toggle("hidden", B.mode !== "local" || B.info.engine !== "api");
  if (B.mode === "local") {
    for (const r of $$('input[name="engine"]')) {
      r.checked = r.value === B.info.engine;
      r.disabled = r.value === "subscription" && !B.info.claude_cli;
      r.onchange = () => $("#key-local").classList.toggle("hidden", r.value !== "api" || !r.checked);
    }
    $("#engine-note").textContent = B.info.claude_cli
      ? "구독 방식은 이 PC에 로그인한 Claude Code(claude 명령)로 돌리고, 구독 사용량에서 차감됩니다. 이미지 공고는 옮기지 못합니다."
      : "claude 명령을 찾지 못해 API 키 방식만 쓸 수 있습니다. Claude Code를 설치하고 로그인하면 구독으로 돌릴 수 있습니다.";
    $("#key-now").textContent = B.info.key;
    $("#key-from").textContent = B.info.key_from ? `(${B.info.key_from})` : "";
    $("#key-local-input").value = "";
  } else {
    $("#key-input").value = browserKey();
    $("#key-remember").checked = Boolean(local.get(KEY, ""));
  }
  $("#settings").showModal();
}

async function saveSettings() {
  local.set(PREFS, { model: $("#model").value });
  try {
    if (B.mode === "local") {
      const picked = $('input[name="engine"]:checked');
      if (picked && picked.value !== B.info.engine) {
        const j = await B.api("api/engine", { engine: picked.value });
        B.info.engine = j.engine;
      }
      const key = $("#key-local-input").value.trim();
      if (key) {
        const j = await B.api("api/key", { key });
        Object.assign(B.info, { key: j.key, key_from: j.key_from });
      }
      renderMode();
    } else {
      const key = $("#key-input").value.trim();
      if (key && !key.startsWith("sk-ant-")) throw new Error("Anthropic API 키는 sk-ant-로 시작합니다.");
      local.del(KEY);
      local.del(KEY, sessionStorage);
      if (key) local.set(KEY, key, $("#key-remember").checked ? localStorage : sessionStorage);
    }
    $("#settings").close();
  } catch (e) {
    $("#settings-msg").textContent = e.message;
  }
}

async function forgetKey() {
  try {
    if (B.mode === "local") {
      const j = await B.api("api/key/delete", {});
      Object.assign(B.info, { key: j.key, key_from: j.key_from });
      $("#key-now").textContent = j.key;
      $("#key-from").textContent = j.key_from ? `(${j.key_from}, 여기서는 지우지 않음)` : "";
      renderMode();
    } else {
      local.del(KEY);
      local.del(KEY, sessionStorage);
      $("#key-input").value = "";
    }
    $("#settings-msg").textContent = "키를 지웠습니다.";
  } catch (e) {
    $("#settings-msg").textContent = e.message;
  }
}

async function main() {
  await B.init();
  renderMode();
  [state.terms, state.templates] = await Promise.all([loadJSON("data/terms-lite.json").catch(() => null), loadJSON("data/templates.json").catch(() => null)]);
  $("#q-type").innerHTML = A.TYPES.map((t) => `<option>${esc(t)}</option>`).join("");
  $("#f-date").placeholder = today();
  await refreshCompanies();
  try {
    $("#t-ledger").value = await B.read("ledger.md");
    $("#t-style").value = await B.read("style.md");
    if ($("#t-ledger").value) checkLedger();
  } catch (e) { $("#ledger-msg").textContent = e.message; }
  const folders = state.companies.filter((c) => c.from === "folder");
  if (folders.length === 1) { $("#f-company").value = folders[0].name; await loadCompany(); }

  $("#ledger-template").onclick = () => {
    if (!state.templates) return;
    if (!$("#t-ledger").value.trim()) $("#t-ledger").value = state.templates["ledger.md"];
    if (!$("#t-style").value.trim()) $("#t-style").value = state.templates["style.md"];
  };
  for (const b of $$("[data-load]")) b.onclick = () => pickFile((t) => { $("#t-ledger").value = t; checkLedger(); });
  $("#ledger-check").onclick = checkLedger;
  $("#ledger-save").onclick = saveLedger;
  $("#f-company").onchange = loadCompany;
  $("#image-pick").onchange = fromImage;
  $("#posting-confirm").onclick = () => { setPostingStatus("확인함"); $("#posting-msg").textContent = "확인함으로 바꿨습니다. 공고를 저장해 주세요."; };
  $("#t-posting-body").oninput = () => { if (!$("#t-posting-body").value.trim()) state.postingImage = ""; };
  $("#posting-save").onclick = savePosting;
  $("#analyze").onclick = analyze;
  $("#analysis-check").onclick = checkAnalysisNow;
  $("#analysis-save").onclick = saveAnalysis;
  $("#q-title").oninput = () => { $("#q-type").value = A.guessType($("#q-title").value); };
  $("#q-write").onclick = writeQuestion;
  $("#draft-pick").onchange = pickDraft;
  $("#draft-save").onclick = saveDraft;
  $("#draft-to-check").onclick = () => selectTab("check");
  $("#check-run").onclick = runCheck;
  $("#submit-preview").onclick = previewSubmit;
  $("#submit-go").onclick = doSubmit;
  $("#open-settings").onclick = openSettings;
  $("#save-settings").onclick = saveSettings;
  $("#forget-key").onclick = forgetKey;
  $("#close-settings").onclick = () => $("#settings").close();
  for (const t of $$(".tab")) t.onclick = () => selectTab(t.dataset.tab);
}

main();
