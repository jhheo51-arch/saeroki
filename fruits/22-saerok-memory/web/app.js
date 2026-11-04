"use strict";

const TOKEN = document.querySelector('meta[name="saerok-token"]').content;
let data = null;
const picked = new Set();      // 휴지통 후보
const trimPicked = new Set();  // 목차 줄 후보
const enc = new TextEncoder();
const bytes = (t) => enc.encode(String(t ?? "")).length;

const $ = (id) => document.getElementById(id);
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const num = (n) => (Number(n) || 0).toLocaleString("ko-KR");
function size(n) {
  n = Number(n) || 0;
  if (n >= 1e9) return (n / 1e9).toFixed(1) + "GB";
  if (n >= 1e6) return (n / 1e6).toFixed(1) + "MB";
  if (n >= 1e3) return (n / 1e3).toFixed(1) + "KB";
  return n + "B";
}
const shortProject = (p) => String(p).replace(/^[A-Za-z]--/, "").replace(/-/g, " ").slice(0, 60);

function toast(text) {
  const t = $("toast");
  t.textContent = text;
  t.classList.add("show");
  clearTimeout(toast.timer);
  toast.timer = setTimeout(() => t.classList.remove("show"), 6000);
}

async function post(path, body) {
  const res = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Saerok-Token": TOKEN },
    body: JSON.stringify(body),
  });
  const out = await res.json().catch(() => ({ error: "응답을 읽지 못했습니다." }));
  toast(out.message || out.error || "끝났습니다.");
  if (res.ok) await load();
  return out;
}

async function load() {
  $("updated").textContent = "검사하는 중…";
  $("refresh").disabled = true;
  try {
    const res = await fetch("/api/summary");
    data = await res.json();
    if (!res.ok) throw new Error(data.error || "검사 실패");
    const all = [...data.versions.candidates, ...data.sessions.candidates];
    for (const id of [...picked]) if (!all.some((c) => c.id === id)) picked.delete(id);
    for (const id of [...trimPicked]) if (!data.memory.candidates.some((c) => c.id === id)) trimPicked.delete(id);
    render();
    $("updated").textContent = `${data.generated_at} 검사`;
  } catch (e) {
    $("updated").textContent = "검사 실패: " + e.message;
  } finally {
    $("refresh").disabled = false;
  }
}

function render() {
  renderNow();
  renderCandidates();
  renderLog();
}

// ---- 지금 ----
function renderNow() {
  const L = data.limits;
  const projects = data.memory.projects;
  const total = projects.reduce((s, p) => s + p.index_bytes, 0);
  const longLines = projects.reduce((s, p) => s + p.long_lines, 0);
  const longest = Math.max(0, ...projects.map((p) => p.longest_line));
  const over = projects.filter((p) => p.over_limit).length;
  const v = data.versions, s = data.sessions;
  const vBytes = v.candidates.reduce((a, c) => a + c.bytes, 0);
  const sBytes = s.candidates.reduce((a, c) => a + c.bytes, 0);
  $("cards").innerHTML = [
    card("기억 목차 합계", `${num(total)}바이트`, `기준 ${num(L.index)}바이트 넘은 프로젝트 ${over}곳`, over > 0),
    card("가장 긴 목차 줄", `${num(longest)}자`, `${L.line}자 넘는 줄 ${longLines}개`, longest > L.line),
    card("옛 버전 후보", `${v.candidates.length}개`, `${size(vBytes)} · 보호 ${v.guarded}개 · 최신 두 버전 ${v.kept}개 남김`),
    card("세션 기록", size(s.bytes), `${s.logs}개 중 ${L.session_days}일 넘은 후보 ${s.candidates.length}개(${size(sBytes)})`),
  ].join("");

  const rows = projects.slice().sort((a, b) => b.index_bytes - a.index_bytes).map((p) => {
    const ratio = Math.min(100, (p.index_bytes / L.index) * 100);
    return `<tr>
      <td title="${esc(p.cwd || p.project)}">${esc(p.cwd || shortProject(p.project))}</td>
      <td class="num">${num(p.index_bytes)}</td>
      <td><div class="gauge"><div class="fill${p.over_limit ? " over" : ""}" style="width:${ratio}%"></div></div></td>
      <td class="num">${num(p.index_lines)}</td>
      <td class="num">${num(p.longest_line)}자${p.long_lines ? ` <span class="badge over">${p.long_lines}</span>` : ""}</td>
      <td class="num">${num(p.files)}개 · ${size(p.file_bytes)}</td>
      <td class="num">약 ${num(p.index_tokens)}</td>
    </tr>`;
  });
  $("projects").innerHTML = rows.length
    ? `<div class="table-wrap"><table><thead><tr><th>프로젝트</th><th class="num">목차 바이트</th><th>기준 ${num(L.index)} 대비</th><th class="num">목차 줄</th><th class="num">가장 긴 줄</th><th class="num">기억 파일</th><th class="num">토큰(어림)</th></tr></thead><tbody>${rows.join("")}</tbody></table></div>`
    : `<div class="empty">기억 폴더가 없습니다.</div>`;

  $("hook").innerHTML = `<div class="item"><div class="row">
    <div><span class="badge ${data.hook_installed ? "ok" : ""}">${data.hook_installed ? "켜짐" : "꺼짐"}</span>
    MEMORY.md가 ${num(L.index)}바이트를 넘거나 ${L.line}자 넘는 줄이 생기면, 상태가 바뀔 때 한 번만 알립니다.</div>
    <button data-hook="${data.hook_installed ? "off" : "on"}" class="${data.hook_installed ? "ghost" : ""}">${data.hook_installed ? "끄기" : "켜기"}</button>
  </div></div>`;
}

