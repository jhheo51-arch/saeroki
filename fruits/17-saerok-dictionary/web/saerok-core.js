/* 새록 사전 핵심 로직. 브라우저(window.SaerokCore)와 Node(require) 양쪽에서 씁니다. */
(function (root, factory) {
  if (typeof module === "object" && module.exports) {
    module.exports = factory();
  } else {
    root.SaerokCore = factory();
  }
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  var LEVELS = ["입문", "실무", "심화"];
  var CIRCLED = ["①", "②", "③", "④", "⑤", "⑥", "⑦", "⑧", "⑨", "⑩"];

  // 대소문자, 공백, 가운뎃점, 하이픈, 슬래시, 괄호, 마침표를 지워 비교합니다.
  function normalize(text) {
    return String(text == null ? "" : text)
      .toLowerCase()
      .normalize("NFC")
      .replace(/[\s·・\-_/().,'"‘’“”]/g, "");
  }

  function searchKeys(term) {
    var keys = [term.term, term.original, term.korean, term.id].concat(term.aliases || []);
    return keys.filter(function (k) { return k; }).map(normalize);
  }

  function levelIndex(level) {
    var i = LEVELS.indexOf(level);
    return i < 0 ? LEVELS.length : i;
  }

  function senseMatches(sense, industry, role) {
    return sense.industries.indexOf(industry) >= 0 && sense.roles.indexOf(role) >= 0;
  }

  function senseScore(sense, industry, role) {
    var ind = sense.industries.indexOf(industry) >= 0;
    var rol = sense.roles.indexOf(role) >= 0;
    if (ind && rol) return 3;
    if (rol) return 2;
    if (ind) return 1;
    return 0;
  }

  // 고른 산업·직무에 맞는 뜻을 ①로 올리고, 나머지는 원래 순서를 지킵니다.
  function orderSenses(term, industry, role) {
    return term.senses
      .map(function (sense, index) { return { sense: sense, index: index, score: senseScore(sense, industry, role) }; })
      .sort(function (a, b) { return b.score - a.score || a.index - b.index; })
      .map(function (item, i) {
        return { number: CIRCLED[i] || "(" + (i + 1) + ")", sense: item.sense, matched: item.score === 3 };
      });
  }

  function cellSense(term, industry, role) {
    for (var i = 0; i < term.senses.length; i++) {
      if (senseMatches(term.senses[i], industry, role)) return term.senses[i];
    }
    return null;
  }

  function cellTerms(terms, industry, role) {
    var out = [];
    terms.forEach(function (term) {
      var sense = cellSense(term, industry, role);
      if (sense) out.push({ term: term, sense: sense });
    });
    return out;
  }

  // 표제어·원어·약어·한글명·별칭이 정확히 같으면 exact, 일부만 겹치면 partial입니다.
  function search(terms, query) {
    var q = normalize(query);
    var result = { query: query, exact: [], partial: [] };
    if (!q) return result;
    terms.forEach(function (term) {
      var keys = searchKeys(term);
      if (keys.indexOf(q) >= 0) {
        result.exact.push(term);
      } else if (q.length >= 2 && keys.some(function (k) { return k.indexOf(q) >= 0 || (k.length >= 2 && q.indexOf(k) >= 0); })) {
        result.partial.push(term);
      }
    });
    return result;
  }

  function matchPurpose(catalog, query) {
    var q = normalize(query);
    if (!q) return null;
    var purposes = catalog.purposes || [];
    for (var i = 0; i < purposes.length; i++) {
      var hit = (purposes[i].keywords || []).some(function (k) { return q.indexOf(normalize(k)) >= 0; });
      if (hit) return purposes[i];
    }
    return null;
  }

  // 목적형 묶음: 고른 칸의 용어를 중요도 순으로 줄 세웁니다. 확인 필요 뜻은 같은 조건에서 뒤로 보냅니다.
  function purposeList(terms, purpose, industry, role) {
    var levels = purpose.levels || LEVELS;
    var items = cellTerms(terms, industry, role).filter(function (item) {
      if (levels.indexOf(item.sense.level) < 0) return false;
      if (purpose.requires_formula && !item.sense.formula) return false;
      return true;
    });
    items.sort(function (a, b) {
      var lv = levels.indexOf(a.sense.level) - levels.indexOf(b.sense.level);
      var imp = (b.sense.importance || 0) - (a.sense.importance || 0);
      var unchecked = (a.sense.status === "verified" ? 0 : 1) - (b.sense.status === "verified" ? 0 : 1);
      var first = purpose.level_first ? lv || imp : imp || lv;
      return first || unchecked || (a.term.id < b.term.id ? -1 : a.term.id > b.term.id ? 1 : 0);
    });
    return items;
  }

  function page(items, pageIndex, size) {
    size = size || 10;
    var start = pageIndex * size;
    return { items: items.slice(start, start + size), hasMore: items.length > start + size, total: items.length };
  }

  function todayCandidates(terms, industry, role, seenIds) {
    var seen = {};
    (seenIds || []).forEach(function (id) { seen[id] = true; });
    var items = cellTerms(terms, industry, role).filter(function (item) { return !seen[item.term.id]; });
    items.sort(function (a, b) {
      return levelIndex(a.sense.level) - levelIndex(b.sense.level) ||
        (a.sense.industries.length === 1 ? 0 : 1) - (b.sense.industries.length === 1 ? 0 : 1) ||
        (b.sense.importance || 0) - (a.sense.importance || 0) ||
        (a.sense.status === "verified" ? 0 : 1) - (b.sense.status === "verified" ? 0 : 1) ||
        (a.term.id < b.term.id ? -1 : a.term.id > b.term.id ? 1 : 0);
    });
    return items;
  }

  // 오늘의 용어: 같은 날·같은 칸에서 이미 고른 용어가 있으면 그대로, 없으면 안 본 용어를 입문→실무→심화 순으로,
  // 같은 난이도에서는 고른 산업 전용 용어를 먼저, 그다음 중요도 순으로 고릅니다.
  function pickToday(terms, industry, role, seenIds, previous, today) {
    if (previous && previous.date === today && previous.industry === industry && previous.role === role) {
      var kept = terms.filter(function (t) { return t.id === previous.id; })[0];
      if (kept && cellSense(kept, industry, role)) return { term: kept, sense: cellSense(kept, industry, role), kept: true };
    }
    var candidates = todayCandidates(terms, industry, role, seenIds);
    if (!candidates.length) return null;
    return { term: candidates[0].term, sense: candidates[0].sense, kept: false };
  }

  function addMissing(list, query, date) {
    var q = normalize(query);
    if (!q) return list;
    var exists = list.some(function (item) { return normalize(item.query) === q; });
    if (exists) {
      return list.map(function (item) {
        return normalize(item.query) === q ? { query: item.query, first_seen: item.first_seen, last_seen: date, count: (item.count || 1) + 1 } : item;
      });
    }
    return list.concat([{ query: String(query).trim(), first_seen: date, last_seen: date, count: 1 }]);
  }

  function missingCsv(list) {
    var escape = function (v) { return '"' + String(v).replace(/"/g, '""') + '"'; };
    var rows = [["query", "count", "first_seen", "last_seen"].join(",")];
    list.forEach(function (item) {
      rows.push([escape(item.query), item.count || 1, item.first_seen, item.last_seen].join(","));
    });
    return rows.join("\n") + "\n";
  }

  return {
    LEVELS: LEVELS,
    normalize: normalize,
    searchKeys: searchKeys,
    orderSenses: orderSenses,
    cellSense: cellSense,
    cellTerms: cellTerms,
    search: search,
    matchPurpose: matchPurpose,
    purposeList: purposeList,
    page: page,
    todayCandidates: todayCandidates,
    pickToday: pickToday,
    addMissing: addMissing,
    missingCsv: missingCsv
  };
});
