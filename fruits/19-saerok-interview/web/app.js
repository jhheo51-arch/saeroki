/* 새록 면접관 화면. 진행 순서는 skills/panel·practice/SKILL.md와 같고, 검사·점수·verdict.md는 interview-core.js(= saerok_interview)가 냅니다.
   브라우저 모드: 키·서류·기록은 이 브라우저에만, Claude는 api.anthropic.com을 바로 부릅니다.
   내 PC 모드(saerok-interview): 기록은 ~/.saerok/interview, Claude 호출은 내 PC 서버가 넘깁니다(기본은 내 구독, 고르면 API 키). */
"use strict";

const S = window.SaerokInterview;
const $ = (sel, el = document) => el.querySelector(sel);
const $$ = (sel, el = document) => Array.from(el.querySelectorAll(sel));
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const pad = (n) => String(n).padStart(2, "0");
const today = () => { const d = new Date(); return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`; };
const fmt = (v) => (v === null || v === undefined ? "-" : String(v));
const nameOf = (who) => `${S.INTERVIEWERS[who].name} 면접관`;

const MODELS = [
  ["claude-sonnet-5-5", "Claude Sonnet 5.5"],
  ["claude-opus-5-5", "Claude Opus 5.5"],
  ["claude-haiku-5-5", "Claude Haiku 5.5"],
];
const PREFS = "saerok-interview:prefs";
const KEY = "saerok-interview:key";
const SESSIONS = "saerok-interview:sessions";
const TERMS_FOR = ["practitioner", "numbers"];  // 용어 목록은 실무·숫자 검증 면접관에게만(panel 스킬 4단계)

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
const prefs = () => {
  // 목록에 없는 모델(옛 저장값·빈 값)은 기본값으로 돌려 선택 칸이 비지 않게 합니다.
  const saved = local.get(PREFS, {}) || {};
  const ok = (v) => MODELS.some(([id]) => id === v);
  return { panel: ok(saved.panel) ? saved.panel : MODELS[0][0], practice: ok(saved.practice) ? saved.practice : MODELS[0][0] };
};
const browserKey = () => local.get(KEY, "", sessionStorage) || local.get(KEY, "");

// ---------- 백엔드: 브라우저 모드 / 내 PC 모드 ----------
// 세션 하나는 {id, meta, score, inputs}입니다. 내 PC 모드의 id는 세션 폴더 경로, 브라우저 모드는 세션 이름입니다.
const API_HEADERS = { "Content-Type": "application/json", "X-Saerok-Interview": "1" };

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
    return j;
  },

  all() { return local.get(SESSIONS, {}) || {}; },
  saveAll(all) {
    if (!local.set(SESSIONS, all)) throw new Error("브라우저 저장 공간에 쓰지 못했습니다. 기록 탭에서 오래된 세션을 내려받은 뒤 지워 주세요.");
  },
  keep(sess) {
    const all = this.all();
    all[sess.id] = { meta: sess.meta, score: sess.score, inputs: sess.inputs };
    this.saveAll(all);
  },

  async create(texts, opts) {
    if (this.mode === "local") {
      const j = await this.api("api/new", { texts, ...opts });
      return { id: j.folder, meta: j.meta, score: j.score, inputs: j.inputs, privacy: j.privacy };
    }
    const all = this.all();
    const made = await S.createSession(texts, { ...opts, date: today() }, Object.keys(all));
    const sess = { id: made.meta.session, meta: made.meta, score: made.score, inputs: made.inputs, privacy: made.privacy };
    this.keep(sess);
    return sess;
  },

  // 내 PC 모드는 서버(saerok_interview.store)가 검사·기록한 결과를, 브라우저 모드는 같은 규칙의 interview-core.js 결과를 씁니다.
  async record(sess, kind, data) {
    if (this.mode === "local") {
      const j = await this.api("api/record", { folder: sess.id, kind, data });
      if (kind === "document") sess.score.document[data.interviewer] = j.result;
      else if (kind === "answer") sess.score.answers.push(j.result);
      else sess.score.real.push(j.result);
      return j.result;
    }
    const out = kind === "document" ? S.recordDocument(sess, data)
      : kind === "answer" ? S.recordAnswer(sess, data, today()) : S.recordReal(sess, data, today());
    this.keep(sess);
    return out;
  },

  async report(sess) {
    if (this.mode === "local") return this.api("api/report", { folder: sess.id });
    return { verdict: S.renderReport(sess), practice: S.renderPractice(sess.meta, sess.score), path: null };
  },

  // 목록에는 본문(inputs)이 없을 수 있습니다. 질문·채점에 본문이 필요하면 get으로 채웁니다.
  async list() {
    if (this.mode === "local") {
      const rows = await this.api("api/sessions");
      return rows.map((r) => ({ id: r.folder, meta: r.meta, score: r.score, inputs: null }));
    }
    const all = this.all();
    return Object.keys(all).sort().map((id) => ({ id, ...all[id] }));
  },

  async get(sess) {
    if (sess.inputs) return sess;
    const j = await this.api(`api/session?folder=${encodeURIComponent(sess.id)}`);
    return { id: j.folder, meta: j.meta, score: j.score, inputs: j.inputs };
  },

  remove(sess) {
    const all = this.all();
    delete all[sess.id];
    this.saveAll(all);
  },
};

// ---------- Claude 호출 ----------
const usage = { input: 0, output: 0, calls: 0 };

async function claude({ system, user, model, maxTokens = 3000 }) {
  const r = await B.send({ model, max_tokens: maxTokens, system, messages: [{ role: "user", content: user }] });
  usage.calls += 1;
  usage.input += (r.usage && r.usage.input_tokens) || 0;
  usage.output += (r.usage && r.usage.output_tokens) || 0;
  renderUsage();
  return (r.content || []).filter((c) => c.type === "text").map((c) => c.text).join("");
}

function parseJSON(text) {
  const fenced = [...text.matchAll(/```(?:json)?\s*([\s\S]*?)```/g)].map((m) => m[1]);
  const tries = fenced.reverse();
  const a = text.indexOf("{"), b = text.lastIndexOf("}");
  if (a >= 0 && b > a) tries.push(text.slice(a, b + 1));
  for (const t of tries) {
    try { return JSON.parse(t); } catch (e) { /* 다음 후보 */ }
  }
  throw new Error("답에서 JSON을 찾지 못했습니다.");
}

// 형식 검사에 걸리면 오류 문장을 붙여 한 번만 다시 묻습니다(panel 스킬 5단계와 같음).
async function askJSON(opts, check) {
  let user = opts.user, lastError;
  for (let attempt = 0; attempt < 2; attempt++) {
    const text = await claude({ ...opts, user });
    try {
      const data = parseJSON(text);
      return check ? check(data) : data;
    } catch (e) {
      lastError = e;
      user = `${opts.user}\n\n앞선 답이 형식 검사에서 걸렸습니다: ${e.message}\n설명 없이 JSON 하나만 다시 주세요.`;
    }
  }
  throw lastError;
}

const agentCache = {};
async function agentPrompt(who) {
  if (!agentCache[who]) {
    const r = await fetch(`agents/${who}.md`);
    if (!r.ok) throw new Error(`면접관 기준 파일(agents/${who}.md)을 읽지 못했습니다.`);
    agentCache[who] = (await r.text()).replace(/^---[\s\S]*?\n---\s*\n/, "").trim();
  }
  return agentCache[who];
}

let termsData = null;
async function loadTerms() {
  if (!termsData) {
    const r = await fetch("data/terms-lite.json");
    if (!r.ok) throw new Error("용어 목록(data/terms-lite.json)을 읽지 못했습니다.");
    termsData = await r.json();
  }
  return termsData;
}

// ---------- 서류 심사 지시(에이전트 파일 + 이 화면에서 달라지는 점) ----------
const WEB_NOTE = `

## 이 화면에서 달라지는 점

Read 도구는 없다. 입력 파일 본문은 사용자 메시지에 '줄 번호: 내용' 꼴로 붙어 있다. 근거의 line에는 그 줄 번호를 쓰고, quote에는 줄 번호를 빼고 원문만 그대로 옮긴다.`;

function numbered(text) {
  return S.splitlines(text).map((line, i) => `${i + 1}: ${line}`).join("\n");
}

function docsBlock(sess) {
  return S.DOCS.filter((k) => sess.meta.inputs[k])
    .map((k) => `### ${k} (${S.DOC_NAMES[k]})\n${numbered(sess.inputs[k])}`).join("\n\n");
}