function card(label, value, hint, over = false) {
  return `<div class="card${over ? " over" : ""}"><div class="label">${esc(label)}</div><div class="value">${esc(value)}</div><div class="hint">${esc(hint)}</div></div>`;
}

// ---- 후보 ----
function renderCandidates() {
  const mem = data.memory.candidates;
  // 150자 넘는 줄을 먼저, 그다음 예산 때문에 줄일 줄을 줄이는 바이트가 큰 순서로 둡니다.
  const trim = mem.filter((c) => c.kind === "index_line")
    .sort((a, b) => (a.budget_only - b.budget_only) || (b.saves - a.saves));
  const arch = mem.filter((c) => c.kind === "archive");
  const review = mem.filter((c) => !c.actionable || ["stale", "broken", "duplicate"].includes(c.kind));
  const count = trim.length + arch.length + data.versions.candidates.length + data.sessions.candidates.length;
  $("cand-count").textContent = count || "";

  $("trim").innerHTML = trim.length
    ? `<div id="budget"></div>${trim.map(trimItem).join("")}`
    : `<div class="empty">${data.limits.line}자 넘는 목차 줄이 없고, 목차도 ${num(data.limits.index)}바이트 안입니다.</div>`;
  renderBudget();
  $("archive").innerHTML = arch.length ? arch.map((c) => `<div class="item"><div class="row">
      <div><h3>${esc(c.title)}</h3><div class="small">${esc(c.reason)} · ${esc(shortProject(c.project))}</div></div>
      <button data-archive="${esc(c.id)}">_archive로 옮기기</button></div></div>`).join("")
    : `<div class="empty">마감·중단 뒤 ${data.limits.memory_days}일 넘은 기억이 없습니다.</div>`;

  const names = { stale: "낡은 경로", broken: "목차 어긋남", duplicate: "중복 의심", index_line: "긴 목차 줄" };
  $("review").innerHTML = review.filter((c) => c.kind !== "index_line").length
    ? `<div class="table-wrap"><table><thead><tr><th>종류</th><th>기억</th><th>이유</th></tr></thead><tbody>${review
        .filter((c) => c.kind !== "index_line")
        .map((c) => `<tr><td><span class="badge">${esc(names[c.kind] || c.kind)}</span></td><td>${esc(c.title)}</td><td class="path">${esc(c.reason)}</td></tr>`)
        .join("")}</tbody></table></div>`
    : `<div class="empty">확인할 것이 없습니다.</div>`;

  renderFiles();
}

