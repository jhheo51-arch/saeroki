/* 새록 지원서 결정적 계층의 브라우저판. saerok_apply/core.py(와 store.py의 개인정보 점검)를 한 줄씩 옮겼습니다.
   같은 입력이면 Python과 같은 결과를 냅니다. test_saerok_apply.py가 node로 이 파일을 돌려 두 결과를 비교합니다.
   글자 수는 Python처럼 코드 포인트(Array.from)로, 바이트는 UTF-8(TextEncoder)로 셉니다. AI는 쓰지 않습니다. */
(function (root) {
  "use strict";

  const TYPES = ["경험형", "성장과정형", "지원 동기형", "직무 이해형", "미래·상상형"];
  const STAR = ["상황", "과제", "행동", "결과", "연결"];
  const SOURCES = ["공고", "조사", "의견"];
  const ACTION_TAGS = ["한 일", "설계안(도입 가정)", "계획"];
  const REQUIRED = ["기간", "소속·직함", "내 역할", "판단 이유", "행동", "결과", "역량"];
  const METRIC_REQUIRED = ["지표", "시점", "비교", "출처"];
  const METRIC_VALUES = ["전", "후", "값"];
  const UNCONFIRMED = "(AI 정리, 확인 전)";
  const IMAGE_MARK = "(이미지에서 옮김, 확인 전)";
  const NEED = "[사용자 확인 필요";
  const SPACES = " \t\n\r\f\v 　";

  const TITLES = ["프로젝트 매니저", "프로덕트 매니저", "부위원장", "위원장", "부회장", "회장", "팀장", "파트장", "리더", "대표",
    "총무", "매니저", "인턴", "기획자", "운영진", "운영자", "개발자", "디자이너", "분석가", "조장", "멘토",
    "간사", "사원", "주임", "대리", "과장", "차장", "부장", "실장", "본부장", "선임", "연구원", "조교", "반장",
    "PM", "PO"];
  const PARTICLES = ["으로서", "로서", "으로", "이었", "이자", "에게", "로", "을", "를", "이", "가", "은", "는", "의", "와",
    "과", "도", "에", "직", "였", "님", "들"];
  const CHANGE = ["벌어", "좁혀", "처음", "최초", "최대", "최고", "최저", "최소", "역대", "넘어섰", "돌파", "아래로", "밑으로",
    "역전", "앞질", "따라잡", "유일", "1위", "두 배", "절반"];
  const HEDGE = ["가정", "설계", "계획", "제안", "구상", "초안", "예정", "검토"];
  const ABSTRACT = ["크게 개선", "크게 향상", "크게 늘", "크게 줄", "크게 기여", "많이 기여", "많은 기여", "큰 성과", "많은 성과",
    "좋은 성과", "눈에 띄게", "획기적", "대폭", "상당히", "극대화", "많은 도움", "큰 도움", "큰 변화"];
  const TEAM = ["우리 팀", "저희 팀", "팀 전체", "팀은", "팀이", "저희는", "저희가", "우리는", "우리가", "동아리는", "동아리가"];
  const SELF = ["제가", "저는", "나는", "내가", "저 혼자", "직접", "제 역할", "저의", "제 몫"];
  const REASON = ["때문", "위해", "이유", "판단", "근거로", "보고", "생각해", "하려고", "고자", "목표로", "알기 위해", "봤기", "보았기"];
  const LINK = ["직무", "입사", "지원한", "살려", "하겠습니다", "기여하고", "이어가"];
  const UNITS = ["%p", "%", "퍼센트", "개월", "명", "건", "개", "원", "만", "억", "천", "배", "주", "년", "월", "일", "시간",
    "분기", "학기", "회", "위", "점", "곳", "권", "장", "달"];
  const PERIOD_UNITS = ["개월", "주", "년", "월", "일", "시간", "분기", "학기", "달"];
  const TYPE_WORDS = [
    ["미래·상상형", ["10년", "미래", "일기", "상상", "만약", "뒤의 나", "후의 모습"]],
    ["지원 동기형", ["지원 동기", "지원한 이유", "지원하게 된", "입사 후", "포부", "왜 우리"]],
    ["성장과정형", ["성장 과정", "성장과정", "가치관", "살아온", "성격", "좌우명"]],
    ["경험형", ["실패", "성과", "협업", "갈등", "어려움", "극복", "도전", "경험", "문제를 해결", "주도"]],
    ["직무 이해형", ["직무", "역량", "이해", "업무", "전문성"]],
  ];

  const NUM = /[0-9][0-9,]*(?:\.[0-9]+)?/g;
  const ID = /^E[0-9]{2,}$/;
  const DATE = /[0-9]{4}-[0-9]{2}-[0-9]{2}/;
  const URL = /https?:\/\/[^\s)>\]|]+/;
  const COMMENT = /<!--([\s\S]*?)-->/g;
  const FIELD = /^-\s*([^:：]+?)\s*[:：]\s*(.*)$/;
  const SUBITEM = /^\s+[-*]\s*(.*)$/;
  const ACTION = /^\[([^\]]+)\]\s*(.*)$/;
  const LEDGER_HEAD = /^##\s+(E[0-9]{2,})(?![0-9])[\s.·:\-]*(.*)$/;
  const LIMIT = /([0-9][0-9,]*)\s*(자|바이트|byte|bytes)\s*(?:\(\s*(공백 포함|공백 제외)\s*\))?/;
  const VERSION = /^v([0-9]+)\s*[·:\-—–]\s*(.+)$/;
  const PER_UNIT = /[가-힣0-9]+당/g;
  const YEAR = /20[0-9]{2}/g;
  const HALF = /상반기|하반기|[1-4]분기/g;
  const TAIL_MARK = /[\s.!?"'”’)\]]+$/;
  const BIGRAM_SKIP = ".,!?'\"“”‘’()[]·:;-";

  // ---------- 작은 도구 ----------
  const len = (s) => Array.from(s).length;
  const has = (text, words) => words.some((w) => text.includes(w));
  const findAll = (re, text) => text.match(re) || [];
  const isSpace = (ch) => SPACES.includes(ch);

  function count(text) {
    let noSpace = 0;
    for (const ch of text) if (!isSpace(ch)) noSpace += 1;
    return { with_spaces: len(text), without_spaces: noSpace, bytes: new TextEncoder().encode(text).length };
  }

  function fit(counted, limit, basis) {
    if (!limit) return { value: counted.with_spaces, ratio: null, fit: "no-limit" };
    const value = counted[basis];
    const ratio = Math.floor(value * 100 / limit);
    const state = value > limit ? "over" : (value * 10 < limit * 9 ? "short" : "ok");
    return { value, ratio, fit: state };
  }

  function normNum(n) {
    n = n.replace(/,/g, "");
    if (n.includes(".")) {
      n = n.replace(/0+$/, "").replace(/\.+$/, "");
      return n || "0";
    }
    return n.replace(/^0+/, "") || "0";
  }

  const isLatin = (ch) => !!ch && (("A" <= ch && ch <= "Z") || ("a" <= ch && ch <= "z"));

  function numbers(text, strict = true) {
    const out = [];
    for (const m of text.matchAll(NUM)) {
      const raw = m[0].replace(/,+$/, "");
      const start = m.index, end = m.index + raw.length;
      const before = start > 0 ? text[start - 1] : "";
      const rest = text.slice(end);
      if (strict && before && isLatin(before)) continue;
      let unit = "";
      const stripped = rest.replace(/^ +/, "");
      for (const u of UNITS) {
        if (stripped.startsWith(u)) { unit = u; break; }
      }
      if (strict && (stripped.slice(unit.length).startsWith("당") || (!unit && ["인당", "건당"].includes(stripped.slice(0, 2))))) continue;
      if (strict && stripped.slice(0, 1) === "당") continue;
      out.push({ raw, value: normNum(raw), unit, kind: PERIOD_UNITS.includes(unit) ? "기간" : "숫자" });
    }
    return out;
  }

  function isPast(text) {
    const s = Array.from(text.replace(TAIL_MARK, ""));
    let prev;
    if (s.join("").endsWith("습니다")) prev = s.length >= 4 ? s[s.length - 4] : "";
    else if (s.join("").endsWith("다")) prev = s.length >= 2 ? s[s.length - 2] : "";
    else return false;
    if (!prev || "있겠없".includes(prev)) return false;
    const code = prev.codePointAt(0) - 0xAC00;
    return code >= 0 && code < 11172 && code % 28 === 20;
  }

  function isFuture(text) {
    const s = Array.from(text.replace(TAIL_MARK, "")).slice(-6).join("");
    return s.includes("겠") || s.includes("싶");
  }

  const hangulOrLatin = (ch) => !!ch && (("가" <= ch && ch <= "힣") || isLatin(ch));

  function titlesIn(text) {
    const found = [];
    for (const title of TITLES) {
      let i = text.indexOf(title);
      while (i !== -1) {
        const before = i > 0 ? text[i - 1] : "";
        const after = text.slice(i + title.length);
        const okBefore = !hangulOrLatin(before);
        const okAfter = !after || !hangulOrLatin(after[0]) || PARTICLES.some((p) => after.startsWith(p));
        if (okBefore && okAfter && !found.includes(title)) { found.push(title); break; }
        i = text.indexOf(title, i + 1);
      }
    }
    return found;
  }

  const asciiWord = (ch) => !!ch && (isLatin(ch) || ("0" <= ch && ch <= "9"));

  function findName(text, name) {
    if (!name) return -1;
    const ascii = Array.from(name).every((ch) => ch.codePointAt(0) < 128);
    const hay = ascii ? text.toLowerCase() : text, needle = ascii ? name.toLowerCase() : name;
    let i = hay.indexOf(needle);
    while (i !== -1) {
      if (!ascii) return i;
      const before = i > 0 ? hay[i - 1] : "";
      const after = i + needle.length < hay.length ? hay[i + needle.length] : "";
      if (!asciiWord(before) && !asciiWord(after)) return i;
      i = hay.indexOf(needle, i + 1);
    }
    return -1;
  }

  function bigrams(text) {
    const s = Array.from(text).filter((ch) => !isSpace(ch) && !BIGRAM_SKIP.includes(ch));
    const out = new Set();
    for (let i = 0; i < s.length - 1; i++) out.add(s[i] + s[i + 1]);
    return out;
  }
  const common = (a, b) => { let n = 0; for (const x of a) if (b.has(x)) n += 1; return n; };

  const plain = (text) => text.replace(COMMENT, "");
  const squash = (text) => Array.from(plain(text)).filter((ch) => !isSpace(ch) && !BIGRAM_SKIP.includes(ch)).join("");

  function guessType(title) {
    for (const [kind, words] of TYPE_WORDS) if (has(title, words)) return kind;
    return "경험형";
  }

  // ---------- 문장 나누기 ----------
  function parseTag(raw) {
    const tag = { ids: [], labels: [], sources: [], unknown: [] };
    for (const token of raw.trim().split(/[\s,]+/)) {
      if (!token) continue;
      if (ID.test(token)) tag.ids.push(token);
      else if (STAR.includes(token)) tag.labels.push(token);
      else if (SOURCES.includes(token)) tag.sources.push(token);
      else tag.unknown.push(token);
    }
    return tag;
  }

  function sentences(block) {
    const parts = block.split(COMMENT);  // 갈라 낸 주석 속 글이 홀수 자리에 옵니다(Python re.split과 같음).
    const out = [];
    parts.forEach((part, k) => {
      if (k % 2 === 1) {
        if (out.length) {
          const tag = parseTag(part);
          for (const key of ["ids", "labels", "sources", "unknown"]) {
            for (const v of tag[key]) if (!out[out.length - 1][key].includes(v)) out[out.length - 1][key].push(v);
          }
        }
        return;
      }
      let start = 0;
      for (let i = 0; i < part.length; i++) {
        const ch = part[i];
        if (".!?".includes(ch) && (i + 1 === part.length || isSpace(part[i + 1]))) {
          const text = part.slice(start, i + 1).trim();
          if (text) out.push({ text, ids: [], labels: [], sources: [], unknown: [] });
          start = i + 1;
        }
      }
      const tail = part.slice(start).trim();
      if (tail) out.push({ text: tail, ids: [], labels: [], sources: [], unknown: [] });
    });
    return out;
  }

  function paragraphs(lines) {
    const paras = [];
    let cur = [];
    for (const line of lines) {
      if (!line.trim()) {
        if (cur.length) { paras.push(cur.join("\n")); cur = []; }
      } else if (line.trimStart().startsWith(">")) {
        continue;
      } else {
        cur.push(line.trim());
      }
    }
    if (cur.length) paras.push(cur.join("\n"));
    return paras;
  }

  function cleanLines(p) {
    return plain(p).split("\n").map((ln) => ln.replace(/[ \t]+/g, " ").trim()).filter((ln) => ln).join("\n");
  }

  function bodyText(paras) {
    return paras.map(cleanLines).filter((t) => t).join("\n");
  }

  function tableRows(lines) {
    const rows = [];
    for (const line of lines) {
      const s = line.trim();
      if (!s.startsWith("|")) continue;
      const cells = s.replace(/^\|+|\|+$/g, "").split("|").map((c) => c.trim());
      if (cells.filter((c) => c).every((c) => /^:?-{2,}:?$/.test(c))) continue;
      rows.push(cells);
    }
    return rows.slice(1);
  }

  function sections(text, level = "## ") {
    const head = [], out = [];
    for (const line of text.replace(/\r\n/g, "\n").split("\n")) {
      if (line.startsWith(level)) out.push([line.slice(level.length).trim(), []]);
      else if (out.length) out[out.length - 1][1].push(line);
      else head.push(line);
    }
    return [head, out];
  }

  function fields(lines) {
    const out = {};
    for (const line of lines) {
      const m = FIELD.exec(line.trim());
      if (m && !(m[1].trim() in out)) out[m[1].trim()] = m[2].trim();
    }
    return out;
  }

  const get = (obj, key) => (Object.prototype.hasOwnProperty.call(obj, key) ? obj[key] : "");
  const issue = (issues, level, code, where, text, message) => issues.push({ level, code, where, text, message });

  // ---------- 경험 장부 ----------
  function parseLedger(text) {
    const experiences = [], issues = [];
    const seen = new Set();
    for (const [heading, lines] of sections(text)[1]) {
      const m = LEDGER_HEAD.exec("## " + heading);
      if (!m) continue;
      const exp = { id: m[1], title: m[2].trim(), fields: {}, actions: [], metrics: [], competencies: [], unconfirmed: [] };
      const where = exp.id;
      if (seen.has(exp.id)) issue(issues, "error", "ledger_dup_id", where, "", `경험 ID ${exp.id}가 두 번 나옵니다.`);
      seen.add(exp.id);
      let current = "";
      for (const line of lines) {
        if (!line.trim()) continue;
        const sub = SUBITEM.exec(line);
        if (sub && (current === "행동" || current === "수치")) {
          const item = sub[1].trim();
          if (current === "행동") {
            const a = ACTION.exec(item);
            if (!a || !ACTION_TAGS.includes(a[1])) {
              issue(issues, "error", "ledger_action_tag", where, item, "행동 앞에 [한 일]·[설계안(도입 가정)]·[계획] 중 하나를 붙여 주세요.");
              continue;
            }
            exp.actions.push({ tag: a[1], text: a[2].trim(), confirmed: !item.includes(UNCONFIRMED) });
            if (item.includes(UNCONFIRMED) && !exp.unconfirmed.includes("행동")) exp.unconfirmed.push("행동");
          } else {
            const metric = { raw: item, confirmed: !item.includes(UNCONFIRMED) };
            for (const piece of item.split("|")) {
              const kv = /^\s*([^:：]+?)\s*[:：]\s*(.*?)\s*$/.exec(piece);
              if (kv) metric[kv[1]] = kv[2];
            }
            const missing = METRIC_REQUIRED.filter((k) => !get(metric, k));
            if (!(get(metric, "값") || (get(metric, "전") && get(metric, "후")))) missing.push("전·후 또는 값");
            if (missing.length) issue(issues, "error", "ledger_metric", where, item, `수치에 ${missing.join(", ")} 칸이 없습니다.`);
            exp.metrics.push(metric);
            if (item.includes(UNCONFIRMED) && !exp.unconfirmed.includes("수치")) exp.unconfirmed.push("수치");
          }
          continue;
        }
        const f = !(line.startsWith(" ") || line.startsWith("\t")) ? FIELD.exec(line.trim()) : null;
        if (f) {
          current = f[1].trim();
          exp.fields[current] = f[2].trim();
          if (f[2].includes(UNCONFIRMED) && !exp.unconfirmed.includes(current)) exp.unconfirmed.push(current);
        }
      }
      for (const key of REQUIRED) {
        if (key === "행동") {
          if (!exp.actions.length) issue(issues, "error", "ledger_field", where, "", "행동이 없습니다. '- 행동:' 아래에 [한 일] 등으로 적어 주세요.");
        } else if (!get(exp.fields, key)) {
          issue(issues, "error", "ledger_field", where, "", `'${key}' 칸이 비었습니다.`);
        }
      }
      exp.competencies = plain(get(exp.fields, "역량")).split(/[,，]/).map((c) => c.trim()).filter((c) => c && c !== UNCONFIRMED);
      const confirmed = [exp.title], everything = [exp.title];
      for (const value of Object.values(exp.fields)) {
        everything.push(value);
        if (!value.includes(UNCONFIRMED)) confirmed.push(value);
      }
      for (const a of exp.actions) { everything.push(a.text); if (a.confirmed) confirmed.push(a.text); }
      for (const mt of exp.metrics) { everything.push(mt.raw); if (mt.confirmed) confirmed.push(mt.raw); }
      exp.evidence = confirmed.join("\n");
      exp.all_text = everything.join("\n");
      experiences.push(exp);
    }
    if (!experiences.length) issue(issues, "error", "ledger_empty", "장부", "", "경험이 없습니다. '## E01. 경험 이름'으로 시작해 주세요.");
    return { experiences, issues };
  }

  function ledgerReport(text) {
    const parsed = parseLedger(text);
    const rows = parsed.experiences.map((e) => {
      const actions = {};
      for (const t of ACTION_TAGS) actions[t] = e.actions.filter((a) => a.tag === t).length;
      return { id: e.id, title: e.title, period: get(e.fields, "기간"), competencies: e.competencies, actions,
        metrics: e.metrics.length, unconfirmed: e.unconfirmed };
    });
    const errors = parsed.issues.filter((i) => i.level === "error").length;
    return { experiences: rows, issues: parsed.issues,
      summary: { experiences: rows.length, errors, unconfirmed: rows.filter((r) => r.unconfirmed.length).length } };
  }

  // ---------- 공고·분석 ----------
  function parsePosting(text) {
    const [head, secs] = sections(text);
    const meta = fields(head);
    let body = "";
    for (const [heading, lines] of secs) if (heading.startsWith("원문")) body = lines.join("\n").trim();
    let status = get(meta, "상태");
    if (text.includes(IMAGE_MARK) && !status.includes("확인함")) status = IMAGE_MARK;
    return { company: get(meta, "회사"), source: get(meta, "출처"), checked_at: get(meta, "확인 날짜"),
      image: get(meta, "원본 이미지"), status: status || "확인함", body };
  }

  const BULLET = /^\s*[-*]\s+(.+)$/;

  function parseAnalysis(text) {
    const out = { items: [], keywords: [], posting_info: "", research: [], research_status: "", research_text: "", terms: [], sections: [] };
    for (const [heading, lines] of sections(text)[1]) {
      out.sections.push(heading);
      if (heading.startsWith("요구·우대 역량")) {
        for (const cells of tableRows(lines)) {
          if (cells.length && cells[0]) {
            out.items.push({ item: plain(cells[0]).trim(), kind: cells.length > 1 ? cells[1] : "",
              ids: cells.length > 3 ? findAll(/E[0-9]{2,}/g, cells[3]) : [], gap: cells.length > 4 ? cells[4] : "" });
          }
        }
      } else if (heading.startsWith("세부 업무")) {
        for (const line of lines) {
          const m = BULLET.exec(line);
          if (m) out.items.push({ item: plain(m[1]).trim(), kind: "업무", ids: [], gap: "" });
        }
      } else if (heading.startsWith("숨은 키워드")) {
        const marked = heading.includes("AI 해석");
        for (const line of lines) {
          const m = BULLET.exec(line);
          if (m) out.keywords.push({ text: m[1].trim(), ai: marked || m[1].includes("AI 해석") });
        }
      } else if (heading.startsWith("회사·직무 맥락")) {
        for (const [sub, subLines] of sections(lines.join("\n"), "### ")[1]) {
          const joined = subLines.join("\n").trim();
          if (sub.startsWith("공고 안 정보")) {
            out.posting_info = joined;
          } else if (sub.startsWith("회사 조사")) {
            out.research_text = joined;
            for (const line of subLines) {
              const m = BULLET.exec(line);
              if (!m) continue;
              const item = m[1].trim();
              if (item.includes("자료 없음") || item.includes("조사 안 됨")) continue;
              const url = URL.exec(item), date = DATE.exec(item);
              out.research.push({ text: item, url: url ? url[0] : "", date: date ? date[0] : "" });
            }
            if (joined.includes("조사 안 됨")) out.research_status = "조사 안 됨";
            else if (joined.includes("자료 없음") || !out.research.length) out.research_status = "자료 없음";
            else out.research_status = "있음";
          }
        }
      } else if (heading.startsWith("용어")) {
        for (const cells of tableRows(lines)) {
          if (cells.length && cells[0]) out.terms.push({ term: cells[0], meaning: cells.length > 1 ? cells[1] : "" });
        }
      }
    }
    return out;
  }

  function termNames(entry) {
    const names = [];
    for (const name of [entry.term || "", entry.korean || "", entry.original || "", ...(entry.aliases || [])]) {
      if (name && len(name) >= 2 && !names.includes(name)) names.push(name);
    }
    return names;
  }

  function termIndex(terms) {
    const index = new Map();
    for (const entry of (terms || {}).terms || []) {
      for (const name of termNames(entry)) if (!index.has(name.toLowerCase())) index.set(name.toLowerCase(), entry);
    }
    return index;
  }

  function sense(entry, industry, role) {
    const senses = entry.senses || [];
    for (const s of senses) {
      if ((!industry || s.industries.includes(industry)) && (!role || s.roles.includes(role))) return s;
    }
    return senses.length ? senses[0] : { definition: "", level: "" };
  }

  function matchTerms(text, terms, industry = "", role = "") {
    const found = [];
    for (const entry of (terms || {}).terms || []) {
      let best = -1, hit = "";
      for (const name of termNames(entry)) {
        const i = findName(text, name);
        if (i !== -1 && (best === -1 || i < best)) { best = i; hit = name; }
      }
      if (best !== -1) {
        const s = sense(entry, industry, role);
        found.push({ term: entry.term, found: hit, at: best, level: s.level || "", definition: s.definition || "" });
      }
    }
    found.sort((a, b) => (a.at - b.at) || (a.term < b.term ? -1 : a.term > b.term ? 1 : 0));
    return found.map((f) => ({ term: f.term, found: f.found, level: f.level, definition: f.definition }));
  }

  function checkAnalysis(postingText, analysisText, terms = null) {
    const issues = [];
    const posting = parsePosting(postingText || "");
    const flags = { posting_failed: false, image_unconfirmed: false, research_none: false, terms_missing: [] };
    if (!postingText || !postingText.trim()) {
      flags.posting_failed = true;
      issue(issues, "error", "posting_missing", "posting.md", "", "공고 원문이 없습니다. 붙여넣기나 캡처 이미지로 넣어 주세요.");
    } else if (posting.status.includes("읽기 실패")) {
      flags.posting_failed = true;
      issue(issues, "error", "posting_failed", "posting.md", posting.source,
        "공고를 읽지 못했습니다. 빈 공고로 분석하지 않습니다. 본문을 붙여 넣거나 캡처를 넣어 주세요.");
    } else if (posting.status === IMAGE_MARK) {
      flags.image_unconfirmed = true;
      issue(issues, "error", "image_unconfirmed", "posting.md", posting.image,
        "이미지에서 옮긴 공고를 아직 확인하지 않았습니다. 확인 전에는 분석하지 않습니다.");
    } else {
      if (!posting.body) {
        flags.posting_failed = true;
        issue(issues, "error", "posting_empty", "posting.md", "", "'## 원문' 아래가 비었습니다.");
      }
      if (!posting.source) issue(issues, "error", "posting_source", "posting.md", "", "'- 출처:'(URL, 붙여넣기, 이미지)가 없습니다.");
      if (!DATE.test(posting.checked_at)) issue(issues, "error", "posting_date", "posting.md", "", "'- 확인 날짜: YYYY-MM-DD'가 없습니다.");
    }
    const blocked = flags.posting_failed || flags.image_unconfirmed;
    const analysis = parseAnalysis(analysisText || "");
    if (analysisText && analysisText.trim()) {
      for (const name of ["요구·우대 역량", "숨은 키워드", "회사·직무 맥락", "용어"]) {
        if (!analysis.sections.some((h) => h.startsWith(name))) issue(issues, "error", "analysis_section", "analysis.md", "", `'## ${name}' 칸이 없습니다.`);
      }
      if (!analysis.items.length) issue(issues, "error", "analysis_items", "analysis.md", "", "요구·우대 역량 표가 비었습니다.");
      for (const k of analysis.keywords) {
        if (!k.ai) issue(issues, "error", "keyword_not_marked", "analysis.md", k.text, "숨은 키워드는 'AI 해석'으로 표시합니다.");
      }
      if (["자료 없음", "조사 안 됨", ""].includes(analysis.research_status)) {
        flags.research_none = true;
        issue(issues, "warn", "research_none", "analysis.md", "",
          `회사 조사: ${analysis.research_status || "자료 없음"}. 자기소개서에 회사 조사 내용을 쓰지 않습니다.`);
      }
      for (const r of analysis.research) {
        if (!r.url || !r.date) issue(issues, "error", "research_no_source", "analysis.md", r.text,
          "회사 조사 항목에는 출처 링크와 확인 날짜(YYYY-MM-DD)가 있어야 합니다.");
      }
      const index = termIndex(terms);
      for (const t of analysis.terms) {
        if (t.meaning.includes("사전에 없음")) flags.terms_missing.push(t.term);
        else if (!index.has(t.term.toLowerCase())) issue(issues, "error", "term_not_in_dictionary", "analysis.md", t.term,
          "17번 사전에 없는 용어입니다. 뜻 칸을 '사전에 없음'으로 바꿔 주세요.");
      }
      if (flags.terms_missing.length) issue(issues, "warn", "terms_missing", "analysis.md", flags.terms_missing.join(", "),
        "사전에 없는 용어입니다. 뜻은 공고 원문으로 확인해 주세요.");
    }
    const errors = issues.filter((i) => i.level === "error").length;
    return { posting: { company: posting.company, source: posting.source, checked_at: posting.checked_at, image: posting.image, status: posting.status },
      blocked, flags, items: analysis.items, issues, summary: { errors, warnings: issues.length - errors, ready: errors === 0 } };
  }

  // ---------- 표기 규칙 ----------
  function parseStyle(text) {
    const style = { banned: [], replace: [], max_sentence: 0, tone: "" };
    for (const line of (text || "").replace(/\r\n/g, "\n").split("\n")) {
      const m = FIELD.exec(line.trim());
      if (!m) continue;
      const key = m[1].trim(), value = m[2].trim();
      if (key === "쓰지 않음" && value) {
        style.banned.push(value);
      } else if (key === "바꿈" && value.includes("→")) {
        const at = value.indexOf("→");
        const a = value.slice(0, at), b = value.slice(at + 1);
        if (a.trim()) style.replace.push([a.trim(), b.trim()]);
      } else if (key === "문장 길이") {
        const n = /[0-9]+/.exec(value);
        style.max_sentence = n ? parseInt(n[0], 10) : 0;
      } else if (key === "말투" && ["합니다", "해요", "한다"].includes(value)) {
        style.tone = value;
      }
    }
    return style;
  }

  function toneOk(text, tone) {
    const s = text.replace(TAIL_MARK, "");
    if (tone === "합니다") return s.endsWith("니다") || s.endsWith("니까");
    if (tone === "해요") return s.endsWith("요");
    if (tone === "한다") return s.endsWith("다") && !s.endsWith("니다");
    return true;
  }

  // ---------- 자기소개서 초안 ----------
  const QUESTION_META = ["유형", "제한", "판", "상태", "연결", "경험"];

  function parseDraft(text) {
    const [head, secs] = sections(text);
    const meta = fields(head);
    const questions = [], short = [];
    for (const [heading, lines] of secs) {
      if (heading.startsWith("짧은 칸")) {
        for (const cells of tableRows(lines)) {
          if (cells.length < 3 || !cells[0]) continue;
          const n = /[0-9]+/.exec(cells[1]);
          const content = cells[2];
          const ids = [], srcs = [];
          for (const s of sentences(content)) {
            for (const i of s.ids) if (!ids.includes(i)) ids.push(i);
            for (const i of s.sources) if (!srcs.includes(i)) srcs.push(i);
          }
          short.push({ name: cells[0], limit: n ? parseInt(n[0], 10) : null, content: plain(content).trim(), ids, sources: srcs });
        }
        continue;
      }
      const m = /^문항\s*([0-9]+)\s*[.:)·]?\s*(.*)$/.exec(heading);
      const q = { no: m ? parseInt(m[1], 10) : questions.length + 1, title: (m ? m[2] : heading).trim(), meta: {}, paras: [], raw: "" };
      const main = [];
      for (const line of lines) {
        if (line.startsWith("### ")) break;
        main.push(line);
      }
      let i = 0;
      while (i < main.length && !main[i].trim()) i += 1;
      while (i < main.length) {
        const f = FIELD.exec(main[i].trim());
        if (!main[i].trim()) { i += 1; continue; }
        if (!f || !QUESTION_META.includes(f[1].trim())) break;
        q.meta[f[1].trim()] = f[2].trim();
        i += 1;
      }
      q.paras = paragraphs(main.slice(i));
      q.raw = q.paras.join("\n\n");
      const limit = LIMIT.exec(get(q.meta, "제한"));
      q.limit = limit ? parseInt(limit[1].replace(/,/g, ""), 10) : null;
      q.basis = limit && limit[2] !== "자" ? "bytes" : (limit && limit[3] === "공백 제외" ? "without_spaces" : "with_spaces");
      const ver = VERSION.exec(get(q.meta, "판"));
      q.version = ver ? `v${ver[1]}` : "";
      q.change = ver ? ver[2].trim() : "";
      q.confirmed = get(q.meta, "상태").trim() === "확정";
      q.type = get(q.meta, "유형").trim();
      q.links = get(q.meta, "연결").split(/[,，]/).map((c) => c.trim()).filter((c) => c);
      questions.push(q);
    }
    return { company: get(meta, "회사"), mode: get(meta, "모드") || (("모드" in meta) ? "" : "초안"), original: get(meta, "원문"),
      date: get(meta, "날짜"), questions, short };
  }

  function submission(text) {
    const draft = parseDraft(text);
    const out = [draft.company ? `# 자기소개서 · ${draft.company}` : "# 자기소개서", ""];
    for (const q of draft.questions) {
      out.push(`## 문항 ${q.no}. ${q.title}`.trimEnd(), "");
      for (const p of q.paras) {
        const para = cleanLines(p);
        if (para) out.push(para, "");
      }
    }
    if (draft.short.length) {
      out.push("## 짧은 칸", "");
      for (const s of draft.short) out.push(`- ${s.name}: ${s.content}`);
      out.push("");
    }
    return out.join("\n").trimEnd() + "\n";
  }

  function evidenceOf(exps, ids) {
    const found = ids.filter((i) => exps.has(i)).map((i) => exps.get(i));
    return [found.map((e) => e.evidence).join("\n"), found.map((e) => e.all_text).join("\n")];
  }

  function factChecks(issues, where, s, exps, postingBody, researchText) {
    const text = s.text;
    const ids = s.ids.filter((i) => exps.has(i));
    if (ids.length) {
      const [evidence, everything] = evidenceOf(exps, ids);
      const have = new Set(numbers(evidence, false).map((n) => n.value));
      const haveAll = new Set(numbers(everything, false).map((n) => n.value));
      for (const n of numbers(text)) {
        if (have.has(n.value)) continue;
        const what = n.kind === "기간" ? "기간·시점" : "숫자";
        if (haveAll.has(n.value)) {
          issue(issues, "error", "unconfirmed_ledger", where, text,
            `${n.raw}${n.unit}는 장부의 '(AI 정리, 확인 전)' 칸에만 있습니다. 장부를 먼저 확인해 주세요.`);
        } else {
          issue(issues, "error", n.kind === "기간" ? "period_not_in_ledger" : "number_not_in_ledger", where, text,
            `${what} ${n.raw}${n.unit}가 장부 ${ids.join(", ")}에 없습니다.`);
        }
      }
      for (const title of titlesIn(text)) {
        if (evidence.includes(title)) continue;
        if (everything.includes(title)) issue(issues, "error", "unconfirmed_ledger", where, text, `직함 '${title}'은 장부의 '(AI 정리, 확인 전)' 칸에만 있습니다.`);
        else issue(issues, "error", "title_not_in_ledger", where, text, `직함 '${title}'이 장부 ${ids.join(", ")}에 없습니다.`);
      }
      for (const word of CHANGE) {
        if (text.includes(word) && !evidence.includes(word)) issue(issues, "warn", "change_unsupported", where, text,
          `시점·변화 표현 '${word}'의 근거가 장부 ${ids.join(", ")}에 없습니다.`);
      }
      const metrics = [];
      for (const i of ids) for (const mt of exps.get(i).metrics) if (mt.confirmed) metrics.push(mt);
      const checked = new Set();
      for (const n of numbers(text)) {
        for (const mt of metrics) {
          const values = METRIC_VALUES.map((k) => get(mt, k)).join(" ");
          if (!numbers(values, false).some((x) => x.value === n.value && x.unit === n.unit)) continue;
          const name = get(mt, "지표");
          if (checked.has(mt) || !name) break;
          checked.add(mt);
          const words = name.trim().split(/\s+/);
          const headWord = words[words.length - 1];
          if (!text.includes(headWord)) issue(issues, "error", "metric_name_mismatch", where, text,
            `${n.raw}${n.unit}는 장부에서 '${name}'의 값입니다. 문장에 지표 이름 '${headWord}'가 없습니다.`);
          for (const per of findAll(PER_UNIT, text)) {
            if (!name.includes(per)) issue(issues, "error", "metric_unit_mismatch", where, text, `문장의 '${per}'가 장부 지표 '${name}'와 다릅니다.`);
          }
          const when = get(mt, "시점") + " " + get(mt, "기간");
          for (const t of [...findAll(YEAR, text), ...findAll(HALF, text)]) {
            if (!when.includes(t)) issue(issues, "error", "metric_time_mismatch", where, text,
              `'${t}'가 장부 지표 '${name}'의 시점(${get(mt, "시점")})과 다릅니다.`);
          }
          break;
        }
      }
      if (isPast(text) && !has(text, HEDGE)) {
        const sb = bigrams(text);
        let best = null, bestRatio = -1;
        for (const i of ids) {
          for (const a of exps.get(i).actions) {
            const ab = bigrams(a.text);
            if (!ab.size) continue;
            const ratio = Math.floor(common(sb, ab) * 1000 / ab.size);
            if (ratio > bestRatio) { best = a; bestRatio = ratio; }
          }
        }
        if (best && best.tag !== "한 일" && bestRatio >= 400) issue(issues, "error", "plan_as_done", where, text,
          `장부에서 [${best.tag}]인 행동을 과거형 성과로 썼습니다: ${best.text}`);
      }
    }
    if (s.sources.includes("공고") && postingBody) {
      const have = new Set(numbers(postingBody, false).map((n) => n.value));
      for (const n of numbers(text)) if (!have.has(n.value)) issue(issues, "error", "number_not_in_posting", where, text, `${n.raw}${n.unit}가 공고 원문에 없습니다.`);
    }
    if (s.sources.includes("조사") && researchText) {
      const have = new Set(numbers(researchText, false).map((n) => n.value));
      for (const n of numbers(text)) if (!have.has(n.value)) issue(issues, "error", "number_not_in_research", where, text, `${n.raw}${n.unit}가 회사 조사 칸에 없습니다.`);
    }
  }

  function companyChecks(issues, where, text, current, companies, mine) {
    for (const c of companies) {
      const name = c.name;
      if (!name || (current && (current.toLowerCase().includes(name.toLowerCase()) || name.toLowerCase().includes(current.toLowerCase())))) continue;
      if (findName(text, name) !== -1) {
        if (c.from === "folder" || mine.includes(name)) issue(issues, "error", "other_company", where, text, `지금 회사(${current || "미정"})가 아닌 지원 회사 이름 '${name}'이 있습니다.`);
        else issue(issues, "warn", "other_company", where, text, `다른 회사·브랜드 이름 '${name}'이 있습니다. 쓴 도구 이름이면 그대로 둬도 됩니다.`);
      }
    }
  }

  function styleChecks(issues, where, text, style, sentence = true) {
    for (const word of style.banned) if (text.includes(word)) issue(issues, "warn", "style_banned", where, text, `표기 규칙: '${word}'를 쓰지 않습니다.`);
    for (const [a, b] of style.replace) if (text.includes(a)) issue(issues, "warn", "style_replace", where, text, `표기 규칙: '${a}' 대신 '${b}'를 씁니다.`);
    if (sentence && style.max_sentence && len(text) > style.max_sentence) issue(issues, "warn", "style_length", where, text,
      `표기 규칙: 문장이 ${len(text)}자로 ${style.max_sentence}자보다 깁니다.`);
    if (sentence && style.tone && !toneOk(text, style.tone)) issue(issues, "warn", "style_tone", where, text, `표기 규칙: '${style.tone}' 말투로 끝내 주세요.`);
  }

  function termChecks(issues, where, text, terms) {
    if (!terms) return;
    const byName = termIndex(terms);
    for (const entry of terms.terms || []) {
      for (const name of termNames(entry)) {
        const i = findName(text, name);
        if (i === -1) continue;
        const rest = text.slice(i + name.length);
        let gloss = "";
        let m = /^\s*\(([^)]*)\)/.exec(rest);
        if (m) gloss = m[1];
        else {
          m = /^(?:이란|란|은|는|이|가)?\s*,?\s*(?:즉|곧)\s+([^,.]*)/.exec(rest);
          if (m) gloss = m[1];
        }
        if (!gloss) continue;
        for (const c of entry.confusable || []) {
          const other = byName.get(c.term.toLowerCase());
          const names = other ? termNames(other) : [c.term];
          if (names.some((n) => findName(gloss, n) !== -1)) {
            issue(issues, "warn", "term_confused", where, text, `'${name}'를 '${c.term}'의 뜻으로 썼을 수 있습니다(17번 사전: ${c.difference})`);
            return;
          }
        }
        break;
      }
    }
  }

  function check(draftText, ledgerText, analysisText = "", postingText = "", styleText = "", companies = null, terms = null, previousText = "") {
    const issues = [];
    const draft = parseDraft(draftText);
    const ledger = parseLedger(ledgerText || "");
    const exps = new Map(ledger.experiences.map((e) => [e.id, e]));
    const analysis = parseAnalysis(analysisText || "");
    const posting = parsePosting(postingText || "");
    const style = parseStyle(styleText);
    const current = draft.company;
    companies = companies || [];
    const mine = companies.filter((c) => c.from === "folder").map((c) => c.name);
    const researchNone = !!analysisText && ["", "자료 없음", "조사 안 됨"].includes(analysis.research_status);
    for (const li of ledger.issues) if (li.code === "ledger_empty") issue(issues, "error", "ledger_empty", "장부", "", li.message);
    if (!current) issue(issues, "error", "draft_meta", "머리", "", "'- 회사: 회사이름'이 없습니다.");
    const questions = [];
    for (const q of draft.questions) {
      const where = `문항 ${q.no}`;
      const body = bodyText(q.paras);
      const counted = count(body);
      const f = fit(counted, q.limit, q.basis);
      if (!TYPES.includes(q.type)) issue(issues, "error", "question_meta", where, "", `'- 유형:'은 ${TYPES.join(", ")} 중 하나여야 합니다.`);
      if (!get(q.meta, "제한")) issue(issues, "error", "question_meta", where, "", "'- 제한: 500자(공백 포함)'이 없습니다. 제한이 없으면 '없음'으로 적어 주세요.");
      else if (f.fit === "over") issue(issues, "error", "length_over", where, "", `${f.value}자로 제한 ${q.limit}자를 넘습니다(${f.ratio}%).`);
      else if (f.fit === "short") issue(issues, "error", "length_short", where, "", `${f.value}자로 제한 ${q.limit}자의 90%에 못 미칩니다(${f.ratio}%).`);
      else if (f.fit === "no-limit") issue(issues, "warn", "no_limit", where, "", "글자 수 제한이 없습니다.");
      if (!q.version) issue(issues, "error", "question_meta", where, "", "'- 판: v1 · 바꾼 점 한 줄'이 없습니다.");
      const ids = [], sents = [];
      let placeholders = 0;
      for (const para of q.paras) sents.push(...sentences(para));
      for (const s of sents) {
        const text = s.text;
        for (const i of s.ids) if (!ids.includes(i)) ids.push(i);
        if (text.includes(NEED)) {
          placeholders += 1;
          issue(issues, "error", "placeholder", where, text, "장부에 근거가 없어 남긴 칸입니다. 장부에 경험을 더하거나 문장을 빼 주세요.");
          continue;
        }
        for (const u of s.unknown) issue(issues, "warn", "unknown_tag", where, text, `모르는 주석 '${u}'입니다. E01·공고·조사·의견·상황·과제·행동·결과·연결만 씁니다.`);
        for (const i of s.ids) {
          if (!exps.has(i)) issue(issues, "error", "unknown_id", where, text, `장부에 ${i}가 없습니다.`);
          else if (exps.get(i).unconfirmed.length) issue(issues, "warn", "unconfirmed_ledger", where, text,
            `${i}에 확인 전 칸(${exps.get(i).unconfirmed.join(", ")})이 있습니다. 확인한 칸만 근거가 됩니다.`);
        }
        const factual = numbers(text).length > 0 || isPast(text) || (titlesIn(text).length > 0 && !isFuture(text));
        if (factual && !s.ids.length && !s.sources.length) issue(issues, "error", "no_id", where, text, "사실 문장에 근거 ID가 없습니다. 문장 뒤에 <!-- E01 -->처럼 달아 주세요.");
        if (s.sources.includes("조사") && researchNone) issue(issues, "error", "research_none_cited", where, text, "분석의 회사 조사가 '자료 없음'인데 조사를 근거로 썼습니다.");
        if (!s.sources.includes("의견")) factChecks(issues, where, s, exps, posting.body, analysis.research_text);
        if (has(text, ABSTRACT) && !/[0-9]/.test(text)) issue(issues, "warn", "para_abstract", where, text, "근거 없는 추상 성과입니다. 수치·기간·규모·전후 변화로 바꿔 주세요.");
        companyChecks(issues, where, text, current, companies, mine);
        styleChecks(issues, where, text, style);
        termChecks(issues, where, text, terms);
      }
      const labeled = sents.filter((s) => s.labels.length);
      if (q.type === "경험형" && !labeled.length && sents.length) issue(issues, "warn", "para_no_star", where, "", "경험형 문항인데 STAR 칸 표시(<!-- E01 행동 --> 등)가 없습니다.");
      if (labeled.length) {
        const size = (...labels) => sents.filter((s) => labels.some((lb) => s.labels.includes(lb))).reduce((n, s) => n + len(s.text), 0);
        const situation = size("상황", "과제"), action = size("행동");
        if (situation > action) issue(issues, "warn", "para_situation_long", where, "",
          `상황·과제(${situation}자)가 내 행동(${action}자)보다 깁니다. 상황은 짧게, 행동은 길게 씁니다.`);
        const results = sents.filter((s) => s.labels.includes("결과"));
        if (results.some((s) => has(s.text, TEAM)) && !sents.some((s) => has(s.text, SELF))) issue(issues, "warn", "para_team_only", where, "",
          "성과의 주어가 팀뿐입니다. 그 안에서 내가 한 일을 밝혀 주세요.");
        if (sents.some((s) => s.labels.includes("행동")) && !sents.some((s) => has(s.text, REASON))) issue(issues, "warn", "para_no_reason", where, "",
          "행동에 판단 이유가 없습니다. 왜 그렇게 했는지 써 주세요.");
        const last = sents.length ? sents[sents.length - 1].text : "";
        const linked = sents.some((s) => s.labels.includes("연결")) || has(last, LINK) || (!!current && last.includes(current));
        if (!linked) issue(issues, "warn", "para_no_link", where, "", "지원 직무에서 이 경험을 어떻게 쓸지로 끝내 주세요.");
      }
      questions.push({ no: q.no, title: q.title, type: q.type, type_guess: guessType(q.title), version: q.version, change: q.change,
        confirmed: q.confirmed, limit: q.limit, basis: q.basis, count: counted, ratio: f.ratio, fit: f.fit, ids, links: q.links,
        placeholders, _sents: sents, _body: body });
    }
    const shortRows = [];
    for (const sf of draft.short) {
      const where = `짧은 칸: ${sf.name}`;
      const counted = count(sf.content);
      const f = fit(counted, sf.limit, "with_spaces");
      if (f.fit === "over") issue(issues, "error", "length_over", where, sf.content, `${f.value}자로 제한 ${sf.limit}자를 넘습니다.`);
      if (sf.content.includes(NEED)) issue(issues, "error", "placeholder", where, sf.content, "장부에 근거가 없어 남긴 칸입니다.");
      else if (!sf.ids.length) issue(issues, "error", "short_no_id", where, sf.content, "짧은 칸에도 근거 ID(<!-- E01 -->)를 달아 주세요.");
      for (const i of sf.ids) if (!exps.has(i)) issue(issues, "error", "unknown_id", where, sf.content, `장부에 ${i}가 없습니다.`);
      const s = { text: sf.content, ids: sf.ids, labels: [], sources: sf.sources, unknown: [] };
      if (!sf.content.includes(NEED)) factChecks(issues, where, s, exps, posting.body, analysis.research_text);
      companyChecks(issues, where, sf.content, current, companies, mine);
      styleChecks(issues, where, sf.content, style, false);
      shortRows.push({ name: sf.name, limit: sf.limit, count: counted, ratio: f.ratio, fit: f.fit, ids: sf.ids });
    }
    // 문항 사이 중복
    const used = new Map();
    for (const q of questions) {
      for (const i of q.ids) {
        if (!used.has(i)) used.set(i, []);
        if (!used.get(i).includes(q.no)) used.get(i).push(q.no);
      }
    }
    for (const [i, nos] of used) if (nos.length > 1) issue(issues, "warn", "dup_experience", "전체", i, `${i} 경험이 문항 ${nos.join(", ")}에 겹칩니다.`);
    for (let a = 0; a < questions.length; a++) {
      for (let b = a + 1; b < questions.length; b++) {
        for (const sa of questions[a]._sents) {
          const ka = squash(sa.text);
          if (len(ka) < 10 || sa.text.includes(NEED)) continue;
          for (const sb of questions[b]._sents) {
            const kb = squash(sb.text);
            if (len(kb) < 10) continue;
            let same = ka === kb;
            if (!same && len(ka) >= 20 && len(kb) >= 20) {
              const ba = bigrams(ka), bb = bigrams(kb);
              same = 200 * common(ba, bb) >= 85 * (ba.size + bb.size);
            }
            if (same) issue(issues, "warn", "dup_sentence", `문항 ${questions[a].no}, ${questions[b].no}`, sb.text, "같거나 거의 같은 문장이 두 문항에 있습니다.");
          }
        }
      }
    }
    const seenNum = new Map();
    for (const q of questions) {
      for (const s of q._sents) {
        for (const n of numbers(s.text)) {
          if (!n.unit || PERIOD_UNITS.includes(n.unit)) continue;
          const key = n.value + n.unit;
          if (!seenNum.has(key)) seenNum.set(key, []);
          if (!seenNum.get(key).includes(q.no)) seenNum.get(key).push(q.no);
        }
      }
    }
    for (const [key, nos] of seenNum) if (nos.length > 1) issue(issues, "warn", "dup_number", "전체", key, `수치 ${key}가 문항 ${nos.join(", ")}에 되풀이됩니다.`);
    // 역량·세부 업무 커버리지
    const coverage = [];
    if (!analysisText) issue(issues, "warn", "no_analysis", "전체", "", "analysis.md가 없어 역량 커버리지를 보지 못했습니다.");
    const names = analysis.items.map((it) => it.item);
    for (const it of analysis.items) {
      const nos = questions.filter((q) => q.links.includes(it.item) || q._body.toLowerCase().includes(it.item.toLowerCase())).map((q) => q.no);
      coverage.push({ item: it.item, kind: it.kind, questions: nos });
      if (!nos.length) issue(issues, "warn", "coverage_missing", "전체", it.item, `공고의 ${it.kind || "역량"} '${it.item}'이 어느 문항에도 없습니다.`);
    }
    if (analysisText) {
      for (const q of questions) {
        for (const link of q.links) if (!names.includes(link)) issue(issues, "warn", "coverage_unknown", `문항 ${q.no}`, link, `'연결'의 '${link}'가 분석의 역량·세부 업무에 없습니다.`);
      }
    }
    // 확정 문항 보호
    if (previousText) {
      const before = new Map(parseDraft(previousText).questions.map((q) => [q.no, q]));
      for (const q of draft.questions) {
        const old = before.get(q.no);
        if (old && old.confirmed && (old.raw !== q.raw || old.title !== q.title || !q.confirmed)) issue(issues, "error", "confirmed_changed", `문항 ${q.no}`, "", "확정한 문항이 바뀌었습니다. 확정 문항은 다시 쓰지 않습니다.");
      }
    }
    for (const q of questions) { delete q._sents; delete q._body; }
    const errors = issues.filter((i) => i.level === "error").length;
    const confirmedAll = questions.length > 0 && questions.every((q) => q.confirmed);
    return { company: current, mode: draft.mode, questions, short_fields: shortRows, coverage, issues,
      summary: { errors, warnings: issues.length - errors, ready: errors === 0, confirmed_all: confirmedAll, submittable: errors === 0 && confirmedAll } };
  }

  // ---------- store.py의 개인정보 점검 ----------
  const PATTERNS = [
    ["주민등록번호", /(?<![0-9])[0-9]{6}[ \t]?-[ \t]?[1-4][0-9]{6}(?![0-9])/g],
    ["전화번호", /(?<![0-9])01[016789][-. \t]?[0-9]{3,4}[-. \t]?[0-9]{4}(?![0-9])/g],
    ["이메일", /[A-Za-z0-9_.+-]+@[A-Za-z0-9_-]+(\.[A-Za-z0-9_-]+)+/g],
  ];
  const mask = (text) => { const c = Array.from(text); return c.slice(0, 3).join("") + "*".repeat(Math.max(c.length - 3, 0)); };

  function scan(text) {
    const found = [];
    text.split(/\r\n|\r|\n/).forEach((line, k) => {
      for (const [kind, pattern] of PATTERNS) {
        for (const m of line.matchAll(pattern)) found.push({ line: k + 1, kind, masked: mask(m[0]) });
      }
    });
    return found;
  }

  const api = {
    TYPES, STAR, SOURCES, ACTION_TAGS, UNCONFIRMED, IMAGE_MARK, NEED,
    count, fit, numbers, isPast, isFuture, titlesIn, findName, plain, guessType, sentences, bodyText,
    parseLedger, ledgerReport, parsePosting, parseAnalysis, matchTerms, checkAnalysis, parseStyle, parseDraft, submission, check, scan,
  };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.SaerokApply = api;
})(typeof globalThis !== "undefined" ? globalThis : this);
