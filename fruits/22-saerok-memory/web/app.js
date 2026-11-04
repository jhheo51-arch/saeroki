"use strict";

const TOKEN = document.querySelector('meta[name="saerok-token"]').content;
let data = null;
const picked = new Set();

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
    for (const id of [...picked]) {
      const all = [...data.versions.candidates, ...data.sessions.candidates];
      if (!all.some((c) => c.id === id)) picked.delete(id);
    }
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
  const trim = mem.filter((c) => c.kind === "index_line");
  const arch = mem.filter((c) => c.kind === "archive");
  const review = mem.filter((c) => !c.actionable || ["stale", "broken", "duplicate"].includes(c.kind));
  const count = trim.length + arch.length + data.versions.candidates.length + data.sessions.candidates.length;
  $("cand-count").textContent = count || "";

  $("trim").innerHTML = trim.length ? trim.map(trimItem).join("") : `<div class="empty">${data.limits.line}자 넘는 목차 줄이 없습니다.</div>`;
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

function trimItem(c) {
  const ai = c.ai_proposal;
  const start = ai || c.proposal;
  return `<div class="item" data-id="${esc(c.id)}">
    <h3>${esc(c.title)} <span class="badge over">${esc(c.reason)}</span> <span class="small">${esc(shortProject(c.project))}</span></h3>
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
  const n = ta.value.trim().length;
  item.querySelector(".len").textContent = `${n}자`;
  label.classList.toggle("bad", n > data.limits.line);
}

document.addEventListener("input", (ev) => {
  const item = ev.target.closest(".item[data-id]");
  if (item && ev.target.tagName === "TEXTAREA") updateLen(item);
});

document.addEventListener("change", (ev) => {
  const t = ev.target;
  if (t.dataset.pick) {
    t.checked ? picked.add(t.dataset.pick) : picked.delete(t.dataset.pick);
    renderFiles();
  } else if (t.dataset.all) {
    for (const id of t.dataset.all.split(",")) t.checked ? picked.add(id) : picked.delete(id);
    renderFiles();
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
    if (b.dataset.trim) {
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