// 체크 상자를 누를 때는 이 두 표만 다시 그려, 고쳐 쓰던 목차 줄이 지워지지 않게 합니다.
function renderFiles() {
  $("versions").innerHTML = fileTable(data.versions.candidates, "옛 버전 후보가 없습니다.");
  $("sessions").innerHTML = fileTable(data.sessions.candidates,
    `${data.limits.session_days}일 넘게 바뀌지 않은 세션 기록이 없습니다. 열린 기록 ${data.sessions.open}개는 늘 뺍니다.`);
}

// 목차 예산: 고른 줄을 지금 적힌 문장대로 바꾸면 목차가 몇 바이트가 되는지 바로 계산합니다.
function renderBudget() {
  const box = $("budget");
  if (!box) return;
  const L = data.limits;
  const trims = data.memory.candidates.filter((c) => c.kind === "index_line");
  const projects = data.memory.projects.filter((p) => trims.some((c) => c.project === p.project));
  box.innerHTML = projects.map((p) => {
    const mine = trims.filter((c) => c.project === p.project);
    const on = mine.filter((c) => trimPicked.has(c.id));
    const after = p.index_bytes - on.reduce((a, c) => a + bytes(c.before) - bytes(currentText(c)), 0);
    const ok = after <= L.index;
    const plan = p.budget;
    const planText = plan
      ? plan.reachable
        ? `줄마다 ${plan.line}자 안으로 줄이면 약 ${num(plan.projected_bytes)}바이트가 됩니다. 원래 설명은 기억 파일 끝으로 옮겨져 잃는 것이 없습니다.`
        : `${plan.line}자까지 줄여도 약 ${num(plan.projected_bytes)}바이트입니다. 끝난 기억 보관도 함께 보세요.`
      : `목차는 이미 ${num(L.index)}바이트 안입니다. ${L.line}자 넘는 줄만 줄이면 됩니다.`;
    const ids = mine.map((c) => c.id).join(",");
    return `<div class="item budget${ok ? "" : " over"}">
      <div class="row">
        <div><h3>${esc(p.cwd || shortProject(p.project))} 목차 예산</h3>
          <div class="small">${esc(planText)}</div></div>
        <div class="budget-num"><strong class="${ok ? "ok-text" : "over-text"}">${num(p.index_bytes)} → ${num(after)}바이트</strong>
          <span class="small">기준 ${num(L.index)} · 고른 줄 ${on.length}/${mine.length}</span></div>
      </div>
      <div class="gauge"><div class="fill${ok ? "" : " over"}" style="width:${Math.min(100, (after / L.index) * 100)}%"></div></div>
      <div class="bar-actions">
        <label><input type="checkbox" data-tall="${esc(ids)}" ${on.length === mine.length ? "checked" : ""}> 모두 고르기</label>
        <button data-trim-many="${esc(ids)}" ${on.length ? "" : "disabled"}>고른 ${on.length}줄 한 번에 적용</button>
      </div>
    </div>`;
  }).join("");
}

function currentText(c) {
  const ta = document.querySelector(`.item[data-id="${c.id}"] textarea`);
  return ta ? ta.value.trim() : (c.ai_proposal || c.proposal);
}

function trimItem(c) {
  const ai = c.ai_proposal;
  const start = ai || c.proposal;
  return `<div class="item" data-id="${esc(c.id)}">
    <h3><input type="checkbox" data-tpick="${esc(c.id)}" ${trimPicked.has(c.id) ? "checked" : ""} aria-label="${esc(c.title)} 고르기">
      ${esc(c.title)} <span class="badge${c.budget_only ? "" : " over"}">${esc(c.reason)}</span> <span class="small">${esc(shortProject(c.project))}</span></h3>
    <div class="diff">
      <div class="before"><div class="label">지금(${num(c.before.length)}자)</div>${esc(c.before)}</div>
      <div class="after"><div class="label"><span>바꿀 줄 · 고쳐 쓸 수 있습니다</span><span class="len"></span></div>
        <textarea rows="2" aria-label="바꿀 목차 줄">${esc(start)}</textarea></div>
    </div>
    <div class="row">
      <div class="choices">
        <button class="ghost" data-fill="cut">앞부분 남기기 제안</button>
        ${ai ? `<button class="ghost" data-fill="ai">AI 요약 제안</button>` : `<span class="small">AI 요약은 Claude에서 /saerok-memory:trim으로 만듭니다.</span>`}
      </div>
      <button data-trim="${esc(c.id)}">적용</button>
    </div>
  </div>`;
}