async function termsBlock(meta) {
  if (!meta.industry || !meta.role) return "";
  const picked = S.pickTerms(await loadTerms(), meta.industry, meta.role, 20);
  return `\n\n이 산업·직무의 핵심 용어(17번 새록 사전):\n${picked.terms.map((t) => `- ${t.term}(${t.original}): ${t.definition}`).join("\n")}`;
}

// ---------- 화면 상태 ----------
const state = { sess: null, busy: false, practice: null, list: [] };

function log(id, text, kind = "") {
  const li = document.createElement("li");
  if (kind) li.className = kind;
  li.textContent = `${kind === "err" ? "⚠ " : kind === "warn" ? "• " : "✓ "}${text}`;
  $(id).appendChild(li);
}
function show(id) { $(id).classList.remove("hidden"); }
function hide(id) { $(id).classList.add("hidden"); }
function busy(on) {
  state.busy = on;
  $$("#start, #p-next, #p-send, #p-stop, #load-docs").forEach((b) => { b.disabled = on; });
}
function renderUsage() {
  $$(".usage-live").forEach((el) => {
    el.textContent = `이번 화면 사용량: Claude 호출 ${usage.calls}번 · 입력 토큰 ${usage.input.toLocaleString()} · 출력 토큰 ${usage.output.toLocaleString()}`;
  });
}
function verdictClass(v) { return { 합격권: "v-합격권", 보류: "v-보류2", 부족: "v-부족" }[v] || "v-none"; }

function retryButton(logId, fn) {
  const li = document.createElement("li");
  const b = document.createElement("button");
  b.className = "btn small";
  b.textContent = "이 단계 다시 시도";
  b.onclick = async () => { li.remove(); busy(true); try { await fn(); } catch (e) { log(logId, e.message, "err"); retryButton(logId, fn); } finally { busy(false); } };
  li.appendChild(b);
  $(logId).appendChild(li);
}

