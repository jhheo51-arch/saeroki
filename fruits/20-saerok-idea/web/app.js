/* 새록 심사단 화면. 진행 순서는 skills/judge/SKILL.md와 같고, 판정·검사·verdict.md는 idea-core.js(= saerok_idea)가 냅니다.
   브라우저 모드: 키·기록은 이 브라우저에만, Claude는 api.anthropic.com을 바로 부릅니다.
   내 PC 모드(saerok-idea): 기록은 ~/.saerok/idea, 키는 자격 증명 관리자, Claude 호출은 내 PC 서버가 넘깁니다. */
"use strict";

const S = window.SaerokIdea;
const $ = (sel, el = document) => el.querySelector(sel);
const $$ = (sel, el = document) => Array.from(el.querySelectorAll(sel));
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const safeUrl = (u) => (/^https?:\/\//i.test(String(u || "")) ? String(u) : "#");
const pad = (n) => String(n).padStart(2, "0");
const today = () => { const d = new Date(); return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`; };
const stamp = () => { const d = new Date(); return `${today()} ${pad(d.getHours())}:${pad(d.getMinutes())}`; };

const MODELS = [
  ["claude-sonnet-5-5", "Claude Sonnet 5.5"],
  ["claude-opus-5-5", "Claude Opus 5.5"],
  ["claude-haiku-5-5", "Claude Haiku 5.5"],
];
const AGENT_FILES = { user_value: "user-value", business: "business", feasibility: "feasibility", panel: "panel" };
const PREFS = "saerok-idea:prefs";
const KEY = "saerok-idea:key";
const RECORDS = "saerok-idea:records";

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
const prefs = () => Object.assign({ judge: "claude-sonnet-5-5", lead: "claude-sonnet-5-5" }, local.get(PREFS, {}));
const browserKey = () => local.get(KEY, "", sessionStorage) || local.get(KEY, "");

// ---------- 백엔드: 브라우저 모드 / 내 PC 모드 ----------
const API_HEADERS = { "Content-Type": "application/json", "X-Saerok-Idea": "1" };

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

  // 기록. run = {id, slug, run, result}. 내 PC 모드의 id는 기록 폴더 경로입니다.
  records() { return local.get(RECORDS, {}); },
  saveRecords(recs) {
    if (!local.set(RECORDS, recs)) throw new Error("브라우저 저장 공간에 쓰지 못했습니다. 기록 탭에서 오래된 기록을 지우거나 내려받아 주세요.");
  },

  async create(idea, from) {
    if (this.mode === "local") {
      const body = from ? { idea, from: { folder: from.run.id, direction: from.direction } } : { idea };
      const j = await this.api("api/new", body);
      return { id: j.folder, slug: j.slug, run: j.run, result: j.result };
    }
    const recs = this.records();
    const slug = from ? from.run.slug : S.slug(idea.line);
    const date = today();
    let run = date, n = 2;
    while (recs[slug] && recs[slug][run]) run = `${date}-${n++}`;
    const origin = from ? { verdict: `${from.run.slug}/${from.run.run}/verdict.md`, direction: from.direction || null } : null;
    const result = S.newResult(idea, date, origin);
    recs[slug] = Object.assign(recs[slug] || {}, { [run]: result });
    this.saveRecords(recs);
    return { id: `${slug}/${run}`, slug, run, result };
  },

  async record(run, part, data) {
    if (this.mode === "local") await this.api("api/record", { folder: run.id, part, data });
    const clean = S.record(run.result, part, data, stamp());
    if (this.mode === "browser") {
      const recs = this.records();
      recs[run.slug] = Object.assign(recs[run.slug] || {}, { [run.run]: run.result });
      this.saveRecords(recs);
    }
    return clean;
  },

  async report(run) {
    if (this.mode === "local") {
      const j = await this.api("api/report", { folder: run.id });
      run.result = j.result;
      return { markdown: j.markdown, path: j.path };
    }
    const path = `${run.slug}/${run.run}/verdict.md`;
    return { markdown: S.render(run.result, run.run, path), path };
  },

  async history() {
    if (this.mode === "local") {
      const ideas = await this.api("api/runs");
      return ideas.map((i) => ({ slug: i.slug, runs: i.runs.map((r) => ({ id: r.folder, slug: i.slug, run: r.run, result: r.result })) }));
    }
    const recs = this.records();
    return Object.keys(recs).map((slug) => ({
      slug,
      runs: Object.keys(recs[slug]).sort().map((run) => ({ id: `${slug}/${run}`, slug, run, result: recs[slug][run] })),
    })).filter((i) => i.runs.length).sort((a, b) => (last(b.runs).run > last(a.runs).run ? 1 : -1));
  },

  remove(run) {
    const recs = this.records();
    if (recs[run.slug]) delete recs[run.slug][run.run];
    if (recs[run.slug] && !Object.keys(recs[run.slug]).length) delete recs[run.slug];
    this.saveRecords(recs);
  },
};
const last = (a) => a[a.length - 1];

// ---------- Claude 호출 ----------
const usage = { input: 0, output: 0, search: 0, calls: 0 };

async function claude({ system, user, model, maxTokens = 4000, search = 0 }) {
  const body = { model, max_tokens: maxTokens, system, messages: [{ role: "user", content: user }] };
  if (search) body.tools = [{ type: "web_search_20250305", name: "web_search", max_uses: search }];
  const content = [];
  for (let turn = 0; turn < 4; turn++) {
    const r = await B.send(body);
    usage.calls += 1;
    usage.input += (r.usage && r.usage.input_tokens) || 0;
    usage.output += (r.usage && r.usage.output_tokens) || 0;
    usage.search += (r.usage && r.usage.server_tool_use && r.usage.server_tool_use.web_search_requests) || 0;
    content.push(...(r.content || []));
    if (r.stop_reason !== "pause_turn") break;
    // 검색이 길어 잠깐 멈추면, 받은 내용을 그대로 돌려줘 이어 가게 합니다.
    body.messages = [{ role: "user", content: user }, { role: "assistant", content: content.slice() }];
  }
  renderUsage();
  return { text: content.filter((c) => c.type === "text").map((c) => c.text).join(""), content };
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

// 형식 검사에 걸리면 오류 문장을 붙여 한 번만 다시 묻습니다(스킬 2단계와 같음).
async function askJSON(opts, check) {
  let user = opts.user, lastError;
  for (let attempt = 0; attempt < 2; attempt++) {
    const reply = await claude({ ...opts, user });
    try {
      const data = parseJSON(reply.text);
      return { data, checked: check ? check(data) : data, reply };
    } catch (e) {
      lastError = e;
      user = `${opts.user}\n\n앞선 답이 형식 검사에서 걸렸습니다: ${e.message}\n설명 없이 JSON 하나만 다시 주세요.`;
    }
  }
  throw lastError;
}

const agentCache = {};
async function agentPrompt(name) {
  if (!agentCache[name]) {
    const r = await fetch(`agents/${AGENT_FILES[name]}.md`);
    if (!r.ok) throw new Error(`심사위원 기준 파일(agents/${AGENT_FILES[name]}.md)을 읽지 못했습니다.`);
    agentCache[name] = (await r.text()).replace(/^---[\s\S]*?\n---\s*\n/, "").trim();
  }
  return agentCache[name];
}

const ideaBlock = (idea) => Object.keys(S.FIELDS).map((k) => `- ${S.FIELDS[k]}: ${idea[k]}`).join("\n");

// ---------- 진행자 지시(스킬 3·4·6단계를 화면에 맞게 옮긴 것) ----------
const LEAD = "너는 '새록 심사단'의 진행자다. 존댓말 한국어로 쓰고, 숫자(시장 규모·사용자 수·가격)를 지어내지 않는다. " +
  "설명 없이 요청한 JSON 하나만 돌려준다.";

const PROMPT_FIELDS = LEAD + "\n아이디어 한 줄에서 4칸(무엇을·누구에게·어떻게 돈을 버는지·왜 지금)을 읽는다. 한 줄에 분명히 적힌 것만 옮기고, " +
  "적혀 있지 않은 칸은 빈 문자열로 둔다. 짐작해 채우지 않는다.\n" +
  '답 형식: {"what": "", "who": "", "money": "", "why_now": ""}';

const PROMPT_PLAN = LEAD + `
심사위원의 걸리는 점을 보고 핵심 가정 3개를 이 아이디어에 맞는 문장으로 쓰고, 검증할 검색어를 만든다.
- problem: 문제가 실제로 있다 / alternative: 사람들이 지금 다른 방법으로 해결한다 / pay: 돈이나 시간을 낼 것이다
- 심사위원 걸리는 점에서 가장 많이 걸린 지점을 우선한다.
- 가정마다 반박 쪽 검색어(counter_queries) 1~2개를 먼저, 받침 쪽 검색어(support_queries) 1~2개를 만든다.
- 경쟁 서비스 검색어(competitor_queries) 2~4개를 만든다.
- 검색어에는 아이디어 원문이나 이 아이디어만의 표현을 넣지 않고 일반 낱말로 쓴다. 예: 아이디어가 "1인 카페 사장님용 재고 알림"이면 "소규모 카페 재고 관리 어려움", "카페 재고 관리 앱 후기".
답 형식:
{"assumptions": [{"key": "problem", "statement": "…", "counter_queries": ["…"], "support_queries": ["…"]},
 {"key": "alternative", …}, {"key": "pay", …}], "competitor_queries": ["…"]}`;

const PROMPT_ASSUMPTION = LEAD + `
web_search로 가정 하나를 검증한다.
- 사용자가 확인한 검색어만, 적힌 그대로, 적힌 순서(반박 쪽 먼저)로 쓴다. 검색어를 바꾸거나 더하지 않는다.
- 검색 결과에 실제로 나온 페이지만 근거로 쓰고, url은 검색 결과의 url을 그대로 옮긴다. 근거마다 이 가정을 받치는지(받침) 반박하는지(반박)와 한 줄 요약을 쓴다.
- 반박 근거와 받침 근거가 둘 다 있으면 둘 다 적는다. 근거가 없으면 status를 "확인 못 함"으로 두고 지어내지 않는다.
- user_check에는 웹으로 확인할 수 없는 것(실제 인터뷰, 작은 판매 시험 등)만 적는다.
검색을 마친 뒤 마지막에 JSON 하나만 쓴다:
{"status": "받침|반박|확인 못 함", "evidence": [{"kind": "받침|반박", "title": "…", "url": "https://…", "note": "…"}], "user_check": "…"}`;

const PROMPT_COMPETITORS = LEAD + `
web_search로 경쟁 서비스를 찾는다.
- 사용자가 확인한 검색어만, 적힌 그대로 쓴다. 검색어를 바꾸거나 더하지 않는다.
- 검색 결과에 실제로 나온 서비스만 적고, url은 검색 결과의 url을 그대로 옮긴다.
- diff에는 이 아이디어와의 차이를 쓴다. 범용 AI 챗봇으로 충분히 되는지도 따져 적는다.
- 사용자가 알려 준 경쟁 서비스는 user_added를 true로 두고 받은 이름·링크를 그대로 쓰며 diff만 채운다.
검색을 마친 뒤 마지막에 JSON 하나만 쓴다:
{"items": [{"name": "…", "url": "https://…", "diff": "…", "user_added": false}]}`;

const PROMPT_DIRECTIONS = LEAD + `
판정에 맞춰 다듬은 방향 2~3개를 만들고 하나를 추천한다. 판정은 바꾸거나 덧붙이지 않는다.
- 진행: 첫 버전 범위를 좁힌 안
- 조건부: 약점을 메운 변형(대상 좁히기·범위 줄이기·수익 방식 바꾸기)
- 보류·판단 보류(정보 부족): 방향 전환안, 또는 미정 칸을 채운 안
방향마다 새 한 줄과 4칸, 바꾼 것, 해결하는 심사 지적·반박된 가정(1~5개), 사용자가 직접 확인할 일을 쓴다.
원래 입력에서 바꾸지 않은 칸은 글자 그대로 옮긴다. 미정 칸을 채웠다면 그 내용을 사용자가 확인할 일에 적는다.
답 형식:
{"directions": [{"title": "…", "idea": {"line": "…", "what": "…", "who": "…", "money": "…", "why_now": "…"},
  "changed": "…", "addresses": ["…"], "user_checks": ["…"]}], "recommended": 1, "why": "추천 이유"}`;

// ---------- 화면 상태 ----------
const state = { run: null, from: null, opts: null, plan: null, found: {}, sources: {}, markdown: "", busy: false };

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
  $$("#start, #search, #read-fields").forEach((b) => { b.disabled = on; });
}
function renderUsage() {
  $$(".usage-live").forEach((el) => {
    el.textContent = `이번 화면 사용량: Claude 호출 ${usage.calls}번 · 입력 토큰 ${usage.input.toLocaleString()} · 출력 토큰 ${usage.output.toLocaleString()} · 웹 검색 ${usage.search}번`;
  });
}

function readIdea() {
  const idea = { line: $("#f-line").value };
  for (const k of ["what", "who", "money", "why_now"]) idea[k] = $(`#f-${k}`).value;
  return idea;
}
function fillIdea(idea) {
  $("#f-line").value = idea.line || "";
  for (const k of ["what", "who", "money", "why_now"]) $(`#f-${k}`).value = idea[k] === S.UNKNOWN ? "" : (idea[k] || "");
}

function readOptions() {
  const money = {};
  for (const [key, id] of [["price", "#m-price"], ["unit_cost", "#m-unit"], ["fixed_cost", "#m-fixed"]]) {
    const raw = $(id).value.trim();
    if (raw === "") continue;
    const v = Number(raw);
    if (!Number.isFinite(v) || v < 0) throw new Error(`${S.MONEY_NAMES[key]}은 0 이상의 숫자여야 합니다.`);
    money[key] = { value: v, source: "사용자 입력" };
  }
  const rivals = [];
  for (const line of $("#f-rivals").value.split("\n").map((l) => l.trim()).filter(Boolean)) {
    const m = line.match(/^(.*?)\s*(https?:\/\/\S+)\s*$/);
    if (!m || !m[1]) throw new Error(`경쟁 서비스는 '이름 https://링크' 꼴로 적어 주세요: ${line}`);
    rivals.push({ name: m[1], url: m[2] });
  }
  return { money, rivals, panel: Number($("input[name=panel]:checked").value) };
}

// ---------- 1. 입력 ----------
async function readFields() {
  const line = $("#f-line").value.trim();
  if (!line) return alert("아이디어 한 줄을 먼저 적어 주세요.");
  busy(true);
  try {
    const { checked } = await askJSON({ system: PROMPT_FIELDS, user: `아이디어 한 줄: ${line}`, model: prefs().lead, maxTokens: 800 },
      (d) => { for (const k of ["what", "who", "money", "why_now"]) if (typeof d[k] !== "string") throw new Error(`${k}가 문자열이 아닙니다.`); return d; });
    for (const k of ["what", "who", "money", "why_now"]) if (!$(`#f-${k}`).value.trim()) $(`#f-${k}`).value = checked[k].trim();
  } catch (e) {
    alert(e.message);
  } finally {
    busy(false);
  }
}

async function start() {
  if (state.busy) return;
  let idea, opts;
  try {
    idea = S.cleanIdea(readIdea());
    opts = readOptions();
  } catch (e) {
    return alert(e.message);
  }
  if (B.mode === "browser" && !browserKey()) {
    $("#settings").showModal();
    return;
  }
  busy(true);
  for (const id of ["#judges", "#log-judges", "#queries", "#log-queries", "#log-research"]) $(id).innerHTML = "";
  hide("#step-queries"); hide("#step-research"); hide("#step-result");
  Object.assign(state, { opts, plan: null, found: {}, sources: {}, markdown: "" });
  try {
    state.run = await B.create(idea, state.from);
    cancelFrom();  // 다음 새 심사가 같은 방향 기록으로 이어지지 않게 합니다.
    show("#step-judges");
    log("#log-judges", B.mode === "local" ? `기록 폴더: ${state.run.id}` : `브라우저 기록: ${state.run.id}`);
    $("#step-judges").scrollIntoView({ behavior: "smooth" });
    await runJudges();
  } catch (e) {
    log("#log-judges", e.message, "err");
  } finally {
    busy(false);
  }
}

// ---------- 2. 심사위원 ----------
function judgeCard(k, j, pending) {
  const meta = S.JUDGES[k];
  if (pending) return `<div class="judge" id="j-${k}"><div class="who">${esc(meta.name)}</div><div class="q">${esc(meta.question)}</div><p><span class="spin"></span> 심사 중</p></div>`;
  if (!j) return `<div class="judge" id="j-${k}"><div class="who">${esc(meta.name)}</div><div class="q">${esc(meta.question)}</div><p>결과 없음</p></div>`;
  return `<div class="judge" id="j-${k}"><div class="who">${esc(meta.name)}</div><div class="q">${esc(meta.question)}</div>
    <div class="score">${j.score}<small style="font-size:14px;color:var(--muted)">/5</small> <span class="badge v-${esc(j.vote)}">${esc(j.vote)}</span></div>
    <div class="lbl">이유</div><ul>${j.reasons.map((r) => `<li>${esc(r)}</li>`).join("")}</ul>
    <div class="lbl">걸리는 점</div><ul>${j.concerns.map((r) => `<li>${esc(r)}</li>`).join("")}</ul></div>`;
}

async function runJudges() {
  const run = state.run;
  $("#judges").innerHTML = S.ORDER.map((k) => judgeCard(k, run.result.judges[k], !run.result.judges[k])).join("");
  const todo = S.ORDER.filter((k) => !run.result.judges[k]);
  const user = `아이디어:\n${ideaBlock(run.result.idea)}\n\n에이전트 파일의 기준표와 답 형식대로 JSON 하나만 돌려주세요.`;
  const results = await Promise.allSettled(todo.map(async (k) => {
    const system = await agentPrompt(k);
    const { data } = await askJSON({ system, user, model: prefs().judge, maxTokens: 1500 },
      (d) => S.checkJudge(Object.assign(d, { judge: k })));
    await B.record(run, "judge", data);
    $(`#j-${k}`).outerHTML = judgeCard(k, run.result.judges[k]);
  }));
  const failed = results.map((r, i) => [todo[i], r]).filter(([, r]) => r.status === "rejected");
  for (const [k, r] of failed) {
    $(`#j-${k}`).outerHTML = judgeCard(k, null);
    log("#log-judges", `${S.JUDGES[k].name}: ${r.reason.message}`, "err");
  }
  if (failed.length) return retryButton("#log-judges", runJudges);
  log("#log-judges", "심사위원 3명이 모두 답했습니다.");
  await planQueries();
}

function retryButton(logId, fn) {
  const li = document.createElement("li");
  const b = document.createElement("button");
  b.className = "btn small";
  b.textContent = "이 단계 다시 시도";
  b.onclick = async () => { li.remove(); busy(true); try { await fn(); } catch (e) { log(logId, e.message, "err"); retryButton(logId, fn); } finally { busy(false); } };
  li.appendChild(b);
  $(logId).appendChild(li);
}

// ---------- 3. 검색어 확인 ----------
function checkPlan(d) {
  const items = d.assumptions || [];
  for (const key of Object.keys(S.ASSUMPTIONS)) {
    const a = items.find((x) => x && x.key === key);
    if (!a || typeof a.statement !== "string" || !a.statement.trim()) throw new Error(`${key} 가정 문장이 없습니다.`);
    for (const f of ["counter_queries", "support_queries"]) {
      if (!Array.isArray(a[f]) || !a[f].length || a[f].length > 2) throw new Error(`${key}.${f}는 1~2개여야 합니다.`);
    }
  }
  if (!Array.isArray(d.competitor_queries) || !d.competitor_queries.length || d.competitor_queries.length > 4) {
    throw new Error("competitor_queries는 1~4개여야 합니다.");
  }
  return d;
}

async function planQueries() {
  show("#step-queries");
  const run = state.run;
  const concerns = S.ORDER.map((k) => `- ${S.JUDGES[k].name}: ${run.result.judges[k].concerns.join(" / ")}`).join("\n");
  log("#log-queries", "핵심 가정 3개와 검색어를 만드는 중입니다…", "warn");
  const { checked } = await askJSON({ system: PROMPT_PLAN, user: `아이디어:\n${ideaBlock(run.result.idea)}\n\n심사위원 걸리는 점:\n${concerns}`,
    model: prefs().lead, maxTokens: 2000 }, checkPlan);
  state.plan = checked;
  renderQueries();
  $("#step-queries").scrollIntoView({ behavior: "smooth" });
}

function queryLine(group, kind, value) {
  return `<div class="q-line" data-group="${group}" data-kind="${kind}"><input type="checkbox" checked aria-label="이 검색어 쓰기">
    <span class="q-kind">${kind === "counter" ? "반박" : kind === "support" ? "받침" : "경쟁"}</span>
    <input type="text" value="${esc(value)}" maxlength="80"></div>`;
}

function renderQueries() {
  const p = state.plan;
  let html = "";
  for (const key of Object.keys(S.ASSUMPTIONS)) {
    const a = p.assumptions.find((x) => x.key === key);
    html += `<div class="q-group"><div class="title">${esc(S.ASSUMPTIONS[key])}</div>
      <label class="f" for="st-${key}">이 아이디어에서의 가정</label><input type="text" id="st-${key}" value="${esc(a.statement)}">
      ${a.counter_queries.map((q) => queryLine(key, "counter", q)).join("")}${a.support_queries.map((q) => queryLine(key, "support", q)).join("")}</div>`;
  }
  html += `<div class="q-group"><div class="title">경쟁 서비스</div>${p.competitor_queries.map((q) => queryLine("rivals", "rival", q)).join("")}
    ${state.opts.rivals.length ? `<p class="usage">내가 알려 준 경쟁 서비스 ${state.opts.rivals.length}개도 함께 정리합니다(검색어로 보내지 않음).</p>` : ""}</div>`;
  $("#queries").innerHTML = html;
  $("#queries").oninput = updateEstimate;
  updateEstimate();
}

function chosenQueries() {
  const out = { rivals: [] };
  for (const key of Object.keys(S.ASSUMPTIONS)) out[key] = { counter: [], support: [] };
  for (const line of $$(".q-line", $("#queries"))) {
    const text = $("input[type=text]", line).value.trim();
    if (!$("input[type=checkbox]", line).checked || !text) continue;
    if (line.dataset.group === "rivals") out.rivals.push(text);
    else out[line.dataset.group][line.dataset.kind].push(text);
  }
  return out;
}

function updateEstimate() {
  const q = chosenQueries();
  const searches = q.rivals.length + Object.keys(S.ASSUMPTIONS).reduce((n, k) => n + q[k].counter.length + q[k].support.length, 0);
  const calls = Object.keys(S.ASSUMPTIONS).filter((k) => q[k].counter.length + q[k].support.length).length +
    (q.rivals.length || state.opts.rivals.length ? 1 : 0) + 2;
  $("#estimate").innerHTML = `남은 예상 사용량: Claude 호출 약 ${calls}번(가정 검증·경쟁 조사·패널 ${state.opts.panel}명·방향), 웹 검색 최대 ${searches}번. ` +
    `<span class="usage-live"></span>`;
  renderUsage();
}

// ---------- 4. 가정 검증·경쟁·패널 ----------
const norm = (u) => { try { const x = new URL(u); return (x.host.toLowerCase() + x.pathname.replace(/\/+$/, "") + x.search); } catch (e) { return ""; } };

// 응답에서 실제로 보낸 검색어와 검색 결과 링크를 모읍니다.
function searchTrace(content) {
  const queries = [], urls = new Map();
  for (const c of content) {
    if (c.type === "server_tool_use" && c.name === "web_search" && c.input) queries.push(String(c.input.query || ""));
    if (c.type === "web_search_tool_result" && Array.isArray(c.content)) {
      for (const r of c.content) if (r.url) urls.set(norm(r.url), { url: r.url, title: r.title || "" });
    }
  }
  return { queries, urls };
}

function warnExtraQueries(label, trace, allowed) {
  const extra = trace.queries.filter((q) => !allowed.includes(q.trim()));
  if (extra.length) log("#log-research", `${label}: 확인하지 않은 검색어 ${extra.length}개가 나갔습니다(${extra.join(", ")}). 다음 심사에서는 검색어를 더 줄여 주세요.`, "warn");
}

async function verifyAssumption(key, statement, q) {
  const all = [...q.counter, ...q.support];
  const counterQuery = q.counter.length ? q.counter.join(" / ") : "(반박 검색어를 빼서 찾지 않음)";
  if (!all.length) {
    log("#log-research", `${S.ASSUMPTIONS[key]}: 검색어가 없어 찾지 않았습니다(확인 못 함).`, "warn");
    return { key, statement, status: "확인 못 함", evidence: [], counter_query: counterQuery, user_check: "" };
  }
  const user = `아이디어:\n${ideaBlock(state.run.result.idea)}\n\n검증할 가정(${S.ASSUMPTIONS[key]}): ${statement}\n\n쓸 검색어(이 순서대로):\n` +
    all.map((x, i) => `${i + 1}. ${x}${i < q.counter.length ? " (반박 쪽)" : " (받침 쪽)"}`).join("\n");
  const { data, reply } = await askJSON({ system: PROMPT_ASSUMPTION, user, model: prefs().lead, maxTokens: 4000, search: all.length },
    (d) => { if (!S.STATUSES.includes(d.status)) throw new Error(`status는 ${S.STATUSES.join("·")} 중 하나여야 합니다.`); return d; });
  const trace = searchTrace(reply.content);
  warnExtraQueries(S.ASSUMPTIONS[key], trace, all);
  // 검색 결과에 없는 링크는 근거로 남기지 않습니다(지어낸 링크 방지).
  let dropped = 0;
  const evidence = [];
  for (const e of Array.isArray(data.evidence) ? data.evidence : []) {
    const hit = trace.urls.get(norm(e && e.url));
    if (!hit || !S.EVIDENCE_KINDS.includes(e.kind)) { dropped += 1; continue; }
    evidence.push({ kind: e.kind, title: String(e.title || hit.title || hit.url).trim(), url: hit.url, checked: today(), note: String(e.note || "").trim() });
  }
  let status = data.status;
  if (S.EVIDENCE_KINDS.includes(status) && !evidence.some((e) => e.kind === status)) status = "확인 못 함";
  if (dropped) log("#log-research", `${S.ASSUMPTIONS[key]}: 검색 결과에 없는 링크 ${dropped}개를 근거에서 뺐습니다.`, "warn");
  log("#log-research", `${S.ASSUMPTIONS[key]}: ${status} (근거 ${evidence.length}개)`);
  return { key, statement, status, evidence, counter_query: counterQuery, user_check: String(data.user_check || "").trim() };
}

async function researchCompetitors(queries) {
  const rivals = state.opts.rivals;
  if (!queries.length && !rivals.length) {
    log("#log-research", "경쟁 조사: 검색어가 없어 조사하지 않았습니다.", "warn");
    return null;
  }
  const user = `아이디어:\n${ideaBlock(state.run.result.idea)}\n\n쓸 검색어:\n${queries.map((x, i) => `${i + 1}. ${x}`).join("\n") || "(없음: 검색하지 말 것)"}` +
    `\n\n사용자가 알려 준 경쟁 서비스:\n${rivals.map((r) => `- ${r.name} ${r.url}`).join("\n") || "(없음)"}`;
  const { data, reply } = await askJSON({ system: PROMPT_COMPETITORS, user, model: prefs().lead, maxTokens: 4000, search: queries.length },
    (d) => { if (!Array.isArray(d.items)) throw new Error("items가 배열이어야 합니다."); return d; });
  const trace = searchTrace(reply.content);
  warnExtraQueries("경쟁 조사", trace, queries);
  const items = [];
  let dropped = 0;
  for (const r of rivals) {
    const said = data.items.find((x) => x && norm(x.url) === norm(r.url));
    items.push({ name: r.name, url: r.url, checked: today(), user_added: true, diff: String((said && said.diff) || "사용자가 알려 준 서비스(차이 미정)").trim() });
  }
  for (const c of data.items) {
    if (!c || c.user_added || rivals.some((r) => norm(r.url) === norm(c.url))) continue;
    const hit = trace.urls.get(norm(c.url));
    if (!hit || !String(c.name || "").trim() || !String(c.diff || "").trim()) { dropped += 1; continue; }
    items.push({ name: String(c.name).trim(), url: hit.url, checked: today(), diff: String(c.diff).trim(), user_added: false });
  }
  if (dropped) log("#log-research", `경쟁 조사: 검색 결과에 없거나 빈칸인 항목 ${dropped}개를 뺐습니다.`, "warn");
  log("#log-research", `경쟁 조사: ${items.length}개`);
  return { queries: queries.length ? queries : ["(검색 안 함: 사용자가 알려 준 서비스만)"], checked: today(), items };
}

async function runPanel() {
  const system = await agentPrompt("panel");
  const size = state.opts.panel;
  const { data } = await askJSON({ system, user: `아이디어:\n${ideaBlock(state.run.result.idea)}\n\n패널 규모: ${size}명`, model: prefs().judge, maxTokens: 2500 },
    (d) => S.checkPanel(Object.assign(d, { size })));
  log("#log-research", `가상 패널 ${size}명: 반대 이유 ${(data.against || []).length}개`);
  return data;
}

async function startResearch() {
  if (state.busy) return;
  const q = chosenQueries();
  const statements = {};
  for (const key of Object.keys(S.ASSUMPTIONS)) {
    statements[key] = $(`#st-${key}`).value.trim();
    if (!statements[key]) return alert(`'${S.ASSUMPTIONS[key]}' 가정 문장을 비울 수 없습니다.`);
  }
  state.queries = q;
  state.statements = statements;
  busy(true);
  show("#step-research");
  $("#step-research").scrollIntoView({ behavior: "smooth" });
  try {
    await research();
  } catch (e) {
    log("#log-research", e.message, "err");
    retryButton("#log-research", research);
  } finally {
    busy(false);
  }
}

// 이미 끝난 부분은 건너뛰므로 '다시 시도'에도 그대로 씁니다.
async function research() {
  const run = state.run, q = state.queries;
  const jobs = [];
  for (const key of Object.keys(S.ASSUMPTIONS)) {
    if (!state.found[key]) jobs.push(verifyAssumption(key, state.statements[key], q[key]).then((a) => { state.found[key] = a; }));
  }
  if (!state.sources.competitors) {
    jobs.push(researchCompetitors(q.rivals).then(async (c) => { if (c) await B.record(run, "competitors", c); state.sources.competitors = true; }));
  }
  if (!run.result.panel) jobs.push(runPanel().then((p) => B.record(run, "panel", p)));
  if (!run.result.money && Object.keys(state.opts.money).length) jobs.push(B.record(run, "money", state.opts.money));
  const results = await Promise.allSettled(jobs);
  const errors = results.filter((r) => r.status === "rejected").map((r) => r.reason.message);
  if (Object.keys(state.found).length === 3 && !run.result.assumptions) {
    await B.record(run, "assumptions", Object.keys(S.ASSUMPTIONS).map((k) => state.found[k]));
  }
  if (errors.length) throw new Error(errors.join(" / "));
  await finish();
}

// ---------- 5. 판정·방향 ----------
async function finish() {
  const run = state.run;
  const decided = S.decideResult(run.result);
  log("#log-research", `판정: ${decided.verdict} (규칙으로 계산, AI가 정하지 않음)`);
  if (!run.result.directions) {
    log("#log-research", "다듬은 방향을 만드는 중입니다…", "warn");
    const r = run.result;
    const summary = [
      `아이디어:\n${ideaBlock(r.idea)}`,
      `판정: ${decided.verdict}\n${decided.steps.map((s) => `- ${s}`).join("\n")}`,
      `심사위원:\n${S.ORDER.map((k) => `- ${S.JUDGES[k].name} ${r.judges[k].score}/5 ${r.judges[k].vote}. 걸리는 점: ${r.judges[k].concerns.join(" / ")}`).join("\n")}`,
      `가정 검증:\n${r.assumptions.map((a) => `- ${S.ASSUMPTIONS[a.key]}(${a.statement}): ${a.status}${a.evidence.map((e) => `; ${e.kind}: ${e.note || e.title}`).join("")}`).join("\n")}`,
      `가상 패널 반대 이유(AI 시뮬레이션): ${(r.panel && r.panel.against.map((x) => x.reason).join(" / ")) || "없음"}`,
      `경쟁 서비스: ${(r.competitors && r.competitors.items.map((c) => `${c.name}(${c.diff})`).join(" / ")) || "조사 안 함 또는 못 찾음"}`,
    ].join("\n\n");
    const { data } = await askJSON({ system: PROMPT_DIRECTIONS, user: summary, model: prefs().lead, maxTokens: 4000 }, S.checkDirections);
    await B.record(run, "directions", data);
  }
  const report = await B.report(run);
  state.markdown = report.markdown;
  log("#log-research", "verdict.md를 만들었습니다.");
  $("#step-result").innerHTML = resultHTML(run, report);
  bindResult($("#step-result"), run, report);
  show("#step-result");
  $("#step-result").scrollIntoView({ behavior: "smooth" });
}

function verdictClass(v) { return ["진행", "조건부", "보류"].includes(v) ? `v-${v}` : "v-none"; }
function statusClass(s) { return s === "확인 못 함" ? "s-확인" : `s-${s}`; }

function resultHTML(run, report) {
  const r = run.result;
  let decided;
  try { decided = S.decideResult(r); } catch (e) { decided = { verdict: "미완료", steps: [e.message] }; }
  const parts = [];
  parts.push(`<h2>🌸 판정 <span class="usage" style="font-weight:400">${esc(run.slug)} / ${esc(run.run)}</span></h2>
    <p class="note">${esc(S.NOTICE)}</p>
    ${r.from ? `<p class="sub">다시 심사: ${esc(r.from.verdict)}${r.from.direction ? `의 방향 ${esc(r.from.direction)}` : ""}</p>` : ""}
    <div class="verdict"><span class="big ${verdictClass(decided.verdict)}">${esc(decided.verdict)}</span>
    <ul class="steps">${decided.steps.map((s) => `<li>${esc(s)}</li>`).join("")}</ul></div>`);
  parts.push(`<h3>입력(사용자 입력)</h3><div class="scroll"><table>${Object.keys(S.FIELDS).map((k) => `<tr><th>${esc(S.FIELDS[k])}</th><td>${esc(r.idea[k])}</td></tr>`).join("")}</table></div>`);
  if (S.ORDER.every((k) => r.judges[k])) {
    parts.push(`<h3>심사위원(AI 시뮬레이션)</h3><div class="judges">${S.ORDER.map((k) => judgeCard(k, r.judges[k])).join("")}</div>`);
  }
  if (r.assumptions) {
    parts.push(`<h3>핵심 가정 검증</h3>` + r.assumptions.map((a) => `<div class="dir"><div class="t">${esc(S.ASSUMPTIONS[a.key])} <span class="badge ${statusClass(a.status)}">${esc(a.status)}</span></div>
      <div class="ev">가정: ${esc(a.statement)}</div><div class="ev usage">반박 근거를 먼저 찾은 검색어: ${esc(a.counter_query)}</div>
      ${a.evidence.map((e) => `<div class="ev"><span class="k">${esc(e.kind)}</span>(확인됨, ${esc(e.checked)}): <a href="${esc(safeUrl(e.url))}" target="_blank" rel="noopener noreferrer">${esc(e.title)}</a>${e.note ? `: ${esc(e.note)}` : ""}</div>`).join("") ||
        `<div class="ev">근거를 찾지 못했습니다(확인 못 함). 지어내지 않았습니다.</div>`}
      ${a.user_check ? `<div class="ev">직접 확인할 일: ${esc(a.user_check)}</div>` : ""}</div>`).join(""));
  }
  const c = r.competitors;
  parts.push(`<h3>경쟁 서비스</h3>` + (c ? `<p class="usage">찾은 범위: 검색어 ${esc(c.queries.join(", "))} (${esc(c.checked)})</p>` +
    (c.items.length ? `<div class="scroll"><table><tr><th>이름</th><th>출처</th><th>차이</th></tr>${c.items.map((i) => `<tr><td><a href="${esc(safeUrl(i.url))}" target="_blank" rel="noopener noreferrer">${esc(i.name)}</a></td><td>${esc(i.source)}, ${esc(i.checked)}</td><td>${esc(i.diff)}</td></tr>`).join("")}</table></div>`
      : `<p>이 범위에서는 경쟁 서비스를 찾지 못했습니다. 없다는 뜻은 아닙니다.</p>`) : `<p class="usage">조사하지 않았습니다.</p>`));
  const p = r.panel;
  if (p) {
    parts.push(`<h3>가상 사용자 패널(AI 시뮬레이션) <span class="badge v-none">판정에 쓰지 않음</span></h3>
      <p class="usage">패널 ${p.size}명: ${esc(p.personas.map((x) => `${x.type} ${x.count}명`).join(", "))}. 수요 예측이 아니라 반대 이유 모음입니다.</p>
      <ul>${p.against.map((x) => `<li>반대: ${esc(x.reason)}${x.types.length ? ` <span class="usage">(${esc(x.types.join(", "))})</span>` : ""}</li>`).join("") || "<li>반대 이유가 하나도 나오지 않았습니다. 패널이 한쪽으로 쏠렸을 수 있습니다.</li>"}
      ${p.for.map((x) => `<li>찬성: ${esc(x)}</li>`).join("")}</ul>`);
  }
  const m = r.money;
  parts.push(`<h3>손익분기</h3>` + (m && m.breakeven.computed
    ? `<ul>${Object.entries(S.MONEY_NAMES).map(([k, n]) => `<li>${esc(n)}: ${esc(S.comma(m.values[k].value))} (${esc(m.values[k].source)})</li>`).join("")}
       <li>고객당 남는 돈: ${esc(S.comma(m.breakeven.margin))}원</li><li><b>${m.breakeven.customers !== null ? `손익분기 월 고객 수: ${esc(S.comma(m.breakeven.customers))}명. ` : ""}</b>${esc(m.breakeven.note)}</li></ul>`
    : m ? `<p>계산하지 않았습니다. 필요한 값: ${esc(m.breakeven.needed.join(", "))}</p>` : `<p class="usage">가격·비용 값이 없어 계산하지 않았습니다.</p>`));
  const d = r.directions;
  if (d) {
    parts.push(`<h3>다듬은 방향(AI 제안)</h3>` + d.items.map((item, i) => `<div class="dir ${i + 1 === d.recommended ? "rec" : ""}">
      <div class="t">방향 ${i + 1}. ${esc(item.title)}${i + 1 === d.recommended ? '<span class="tag">추천</span>' : ""}</div>
      <div class="ev">한 줄: ${esc(item.idea.line)}</div>
      <div class="ev">바꾼 것: ${esc(item.changed)}</div><div class="ev">해결하는 지적: ${esc(item.addresses.join(" / "))}</div>
      ${item.user_checks.map((x) => `<div class="ev">직접 확인할 일: ${esc(x)}</div>`).join("")}
      <div class="row" style="margin-top:8px"><button class="btn small" data-direction="${i + 1}">이 방향으로 다시 심사</button></div></div>`).join("") +
      `<p class="usage">추천 이유: ${esc(d.why)}. 방향은 제안이며 원래 입력은 그대로 남아 있습니다.</p>`);
  }
  const next = ["진행", "조건부"].includes(decided.verdict)
    ? `<p class="sub">기획으로 넘기기: ${B.mode === "local" ? "" : "verdict.md를 내려받은 뒤 그 경로로 "}Claude Code에서 <code>/saerok-prd:design --from "${esc(report.path)}"</code></p>` : "";
  parts.push(`<h3>내려받기</h3>${next}<div class="row">
      <button class="btn primary" data-download="md">verdict.md 내려받기</button>
      <button class="btn" data-download="json">result.json 내려받기</button>
      <button class="btn" data-toggle-md>verdict.md 보기</button></div>
    ${B.mode === "local" ? `<p class="usage">내 PC에 저장됨: ${esc(report.path)}</p>` : `<p class="usage">이 브라우저에만 저장했습니다. 다른 기기에서 보려면 내려받아 두세요.</p>`}
    <pre class="md hidden"></pre><p class="usage usage-live"></p>`);
  return parts.join("");
}

function download(name, text, type) {
  const url = URL.createObjectURL(new Blob([text], { type }));
  const a = document.createElement("a");
  a.href = url;
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function bindResult(root, run, report) {
  const base = `${run.slug}-${run.run}`;
  root.querySelector("[data-download=md]").onclick = () => download(`${base}-verdict.md`, report.markdown, "text/markdown;charset=utf-8");
  root.querySelector("[data-download=json]").onclick = () => download(`${base}-result.json`, JSON.stringify(run.result, null, 2) + "\n", "application/json");
  root.querySelector("[data-toggle-md]").onclick = () => {
    const pre = root.querySelector("pre.md");
    pre.textContent = report.markdown;
    pre.classList.toggle("hidden");
  };
  for (const b of root.querySelectorAll("[data-direction]")) {
    b.onclick = () => startFromDirection(run, Number(b.dataset.direction));
  }
  renderUsage();
}

function startFromDirection(run, n) {
  const item = run.result.directions.items[n - 1];
  state.from = { run, direction: n };
  fillIdea(item.idea);
  $("#from-note").textContent = `방향 ${n}(${item.title})을 다시 심사합니다. 같은 아이디어 폴더(${run.slug})에 새 기록으로 남고, 원래 기록은 그대로입니다. 입력을 고쳐도 됩니다.`;
  show("#from-note");
  show("#cancel-from");
  selectTab("judge");
  for (const id of ["#step-judges", "#step-queries", "#step-research", "#step-result"]) hide(id);
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function cancelFrom() {
  state.from = null;
  hide("#from-note");
  hide("#cancel-from");
}

// ---------- 기록 탭 ----------
async function renderHistory() {
  $("#history-where").textContent = B.mode === "local"
    ? `내 PC 기록 폴더: ${B.info.home}` : "이 브라우저에만 저장된 기록입니다. 브라우저 데이터를 지우면 사라지니 필요한 것은 내려받아 두세요.";
  hide("#history-view");
  let ideas;
  try { ideas = await B.history(); } catch (e) { $("#history").innerHTML = `<p class="empty">${esc(e.message)}</p>`; return; }
  if (!ideas.length) { $("#history").innerHTML = `<p class="empty">아직 심사 기록이 없습니다.</p>`; return; }
  const head = ["기록", "판정", ...S.ORDER.map((k) => S.JUDGES[k].name), ...Object.values(S.ASSUMPTIONS), ""];
  $("#history").innerHTML = ideas.map((idea, gi) => {
    const rows = S.compare(idea.runs.map((r) => ({ run: r.run, result: r.result })));
    return `<h3>${esc(last(idea.runs).result.idea.line)}</h3><div class="scroll"><table><tr>${head.map((h) => `<th>${esc(h)}</th>`).join("")}</tr>
      ${rows.map((row, ri) => `<tr><td>${esc(row.run)}${row.from && row.from.direction ? ` <span class="usage">방향 ${esc(row.from.direction)}</span>` : ""}</td>
        <td><span class="badge ${verdictClass(row.verdict)}">${esc(row.verdict)}</span></td>
        ${S.ORDER.map((k) => `<td>${row.scores[k] ?? "-"}</td>`).join("")}
        ${Object.keys(S.ASSUMPTIONS).map((k) => `<td>${esc(row.assumptions[k] || "-")}</td>`).join("")}
        <td><button class="btn small" data-open="${gi}:${ri}">열기</button>${B.mode === "browser" ? ` <button class="btn small" data-remove="${gi}:${ri}">지우기</button>` : ""}</td></tr>`).join("")}
      </table></div>`;
  }).join("");
  const pick = (v) => { const [g, r] = v.split(":").map(Number); return ideas[g].runs[r]; };
  for (const b of $$("[data-open]", $("#history"))) b.onclick = () => openRun(pick(b.dataset.open));
  for (const b of $$("[data-remove]", $("#history"))) {
    b.onclick = () => {
      const run = pick(b.dataset.remove);
      if (!confirm(`${run.slug} / ${run.run} 기록을 이 브라우저에서 지울까요? 되돌릴 수 없습니다.`)) return;
      B.remove(run);
      renderHistory();
    };
  }
}

async function openRun(run) {
  const view = $("#history-view");
  let report;
  try {
    report = await B.report(run);
  } catch (e) {
    // 끝나지 않은 기록은 verdict.md를 만들 수 없어 있는 부분만 보여 줍니다.
    report = { markdown: `# 미완료 기록\n\n${e.message}\n`, path: B.mode === "local" ? run.id : `${run.slug}/${run.run}` };
  }
  view.innerHTML = resultHTML(run, report);
  bindResult(view, run, report);
  show("#history-view");
  view.scrollIntoView({ behavior: "smooth" });
}

function selectTab(name) {
  for (const t of $$(".tab")) t.setAttribute("aria-selected", String(t.dataset.tab === name));
  $("#tab-judge").classList.toggle("hidden", name !== "judge");
  $("#tab-history").classList.toggle("hidden", name !== "history");
  if (name === "history") renderHistory();
}

// ---------- 설정 ----------
function renderMode() {
  $("#mode").innerHTML = B.mode === "local"
    ? `<b>내 PC 모드</b> · 기록은 <code>${esc(B.info.home)}</code>에만, 키는 ${esc(B.info.key_from || "아직 없음")}`
    : `<b>브라우저 모드</b> · 키와 기록은 이 브라우저에만 저장되고, Claude는 Anthropic에 바로 연결합니다. ` +
      `내 PC에 저장하려면 터미널에서 <code>saerok-idea</code>를 실행하세요.`;
}

function openSettings() {
  const p = prefs();
  for (const id of ["#model-judge", "#model-lead"]) {
    $(id).innerHTML = MODELS.map(([v, n]) => `<option value="${v}">${n}</option>`).join("");
  }
  $("#model-judge").value = p.judge;
  $("#model-lead").value = p.lead;
  $("#settings-msg").textContent = "";
  $("#key-browser").classList.toggle("hidden", B.mode === "local");
  $("#key-local").classList.toggle("hidden", B.mode !== "local");
  if (B.mode === "local") {
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
  local.set(PREFS, { judge: $("#model-judge").value, lead: $("#model-lead").value });
  try {
    if (B.mode === "local") {
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
}

async function main() {
  await B.init();
  renderMode();
  $("#start").onclick = start;
  $("#search").onclick = startResearch;
  $("#read-fields").onclick = readFields;
  $("#cancel-from").onclick = cancelFrom;
  $("#open-settings").onclick = openSettings;
  $("#save-settings").onclick = saveSettings;
  $("#forget-key").onclick = forgetKey;
  $("#close-settings").onclick = () => $("#settings").close();
  for (const t of $$(".tab")) t.onclick = () => selectTab(t.dataset.tab);
}

main();