function fileTable(list, emptyText) {
  if (!list.length) return `<div class="empty">${esc(emptyText)}</div>`;
  const ids = list.map((c) => c.id);
  const on = ids.filter((i) => picked.has(i));
  const bytes = list.filter((c) => picked.has(c.id)).reduce((a, c) => a + c.bytes, 0);
  return `<div class="bar-actions">
      <label><input type="checkbox" data-all="${esc(ids.join(","))}" ${on.length === ids.length ? "checked" : ""}> 모두 고르기</label>
      <button data-trash="${esc(ids.join(","))}" ${on.length ? "" : "disabled"}>고른 ${on.length}개(${size(bytes)}) 휴지통으로</button>
    </div>
    <div class="table-wrap"><table><thead><tr><th></th><th>파일</th><th>이유</th><th class="num">크기</th></tr></thead><tbody>${list
      .map((c) => `<tr><td><input type="checkbox" data-pick="${esc(c.id)}" ${picked.has(c.id) ? "checked" : ""} aria-label="${esc(c.title)} 고르기"></td>
        <td class="path" title="${esc(c.path)}">${esc(c.path)}</td><td>${esc(c.reason)}</td><td class="num">${size(c.bytes)}</td></tr>`)
      .join("")}</tbody></table></div>`;
}

// ---- 기록 ----
function renderLog() {
  const log = data.apply_log;
  const st = data.stats;
  $("log-stats").innerHTML = st && st.actions ? [
    card("적용한 조치", `${num(st.actions)}건`, `되돌린 것 ${num(st.undone)}건`),
    card("되돌린 비율", `${st.undo_rate}%`, "목표 10% 이하. 높으면 후보 기준을 다시 봅니다", st.undo_rate > 10),
    card("목차에서 줄인 양", `${num(st.index_bytes_saved)}바이트`, "되돌린 조치는 뺐습니다"),
    card("휴지통으로 보낸 양", size(st.trashed_bytes), "비우기 전까지 Windows 휴지통에서 복원할 수 있습니다"),
  ].join("") : "";
  $("log").innerHTML = log.length
    ? `<div class="table-wrap"><table><thead><tr><th>시각</th><th>조치</th><th>대상</th><th></th></tr></thead><tbody>${log
        .map((e) => {
          const files = (e.ops || []).map((o) => (o.path || o.src || "").split(/[\\/]/).pop()).filter(Boolean);
          const trashOnly = (e.ops || []).every((o) => o.type === "trash");
          const action = e.undone_at
            ? `<span class="small">${esc(e.undone_at)} 되돌림</span>`
            : trashOnly
              ? `<span class="small">휴지통에서 복원</span>`
              : `<button class="ghost" data-undo="${esc(e.id)}">되돌리기</button>`;
          return `<tr><td class="num">${esc(e.at)}</td><td>${esc(e.label)}</td><td class="path">${esc([...new Set(files)].slice(0, 4).join(", "))}${files.length > 4 ? ` 외 ${files.length - 4}개` : ""}</td><td>${action}</td></tr>`;
        })
        .join("")}</tbody></table></div>`
    : `<div class="empty">아직 적용한 것이 없습니다.</div>`;
}

// ---- 이벤트 ----
function updateLen(item) {
  const ta = item.querySelector("textarea");
  const label = item.querySelector(".after .label");
  const c = data.memory.candidates.find((x) => x.id === item.dataset.id);
  const n = ta.value.trim().length;
  const goal = c && c.limit ? c.limit : data.limits.line;
  item.querySelector(".len").textContent = goal < data.limits.line ? `${n}자 / 예산 ${goal}자` : `${n}자 / ${goal}자`;
  label.classList.toggle("bad", n > data.limits.line);
  label.classList.toggle("warn", n <= data.limits.line && n > goal);
}