function download(name, text, type) {
  const url = URL.createObjectURL(new Blob([text], { type }));
  const a = document.createElement("a");
  a.href = url;
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

// ---------- 1. 서류 넣기 ----------
function readTexts() {
  const texts = {};
  for (const k of S.DOCS) {
    const v = $(`#d-${k}`).value;
    if (v.trim()) texts[k] = v;
  }
  return texts;
}

function readOpts() {
  const opts = { company: $("#f-company").value.trim(), industry: $("#f-industry").value, role: $("#f-role").value };
  if (Boolean(opts.industry) !== Boolean(opts.role)) throw new Error("산업과 직무는 함께 고르거나 함께 비워 주세요.");
  return opts;
}

// 개인정보 꼴을 먼저 보여 주고, 사용자가 그대로 진행할지 정합니다(panel 스킬 2단계).
function privacyOK(texts) {
  const hits = [];
  for (const [k, text] of Object.entries(texts)) {
    for (const h of S.scan(text)) hits.push(`${S.DOC_NAMES[k]} ${h.line}줄: ${h.kind} ${h.masked}`);
  }
  if (!hits.length) return true;
  return confirm(`개인정보로 보이는 값이 있습니다.\n\n${hits.slice(0, 12).join("\n")}${hits.length > 12 ? `\n…외 ${hits.length - 12}개` : ""}\n\n` +
    "지운 뒤 다시 하려면 '취소'를, 그대로 Claude에 보내 심사하려면 '확인'을 눌러 주세요.");
}

async function start() {
  if (state.busy) return;
  let texts, opts;
  try {
    texts = readTexts();
    opts = readOpts();
    if (!texts.resume_letter) throw new Error("자기소개서는 꼭 필요합니다.");
    if (opts.industry) S.pickTerms(await loadTerms(), opts.industry, opts.role, 1);
  } catch (e) {
    return alert(e.message);
  }
  if (!privacyOK(texts)) return;
  if (B.mode === "browser" && !browserKey()) {
    openSettings();
    return;
  }
  busy(true);
  $("#judges").innerHTML = "";
  $("#log-panel").innerHTML = "";
  hide("#step-result");
  try {
    state.sess = await B.create(texts, opts);
    show("#step-panel");
    log("#log-panel", B.mode === "local" ? `세션 폴더: ${state.sess.id}` : `브라우저 세션: ${state.sess.id}`);
    if (!state.sess.meta.posting) log("#log-panel", "채용 공고가 없어 실무 '공고 요건 연결'과 임원 '회사·산업 이해'는 해당 없음으로 봅니다.", "warn");
    $("#step-panel").scrollIntoView({ behavior: "smooth" });
    await runPanel();
  } catch (e) {
    show("#step-panel");
    log("#log-panel", e.message, "err");
  } finally {
    busy(false);
  }
}

// ---------- 2. 면접관 5명 ----------
function judgeCard(who, doc, pending) {
  const meta = S.INTERVIEWERS[who];
  const head = `<div class="who">${esc(nameOf(who))}</div><div class="q">${esc(meta.looks_at)}</div>`;
  if (pending) return `<div class="judge" id="j-${who}">${head}<p><span class="spin"></span> 심사 중</p></div>`;
  if (!doc) return `<div class="judge" id="j-${who}">${head}<p>결과 없음</p></div>`;
  const v = S.verdict(doc.total);
  return `<div class="judge" id="j-${who}">${head}
    <div class="score">${fmt(doc.total)}<small style="font-size:14px;color:var(--muted)">/10</small> <span class="badge ${verdictClass(v)}">${esc(v)}</span></div>
    <div class="ev">${esc(doc.comment)}</div>
    <div class="lbl">질문</div><ul>${doc.questions.map((q) => `<li>${esc(q.question)} <span class="badge ${q.grounded ? "s-확인됨" : "s-확인안됨"}">${q.grounded ? "근거 확인" : "일반 질문"}</span></li>`).join("")}</ul>
    <div class="lbl">고칠 점</div><ul>${doc.fixes.map((f) => `<li>${esc(f)}</li>`).join("") || "<li>없음</li>"}</ul></div>`;
}

async function runPanel() {
  const sess = state.sess;
  $("#judges").innerHTML = S.ORDER.map((w) => judgeCard(w, sess.score.document[w], !sess.score.document[w])).join("");
  const todo = S.ORDER.filter((w) => !sess.score.document[w]);
  const docs = docsBlock(sess);
  const terms = await termsBlock(sess.meta);
  const results = await Promise.allSettled(todo.map(async (who) => {
    const system = (await agentPrompt(who)) + WEB_NOTE;
    const user = `회사: ${sess.meta.company || "미지정"}${TERMS_FOR.includes(who) ? terms : ""}\n\n입력 문서:\n\n${docs}\n\n` +
      "에이전트 파일의 기준 항목과 답 형식대로 JSON 하나만 돌려주세요.";
    // 기록 전에 복사본에 같은 검사를 돌려, 걸리면 그 오류 문장으로 한 번 다시 묻습니다.
    const data = await askJSON({ system, user, model: prefs().panel, maxTokens: 2500 }, (d) => {
      d.interviewer = who;
      S.recordDocument({ meta: sess.meta, inputs: sess.inputs, score: structuredClone(sess.score) }, d);
      return d;
    });
    await B.record(sess, "document", data);
    $(`#j-${who}`).outerHTML = judgeCard(who, sess.score.document[who]);
  }));
  const failed = results.map((r, i) => [todo[i], r]).filter(([, r]) => r.status === "rejected");
  for (const [who, r] of failed) {
    $(`#j-${who}`).outerHTML = judgeCard(who, null);
    log("#log-panel", `${nameOf(who)}: ${r.reason.message}`, "err");
  }
  if (failed.length) {
    await showVerdict();  // 빠진 면접관은 verdict.md에 '아직 결과가 없는 면접관'으로 적힙니다.
    return retryButton("#log-panel", runPanel);
  }
  log("#log-panel", "면접관 5명이 모두 답했습니다.");
  await showVerdict();
}

// ---------- 3. 판정 ----------
async function showVerdict() {
  const sess = state.sess;
  const report = await B.report(sess);
  const box = $("#step-result");
  box.innerHTML = verdictHTML(sess, report);
  bindVerdict(box, sess, report);
  show("#step-result");
  box.scrollIntoView({ behavior: "smooth" });
}

function verdictHTML(sess, report) {
  const doc = sess.score.document;
  const list = S.questionList(sess.score);
  const loose = list.filter((q) => !q.grounded).map((q) => `Q${q.no}`);
  const rows = S.ORDER.map((w) => {
    const d = doc[w], v = d ? S.verdict(d.total) : "결과 없음";
    return `<tr><td>${esc(nameOf(w))}</td><td>${d ? `${fmt(d.total)}/10` : "-"}</td><td><span class="badge ${verdictClass(v)}">${esc(v)}</span></td><td>${esc(d ? d.comment : "")}</td></tr>`;
  }).join("");
  return `<h2>🎤 판정 <span class="usage" style="font-weight:400">${esc(sess.meta.session)}</span></h2>
    <p class="note">${esc(S.NOTICE)}</p>
    <div class="scroll"><table><tr><th>면접관</th><th>서류 점수</th><th>판정</th><th>한 줄 평</th></tr>${rows}</table></div>
    <h3>질문 ${list.length}개</h3>
    ${list.map((q) => `<div class="dir"><div class="t">Q${q.no}. [${esc(S.INTERVIEWERS[q.interviewer].name)} · ${esc(S.item(q.interviewer, q.item).name)}] ${esc(q.question)}</div>
      ${q.evidence.map((e) => `<div class="ev"><span class="badge ${e.status === "확인" ? "s-확인됨" : "s-확인안됨"}">${esc(e.status)}</span> ${esc(S.DOC_NAMES[e.doc] || e.doc)} ${esc(e.line)}줄 “${esc(e.quote)}”</div>`).join("") ||
        '<div class="ev usage">근거 없음(일반 질문)</div>'}
      ${q.direction ? `<div class="ev usage">좋은 답의 방향: ${esc(q.direction)}</div>` : ""}</div>`).join("")}
    ${loose.length ? `<p class="usage">근거 원문을 서류에서 찾지 못한 질문: ${loose.join(", ")}. 일반 질문으로 봅니다.</p>` : ""}
    <h3>다음 단계</h3>
    <div class="row">
      <button class="btn primary" data-practice>실전 연습 시작</button>
      <button class="btn" data-download="md">verdict.md 내려받기</button>
      <button class="btn" data-toggle-md>verdict.md 보기</button>
    </div>
    ${B.mode === "local" ? `<p class="usage">내 PC에 저장됨: ${esc(report.path)}</p>` : `<p class="usage">이 브라우저에만 저장했습니다. 다른 기기에서 보려면 내려받아 두세요.</p>`}
    <pre class="md hidden"></pre><p class="usage usage-live"></p>`;
}

function bindVerdict(root, sess, report) {
  root.querySelector("[data-download=md]").onclick = () => download(`${sess.meta.session}-verdict.md`, report.verdict, "text/markdown;charset=utf-8");
  root.querySelector("[data-toggle-md]").onclick = () => {
    const pre = root.querySelector("pre.md");
    pre.textContent = report.verdict;
    pre.classList.toggle("hidden");
  };
  root.querySelector("[data-practice]").onclick = () => { selectTab("practice", sess.id); };
  renderUsage();
}

// ---------- 실전 연습 ----------
const MAX_FOLLOW = { 순한맛: 1, 보통: 2, 매운맛: 2 };

function rubricLines(who, posting) {
  return S.INTERVIEWERS[who].items.map((i) => {
    const auto = S.autoNa(who, i.key, "answer", posting);
    return `- ${i.key}: ${i.name} (0~${i.max}점)${auto ? ` → 자동으로 해당 없음(${auto}), null로 둔다` : ""}`;
  }).join("\n");
}

async function persona(who) {
  return (await agentPrompt(who)).split(/\n\s*\n/)[0];
}

async function followSystem(who, level, mayStop) {
  return `${await persona(who)}

지금은 '새록 면접관' 실전 연습이다. 지원자의 답을 듣고 같은 면접관 입장에서 꼬리 질문 하나를 한다. 면접관 말투로, 한국어로 쓴다.
기준 항목(이 밖의 것을 캐묻지 않는다):
${rubricLines(who, state.practice.sess.meta.posting)}
- 강도 ${level}: ${level === "순한맛" ? "부드럽게 묻고, hint에 답의 방향 힌트 한 줄을 준다." : level === "매운맛" ? "답의 빈틈을 바로 짚어 묻는다. hint는 빈 문자열." : "답에서 가장 약한 곳 하나를 묻는다. hint는 빈 문자열."}
- ${mayStop ? "답이 이미 충분하면 followup을 빈 문자열로 둔다." : "followup은 비우지 않는다."}
- 완성 답안을 쓰지 않는다. 지원자가 말하지 않은 경험을 지어내지 않는다.
설명 없이 JSON 하나만 돌려준다: {"followup": "", "hint": ""}`;
}

async function gradeSystem(who) {
  return `${await persona(who)}

지금은 '새록 면접관' 실전 연습의 채점이다. 아래 기준 항목만으로 지원자의 답(꼬리 질문 답 포함)을 채점한다.
${rubricLines(who, state.practice.sess.meta.posting)}
- 항목마다 0~배점 정수를 준다. 답에서 볼 수 없는 항목은 null로 두고 na에 이유를 적는다. 0점과 '볼 수 없음'을 섞지 않는다.
- missing에는 답에 빠진 것 0~3개, better에는 더 좋은 답의 방향 한 줄을 쓴다. 완성 답안(모범 답변 전문)은 쓰지 않는다.
- 지원자가 답에 넣지 않은 경험을 지어내 칭찬하거나 감점하지 않는다.
설명 없이 JSON 하나만 돌려준다: {"items": {${S.INTERVIEWERS[who].items.map((i) => `"${i.key}": 0`).join(", ")}}, "na": {}, "missing": [], "better": ""}`;
}

function convoText(p) {
  const lines = [`질문: ${p.q.question}`, `지원자 답: ${p.answer}`];
  for (const f of p.followups) {
    lines.push(`꼬리 질문: ${f.question}`);
    if (f.answer !== undefined) lines.push(`지원자 답: ${f.answer}`);
  }
  return lines.join("\n");
}

async function renderPracticeSelect(pick) {
  $("#p-who").innerHTML = S.ORDER.map((w) => `<label class="check"><input type="checkbox" value="${w}"> ${esc(S.INTERVIEWERS[w].name)}</label>`).join("");
  let list;
  try { list = await B.list(); } catch (e) { $("#p-msg").textContent = e.message; return; }
  state.list = list.filter((s) => Object.keys(s.score.document).length);
  const sel = $("#p-session");
  sel.innerHTML = state.list.length
    ? state.list.map((s, i) => `<option value="${i}">${esc(s.meta.session)} · ${esc(s.meta.company || "회사 미지정")} · 답 ${s.score.answers.length}개</option>`).join("")
    : '<option value="">서류 심사한 세션이 없습니다</option>';
  const at = state.list.findIndex((s) => s.id === pick);
  sel.value = String(at >= 0 ? at : state.list.length - 1);
  $("#p-msg").textContent = state.list.length ? "" : "'새 면접' 탭에서 서류 심사를 먼저 해 주세요.";
}

async function pickedSession() {
  const s = state.list[Number($("#p-session").value)];
  if (!s) throw new Error("연습할 세션을 골라 주세요.");
  const full = await B.get(s);
  state.list[Number($("#p-session").value)] = full;
  return full;
}

async function nextQuestion() {
  if (state.busy) return;
  if (B.mode === "browser" && !browserKey()) return openSettings();
  busy(true);
  try {
    const sess = await pickedSession();
    const who = $$("#p-who input:checked").map((c) => c.value);
    const q = S.nextQuestion(sess, who);
    hide("#p-result");
    if (!q) {
      hide("#p-box");
      $("#p-msg").textContent = who.length ? "고른 면접관의 질문에 모두 답했습니다. 다른 면접관을 고르거나 연습 기록을 보세요."
        : "이 세션의 질문에 모두 답했습니다. 연습 기록을 보거나 기록·비교 탭에서 회차를 비교해 보세요.";
      return;
    }
    const level = $("input[name=level]:checked").value;
    state.practice = { sess, q, level, answer: null, followups: [], hints: [] };
    $("#p-msg").textContent = "";
    $("#log-practice").innerHTML = "";
    renderConvo();
    show("#p-box");
    $("#p-answer").value = "";
    $("#p-answer").focus();
  } catch (e) {
    $("#p-msg").textContent = e.message;
  } finally {
    busy(false);
  }
}

function renderConvo() {
  const p = state.practice;
  const who = esc(nameOf(p.q.interviewer));
  let html = `<div class="qa ask"><div class="who">Q${p.q.no} · ${who} · ${esc(p.level)}</div>${esc(p.q.question)}
    ${p.q.evidence.length ? `<details class="more" style="margin-top:6px;padding-top:6px"><summary>근거 원문 보기</summary>${p.q.evidence.map((e) => `<div class="ev">${esc(S.DOC_NAMES[e.doc] || e.doc)} ${esc(e.line)}줄 “${esc(e.quote)}”</div>`).join("")}</details>` : ""}</div>`;
  if (p.answer !== null) html += `<div class="qa"><div class="who">내 답</div>${esc(p.answer)}</div>`;
  p.followups.forEach((f, i) => {
    html += `<div class="qa ask"><div class="who">꼬리 질문 ${i + 1} · ${who}</div>${esc(f.question)}${p.hints[i] ? `<div class="hint">힌트: ${esc(p.hints[i])}</div>` : ""}</div>`;
    if (f.answer !== undefined) html += `<div class="qa"><div class="who">내 답</div>${esc(f.answer)}</div>`;
  });
  $("#p-convo").innerHTML = html;
}

async function sendAnswer() {
  const p = state.practice;
  if (state.busy || !p) return;
  const text = $("#p-answer").value.trim();
  if (!text) return alert("답을 적어 주세요.");
  busy(true);
  try {
    if (p.answer === null) p.answer = text;
    else p.followups[p.followups.length - 1].answer = text;
    $("#p-answer").value = "";
    renderConvo();
    const asked = p.followups.length;
    if (asked < MAX_FOLLOW[p.level]) {
      const mayStop = asked >= 1;  // 첫 꼬리 질문은 늘 하고, 보통의 두 번째는 답이 충분하면 건너뜁니다.
      log("#log-practice", "꼬리 질문을 만드는 중입니다…", "warn");
      const d = await askJSON({ system: await followSystem(p.q.interviewer, p.level, mayStop), user: convoText(p),
        model: prefs().practice, maxTokens: 600 }, (d) => {
        if (typeof d.followup !== "string") throw new Error("followup은 문자열이어야 합니다.");
        if (!mayStop && !d.followup.trim()) throw new Error("첫 꼬리 질문은 비울 수 없습니다.");
        return d;
      });
      if (d.followup.trim()) {
        p.followups.push({ question: d.followup.trim() });
        p.hints.push(p.level === "순한맛" ? String(d.hint || "").trim() : "");
        renderConvo();
        $("#log-practice").innerHTML = "";
        $("#p-answer").focus();
        return;
      }
      log("#log-practice", "답이 충분해 꼬리 질문을 더 하지 않습니다.");
    }
    await grade();
  } catch (e) {
    log("#log-practice", e.message, "err");
    retryButton("#log-practice", grade);
  } finally {
    busy(false);
  }
}

// 이 질문을 그만두면 지금까지 한 답만으로 채점합니다(답이 없으면 기록하지 않음).
async function stopQuestion() {
  const p = state.practice;
  if (state.busy || !p) return;
  if (p.answer === null) { hide("#p-box"); state.practice = null; return; }
  const lastF = p.followups[p.followups.length - 1];
  if (lastF && lastF.answer === undefined) p.followups.pop();
  busy(true);
  try { await grade(); } catch (e) { log("#log-practice", e.message, "err"); retryButton("#log-practice", grade); } finally { busy(false); }
}

async function grade() {
  const p = state.practice;
  log("#log-practice", "채점하는 중입니다…", "warn");
  const followups = p.followups.filter((f) => f.answer !== undefined).map((f) => ({ question: f.question, answer: f.answer }));
  const user = `${convoText({ ...p, followups })}\n\n면접관 메모(좋은 답의 방향): ${p.q.direction || "없음"}`;
  const answer = await askJSON({ system: await gradeSystem(p.q.interviewer), user, model: prefs().practice, maxTokens: 1200 }, (d) => {
    const row = { no: p.q.no, interviewer: p.q.interviewer, level: p.level, question: p.q.question, answer: p.answer,
      followups, items: d.items, na: d.na || {}, missing: Array.isArray(d.missing) ? d.missing : [], better: String(d.better || "") };
    S.recordAnswer({ meta: p.sess.meta, inputs: p.sess.inputs, score: structuredClone(p.sess.score) }, row, today());
    return row;
  });
  const row = await B.record(p.sess, "answer", answer);
  const opt = $("#p-session").selectedOptions[0];
  if (opt) opt.textContent = `${p.sess.meta.session} · ${p.sess.meta.company || "회사 미지정"} · 답 ${p.sess.score.answers.length}개`;
  hide("#p-box");
  state.practice = null;
  const box = $("#p-result");
  const v = S.verdict(row.total);
  box.innerHTML = `<h2>Q${row.no} 채점 <span class="badge ${verdictClass(v)}">${esc(v)}</span></h2>
    <p class="note">${esc(S.NOTICE)}</p>
    <div class="score" style="font-size:26px;font-weight:800">${fmt(row.total)}<small style="font-size:14px;color:var(--muted)">/10</small></div>
    <ul>${S.INTERVIEWERS[row.interviewer].items.map((i) => `<li>${esc(i.name)}: ${row.items[i.key] === null ? `해당 없음(${esc(row.na[i.key] || "")})` : `${row.items[i.key]}/${i.max}`}</li>`).join("")}</ul>
    ${row.missing.length ? `<p><b>빠진 것</b>: ${esc(row.missing.join(", "))}</p>` : ""}
    ${row.better ? `<p><b>더 좋은 답의 방향</b>: ${esc(row.better)}</p>` : ""}
    <div class="row"><button class="btn primary" data-next>다음 질문으로</button><button class="btn" data-record>연습 기록 보기</button></div>
    <p class="usage usage-live"></p>`;
  box.querySelector("[data-next]").onclick = nextQuestion;
  box.querySelector("[data-record]").onclick = showPractice;
  show("#p-result");
  renderUsage();
  box.scrollIntoView({ behavior: "smooth" });
}

async function showPractice() {
  try {
    const sess = await pickedSession();
    const report = await B.report(sess);
    const box = $("#p-result");
    box.innerHTML = `<h2>연습 기록 <span class="usage" style="font-weight:400">${esc(sess.meta.session)}</span></h2>
      ${sess.score.answers.length ? "" : '<p class="usage">아직 답한 질문이 없습니다.</p>'}
      <div class="row"><button class="btn" data-download>practice.md 내려받기</button></div>
      ${B.mode === "local" ? `<p class="usage">내 PC에 저장됨: ${esc(sess.id)}에 practice.md</p>` : ""}
      <pre class="md"></pre>`;
    box.querySelector("pre.md").textContent = report.practice;
    box.querySelector("[data-download]").onclick = () => download(`${sess.meta.session}-practice.md`, report.practice, "text/markdown;charset=utf-8");
    show("#p-result");
    box.scrollIntoView({ behavior: "smooth" });
  } catch (e) {
    $("#p-msg").textContent = e.message;
  }
}

// ---------- 기록·비교 ----------
async function renderHistory() {
  $("#history-where").textContent = B.mode === "local"
    ? `내 PC 면접 폴더: ${B.info.home}` : "이 브라우저에만 저장된 세션입니다. 서류 본문도 함께 들어 있으니 공용 PC에서는 다 쓴 뒤 지워 주세요.";
  hide("#history-view");
  let list;
  try { list = await B.list(); } catch (e) { $("#history").innerHTML = `<p class="empty">${esc(e.message)}</p>`; return; }
  state.list = list;
  if (!list.length) { $("#history").innerHTML = `<p class="empty">아직 면접 기록이 없습니다.</p>`; return; }
  const head = ["", "세션", ...S.ORDER.map((w) => S.INTERVIEWERS[w].name), "답한 수", ""];
  $("#history").innerHTML = `<div class="scroll"><table><tr>${head.map((h) => `<th>${esc(h)}</th>`).join("")}</tr>
    ${list.map((s, i) => `<tr><td><input type="checkbox" data-pick="${i}" aria-label="비교에 넣기"></td>
      <td>${esc(s.meta.session)}<div class="usage">${esc(s.meta.company || "회사 미지정")}</div></td>
      ${S.ORDER.map((w) => `<td>${fmt((s.score.document[w] || {}).total)}</td>`).join("")}
      <td>${s.score.answers.length}</td>
      <td><button class="btn small" data-open="${i}">열기</button> <button class="btn small" data-train="${i}">연습</button>
        ${B.mode === "browser" ? `<button class="btn small" data-json="${i}">JSON</button> <button class="btn small" data-remove="${i}">지우기</button>` : ""}</td></tr>`).join("")}
    </table></div><p class="usage">서류 점수는 10점 환산입니다. 같은 서류로 다시 심사하면 비교에서 점수 차이도 봅니다.</p>`;
  const at = (b, k) => list[Number(b.dataset[k])];
  for (const b of $$("[data-open]", $("#history"))) b.onclick = () => openSession(at(b, "open"));
  for (const b of $$("[data-train]", $("#history"))) b.onclick = () => selectTab("practice", at(b, "train").id);
  for (const b of $$("[data-json]", $("#history"))) {
    b.onclick = () => { const s = at(b, "json"); download(`${s.meta.session}.json`, JSON.stringify({ meta: s.meta, score: s.score, inputs: s.inputs }, null, 2) + "\n", "application/json"); };
  }
  for (const b of $$("[data-remove]", $("#history"))) {
    b.onclick = () => {
      const s = at(b, "remove");
      if (!confirm(`${s.meta.session} 세션(서류 본문·점수)을 이 브라우저에서 지울까요? 되돌릴 수 없습니다.`)) return;
      B.remove(s);
      renderHistory();
    };
  }
}

function compareChecked() {
  const picked = $$("[data-pick]:checked", $("#history")).map((c) => state.list[Number(c.dataset.pick)]);
  if (picked.length < 2) return alert("비교할 세션을 2개 이상 체크해 주세요.");
  picked.sort((a, b) => (a.meta.session < b.meta.session ? -1 : 1));
  const md = S.renderCompare(S.compare(picked.map((s) => [s.meta, s.score])));
  const view = $("#history-view");
  view.innerHTML = `<h2>회차 비교</h2><p class="note">${esc(S.NOTICE)}</p>
    <div class="row" style="margin-top:0"><button class="btn" data-download>compare.md 내려받기</button></div><pre class="md"></pre>`;
  view.querySelector("pre.md").textContent = md;
  view.querySelector("[data-download]").onclick = () => download("compare.md", md, "text/markdown;charset=utf-8");
  show("#history-view");
  view.scrollIntoView({ behavior: "smooth" });
}

async function openSession(entry) {
  const view = $("#history-view");
  let sess, report;
  try {
    sess = await B.get(entry);
    report = await B.report(sess);
  } catch (e) {
    view.innerHTML = `<p class="empty">${esc(e.message)}</p>`;
    show("#history-view");
    return;
  }
  const real = sess.score.real.flatMap((r) => r.questions.map((q) => `${r.date} · ${q.question}${q.matched ? ` (Q${q.matched}와 비슷함)` : ""}`));
  view.innerHTML = `<h2>${esc(sess.meta.session)} <span class="usage" style="font-weight:400">${esc(sess.meta.company || "회사 미지정")}</span></h2>
    <h3>실제 면접 질문 기록</h3>
    <p class="sub">실제 면접에서 받은 질문을 한 줄에 하나씩 적습니다. 모의 질문과 비슷했다면 끝에 <code>/ Q3</code>처럼 번호를 붙입니다. 붙인 것만 적중으로 셉니다.</p>
    ${real.length ? `<ul>${real.map((x) => `<li>${esc(x)}</li>`).join("")}</ul>` : ""}
    <div class="grid2"><div><label class="f" for="r-date">면접 날짜</label><input type="text" id="r-date" value="${today()}"></div></div>
    <label class="f" for="r-questions">받은 질문</label>
    <textarea id="r-questions" placeholder="재고 알림 정확도를 어떻게 쟀나요? / Q9&#10;우리 회사 앱을 써 봤나요?"></textarea>
    <div class="row"><button class="btn primary" data-real>기록</button><span class="usage" id="r-msg"></span></div>
    <h3>verdict.md</h3><div class="row" style="margin-top:0"><button class="btn small" data-dl="verdict">내려받기</button></div><pre class="md" data-md="verdict"></pre>
    <h3>practice.md</h3><div class="row" style="margin-top:0"><button class="btn small" data-dl="practice">내려받기</button></div><pre class="md" data-md="practice"></pre>`;
  for (const k of ["verdict", "practice"]) {
    view.querySelector(`[data-md=${k}]`).textContent = report[k];
    view.querySelector(`[data-dl=${k}]`).onclick = () => download(`${sess.meta.session}-${k}.md`, report[k], "text/markdown;charset=utf-8");
  }
  view.querySelector("[data-real]").onclick = async () => {
    const questions = [];
    for (const line of $("#r-questions").value.split("\n").map((l) => l.trim()).filter(Boolean)) {
      const m = line.match(/^(.*?)\s*\/\s*Q(\d+)\s*$/i);
      questions.push(m ? { question: m[1], matched: Number(m[2]), confirmed: true } : { question: line, matched: null });
    }
    const date = $("#r-date").value.trim();
    if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) { $("#r-msg").textContent = "날짜는 YYYY-MM-DD 꼴로 적어 주세요."; return; }
    try {
      await B.record(sess, "real", { date, questions });
      await renderHistory();
      await openSession(sess);
    } catch (e) {
      $("#r-msg").textContent = e.message;
    }
  };
  show("#history-view");
  view.scrollIntoView({ behavior: "smooth" });
}

function selectTab(name, pick) {
  for (const t of $$(".tab")) t.setAttribute("aria-selected", String(t.dataset.tab === name));
  for (const tab of ["panel", "practice", "history"]) $(`#tab-${tab}`).classList.toggle("hidden", name !== tab);
  if (name === "history") renderHistory();
  if (name === "practice") renderPracticeSelect(pick || (state.sess && state.sess.id));
}

// ---------- 서류 불러오기 ----------
function loadFile(kind) {
  const input = $("#file-pick");
  input.value = "";
  input.onchange = async () => {
    const file = input.files[0];
    if (!file) return;
    if (!/\.(md|txt)$/i.test(file.name)) return alert(".md·.txt만 읽습니다. 한글·워드·PDF는 본문을 복사해 붙여 넣어 주세요.");
    $(`#d-${kind}`).value = (await file.text()).replace(/^﻿/, "");
  };
  input.click();
}

// 내 PC 모드: 면접 폴더의 '서류' 폴더에서 파일 이름 규칙으로 고릅니다(saerok-interview docs와 같음).
async function loadDocs() {
  if (state.busy) return;
  const msg = $("#docs-msg");
  busy(true);
  try {
    const j = await B.api(`api/docs?company=${encodeURIComponent($("#f-company").value.trim())}`);
    if (!j.pick) {
      msg.textContent = `공고가 여러 회사입니다. 회사 칸에 하나를 적고 다시 눌러 주세요: ${j.choices.join(", ")}`;
      return;
    }
    for (const k of S.DOCS) $(`#d-${k}`).value = j.texts[k] || "";
    if (j.company) $("#f-company").value = j.company;
    const extra = [];
    if (j.unreadable.length) extra.push(`읽지 못한 파일(본문을 .md로 저장하면 함께 읽음): ${j.unreadable.join(", ")}`);
    if (j.unknown.length) extra.push(`이름 규칙 밖이라 뺀 파일: ${j.unknown.join(", ")}`);
    msg.textContent = `불러옴: ${Object.keys(j.pick).map((k) => S.DOC_NAMES[k]).join(", ")}${extra.length ? ` · ${extra.join(" · ")}` : ""}`;
  } catch (e) {
    if (/서류 폴더가 없습니다/.test(e.message) && confirm(`${e.message}\n\n지금 서류 폴더와 양식을 만들까요?`)) {
      try {
        const j = await B.api("api/docs/init", {});
        msg.textContent = `서류 폴더를 만들었습니다: ${j.folder}. 양식(${j.created.join(", ") || "이미 있음"})을 채운 뒤 다시 눌러 주세요.`;
      } catch (e2) { msg.textContent = e2.message; }
    } else {
      msg.textContent = e.message;
    }
  } finally {
    busy(false);
  }
}