document.addEventListener("input", (ev) => {
  const item = ev.target.closest(".item[data-id]");
  if (item && ev.target.tagName === "TEXTAREA") {
    updateLen(item);
    renderBudget();
  }
});

document.addEventListener("change", (ev) => {
  const t = ev.target;
  if (t.dataset.pick) {
    t.checked ? picked.add(t.dataset.pick) : picked.delete(t.dataset.pick);
    renderFiles();
  } else if (t.dataset.all) {
    for (const id of t.dataset.all.split(",")) t.checked ? picked.add(id) : picked.delete(id);
    renderFiles();
  } else if (t.dataset.tpick) {
    t.checked ? trimPicked.add(t.dataset.tpick) : trimPicked.delete(t.dataset.tpick);
    renderBudget();
  } else if (t.dataset.tall) {
    for (const id of t.dataset.tall.split(",")) {
      t.checked ? trimPicked.add(id) : trimPicked.delete(id);
      const box = document.querySelector(`input[data-tpick="${id}"]`);
      if (box) box.checked = t.checked;
    }
    renderBudget();
  }
});

document.addEventListener("click", async (ev) => {
  const b = ev.target.closest("button");
  if (!b) return;
  if (b.dataset.tab) return showTab(b.dataset.tab);
  if (b.id === "refresh") return load();
  const item = b.closest(".item[data-id]");
  if (b.dataset.fill && item) {
    const c = data.memory.candidates.find((x) => x.id === item.dataset.id);
    item.querySelector("textarea").value = b.dataset.fill === "ai" ? c.ai_proposal : c.proposal;
    return updateLen(item);
  }
  b.disabled = true;
  try {
    if (b.dataset.trimMany) {
      const ids = b.dataset.trimMany.split(",").filter((i) => trimPicked.has(i));
      const items = ids.map((id) => ({ id, text: currentText(data.memory.candidates.find((c) => c.id === id)) }));
      if (items.some((i) => i.text.length > data.limits.line)) {
        toast(`${data.limits.line}자 넘는 줄이 있습니다. 고친 뒤 다시 누르세요.`);
      } else if (confirm(`고른 목차 줄 ${ids.length}개를 바꿀까요? 원래 설명은 각 기억 파일 끝으로 옮기고, 기록 탭에서 한 번에 되돌릴 수 있습니다.`)) {
        const out = await post("/api/trim-many", { items });
        if (out.ok) {
          trimPicked.clear();
          renderBudget();
        }
      }
    } else if (b.dataset.trim) {
      await post("/api/trim", { id: b.dataset.trim, text: item.querySelector("textarea").value.trim() });
    } else if (b.dataset.archive) {
      if (confirm("이 기억 파일을 _archive로 옮기고 목차에서 뺄까요? 기록 탭에서 되돌릴 수 있습니다.")) await post("/api/archive", { id: b.dataset.archive });
    } else if (b.dataset.trash) {
      const ids = b.dataset.trash.split(",").filter((i) => picked.has(i));
      if (confirm(`고른 ${ids.length}개를 Windows 휴지통으로 보낼까요? 영구 삭제는 하지 않습니다.`)) await post("/api/trash", { ids });
    } else if (b.dataset.hook) {
      await post("/api/hook", { on: b.dataset.hook === "on" });
    } else if (b.dataset.undo) {
      await post("/api/undo", { id: b.dataset.undo });
    }
  } finally {
    b.disabled = false;
  }
});

function showTab(name) {
  for (const t of document.querySelectorAll(".tabs button")) t.setAttribute("aria-selected", String(t.dataset.tab === name));
  for (const s of document.querySelectorAll(".tab")) s.hidden = s.id !== "tab-" + name;
  if (name === "cand") for (const item of document.querySelectorAll(".item[data-id]")) updateLen(item);
}

load().then(() => {
  for (const item of document.querySelectorAll(".item[data-id]")) updateLen(item);
});