// ---------- 설정 ----------
function renderMode() {
  $("#mode").innerHTML = B.mode === "local"
    ? `<b>내 PC 모드</b> · 기록은 <code>${esc(B.info.home)}</code>에만, Claude는 ` +
      (B.info.engine === "subscription" ? "내 구독(Claude Code)으로 부릅니다" : `API 키로 부릅니다(키: ${esc(B.info.key_from || "아직 없음")})`)
    : `<b>브라우저 모드</b> · 키와 서류·기록은 이 브라우저에만 저장되고, Claude는 Anthropic에 바로 연결합니다. ` +
      `내 PC 면접 폴더에 저장하려면 터미널에서 <code>saerok-interview</code>를 실행하세요.`;
  $("#docs-row").classList.toggle("hidden", B.mode !== "local");
}

function openSettings() {
  const p = prefs();
  for (const id of ["#model-panel", "#model-practice"]) {
    $(id).innerHTML = MODELS.map(([v, n]) => `<option value="${v}">${n}</option>`).join("");
  }
  $("#model-panel").value = p.panel;
  $("#model-practice").value = p.practice;
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
      ? "구독 방식은 이 PC에 로그인한 Claude Code(claude 명령)로 돌리고, 구독 사용량에서 차감됩니다."
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
  local.set(PREFS, { panel: $("#model-panel").value, practice: $("#model-practice").value });
  try {
    if (B.mode === "local") {
      const picked = $('input[name="engine"]:checked');
      if (picked && picked.value !== B.info.engine) {
        const j = await B.api("api/engine", { engine: picked.value });
        B.info.engine = j.engine;
        renderMode();
      }
      const key = $("#key-local-input").value.trim();
      if (key) {
        const j = await B.api("api/key", { key });
        Object.assign(B.info, { key: j.key, key_from: j.key_from });
        renderMode();
      }
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

async function fillChoices() {
  try {
    const data = await loadTerms();
    $("#f-industry").innerHTML += data.industries.map((i) => `<option value="${esc(i.id)}">${esc(i.name)}</option>`).join("");
    $("#f-role").innerHTML += data.roles.map((r) => `<option value="${esc(r.id)}">${esc(r.name)}</option>`).join("");
  } catch (e) {
    $("#f-industry").disabled = $("#f-role").disabled = true;
  }
}

async function main() {
  await B.init();
  renderMode();
  fillChoices();
  $("#start").onclick = start;
  $("#load-docs").onclick = loadDocs;
  for (const b of $$("[data-load]")) b.onclick = () => loadFile(b.dataset.load);
  $("#p-next").onclick = nextQuestion;
  $("#p-send").onclick = sendAnswer;
  $("#p-stop").onclick = stopQuestion;
  $("#p-record").onclick = showPractice;
  $("#compare").onclick = compareChecked;
  $("#open-settings").onclick = openSettings;
  $("#save-settings").onclick = saveSettings;
  $("#forget-key").onclick = forgetKey;
  $("#close-settings").onclick = () => $("#settings").close();
  for (const t of $$(".tab")) t.onclick = () => selectTab(t.dataset.tab);
}

main();
