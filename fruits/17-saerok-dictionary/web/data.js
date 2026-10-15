/* 자동 생성 파일입니다. data/glossary/*.json을 고친 뒤 `python glossary.py build`로 다시 만듭니다. */
window.SAEROK_DATA = {
 "catalog": {
  "version": 1,
  "industries": [
   {
    "id": "ecommerce",
    "name": "이커머스·리테일",
    "description": "온라인 쇼핑몰, 오픈마켓, 리테일 커머스"
   },
   {
    "id": "platform",
    "name": "IT·플랫폼 서비스",
    "description": "앱·웹 서비스, 중개 플랫폼, SaaS"
   }
  ],
  "roles": [
   {
    "id": "pm",
    "name": "기획(PM·PO)",
    "description": "제품 기획, 서비스 기획, 프로덕트 오너"
   },
   {
    "id": "data",
    "name": "데이터 분석",
    "description": "지표 설계, 분석, 실험"
   },
   {
    "id": "marketing",
    "name": "마케팅·그로스",
    "description": "퍼포먼스 마케팅, CRM, 그로스"
   },
   {
    "id": "cx",
    "name": "CX·운영",
    "description": "고객 상담, 서비스 운영, 물류·주문 운영"
   }
  ],
  "levels": [
   "입문",
   "실무",
   "심화"
  ],
  "purposes": [
   {
    "id": "first_week",
    "name": "입사 첫 주",
    "keywords": [
     "입사",
     "첫 주",
     "첫주",
     "온보딩",
     "신입",
     "기초",
     "입문"
    ],
    "levels": [
     "입문",
     "실무"
    ],
    "description": "회의에서 바로 들리는 입문 용어부터 중요도 순",
    "level_first": true
   },
   {
    "id": "interview",
    "name": "면접 준비",
    "keywords": [
     "면접",
     "취업",
     "지원",
     "인터뷰",
     "자소서"
    ],
    "levels": [
     "실무",
     "심화"
    ],
    "description": "실무·심화 용어를 중요도 순"
   },
   {
    "id": "metrics",
    "name": "지표 이해",
    "keywords": [
     "지표",
     "공식",
     "계산",
     "메트릭",
     "KPI",
     "수치"
    ],
    "levels": [
     "입문",
     "실무",
     "심화"
    ],
    "requires_formula": true,
    "description": "계산식이 있는 지표만 중요도 순"
   }
  ]
 },
 "terms": [
  {
   "id": "conversion_rate",
   "term": "전환율",
   "original": "Conversion Rate",
   "korean": "전환율",
   "aliases": [
    "CVR",
    "씨브이알",
    "컨버전율",
    "전환률"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "marketing",
      "data",
      "pm"
     ],
     "level": "입문",
     "importance": 5,
     "definition": "광고를 클릭하거나 사이트에 들어온 사람 가운데 구매·가입처럼 목표로 정한 행동까지 한 사람의 비율입니다. 무엇을 전환으로 볼지와 분모(클릭, 방문, 상호작용)를 먼저 정해야 숫자를 비교할 수 있습니다.",
     "formula": "전환율(%) = 전환 수 ÷ 광고 상호작용(또는 방문) 수 × 100",
     "examples": [
      "이번 주 상세페이지 전환율이 2%대로 떨어졌는데, 결제 단계에서 빠지는 건지 확인해 볼게요.",
      "전환 기준을 가입으로 볼지 첫 구매로 볼지 먼저 정하고 전환율 비교합시다."
     ],
     "sources": [
      {
       "title": "전환율: 정의 - Google Ads 고객센터",
       "url": "https://support.google.com/google-ads/answer/2684489?hl=ko",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "퍼널",
     "note": "단계별 전환율을 이어 보면 퍼널이 됩니다."
    },
    {
     "term": "CPA",
     "note": "전환율이 오르면 같은 광고비로 CPA가 내려갑니다."
    }
   ],
   "confusable": [
    {
     "term": "CTR",
     "difference": "CTR은 노출 대비 클릭, 전환율은 클릭·방문 대비 목표 행동 비율입니다."
    }
   ]
  },
  {
   "id": "ctr",
   "term": "CTR",
   "original": "Click-Through Rate",
   "korean": "클릭률",
   "aliases": [
    "씨티알",
    "클릭스루율",
    "클릭 률"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "marketing",
      "data"
     ],
     "level": "입문",
     "importance": 5,
     "definition": "광고가 사람들에게 보인 횟수 가운데 실제로 클릭된 비율입니다. 광고 문구·이미지가 관심을 끄는지 가늠할 때 씁니다.",
     "formula": "CTR(%) = 클릭 수 ÷ 노출 수 × 100",
     "examples": [
      "새 배너 CTR이 기존보다 높게 나와서 소재를 이쪽으로 교체하려고요.",
      "CTR은 괜찮은데 전환이 안 나오면 랜딩 페이지 쪽을 봐야 할 것 같아요."
     ],
     "sources": [
      {
       "title": "클릭률(CTR): 정의 - Google Ads 고객센터",
       "url": "https://support.google.com/google-ads/answer/2615875?hl=ko",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "노출",
     "note": "CTR의 분모가 노출 수입니다."
    },
    {
     "term": "CPC",
     "note": "CTR과 함께 클릭 효율을 볼 때 씁니다."
    }
   ],
   "confusable": [
    {
     "term": "전환율",
     "difference": "CTR은 클릭까지, 전환율은 구매·가입 같은 목표 행동까지 봅니다."
    }
   ]
  },
  {
   "id": "impression",
   "term": "노출",
   "original": "Impression",
   "korean": "노출 수",
   "aliases": [
    "임프레션",
    "노출수",
    "Imp",
    "임프"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "marketing"
     ],
     "level": "입문",
     "importance": 4,
     "definition": "광고가 화면에 표시된 횟수입니다. 같은 사람에게 여러 번 보이면 그만큼 여러 번 집계되며, 실제로 봤는지·클릭했는지와는 별개입니다.",
     "formula": null,
     "examples": [
      "이번 캠페인 노출은 많은데 클릭이 적어서 타기팅을 좁혀 보려고요.",
      "노출 수 기준으로 과금되는 상품이라 CPM부터 확인해 주세요."
     ],
     "sources": [
      {
       "title": "노출수: 정의 - Google Ads 고객센터",
       "url": "https://support.google.com/google-ads/answer/6320?hl=ko",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "CTR",
     "note": "노출 수를 분모로 클릭률을 계산합니다."
    },
    {
     "term": "CPM",
     "note": "노출 1,000회 기준 비용입니다."
    }
   ],
   "confusable": [
    {
     "term": "도달",
     "difference": "노출은 표시 횟수, 도달은 광고를 본 고유 사용자 수입니다."
    }
   ]
  },
  {
   "id": "cpc",
   "term": "CPC",
   "original": "Cost Per Click",
   "korean": "클릭당 비용",
   "aliases": [
    "씨피씨",
    "클릭단가",
    "PPC",
    "클릭당비용"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "marketing"
     ],
     "level": "입문",
     "importance": 4,
     "definition": "광고가 한 번 클릭될 때 드는 비용, 또는 클릭이 일어날 때만 돈을 내는 과금 방식입니다. 광고주가 정한 최대 금액보다 실제 청구액이 낮은 경우가 많습니다.",
     "formula": "평균 CPC = 광고비 ÷ 클릭 수",
     "examples": [
      "키워드 경쟁이 심해져서 CPC가 지난달보다 꽤 올랐어요.",
      "CPC 입찰 상한을 조금 낮추고 전환 추이를 보겠습니다."
     ],
     "sources": [
      {
       "title": "클릭당비용(CPC): 정의 - Google Ads 고객센터",
       "url": "https://support.google.com/google-ads/answer/116495?hl=ko",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "CTR",
     "note": "클릭 효율과 클릭 비용을 함께 봐야 합니다."
    },
    {
     "term": "검색 광고",
     "note": "검색 광고는 대개 CPC 방식으로 과금됩니다."
    }
   ],
   "confusable": [
    {
     "term": "CPM",
     "difference": "CPC는 클릭 1회당, CPM은 노출 1,000회당 비용입니다."
    }
   ]
  },
  {
   "id": "cpm",
   "term": "CPM",
   "original": "Cost Per Mille",
   "korean": "1,000회 노출당 비용",
   "aliases": [
    "씨피엠",
    "천회노출당비용",
    "CPT",
    "노출당 단가"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "marketing"
     ],
     "level": "입문",
     "importance": 4,
     "definition": "광고가 1,000번 노출될 때마다 드는 비용, 또는 그 기준으로 돈을 내는 과금 방식입니다. 인지도를 넓히는 캠페인에서 주로 씁니다.",
     "formula": "CPM = 광고비 ÷ 노출 수 × 1,000",
     "examples": [
      "브랜딩 캠페인이라 CPM 과금으로 가고, 성과는 도달 기준으로 볼게요.",
      "같은 예산이면 CPM 낮은 매체에서 노출을 더 확보할 수 있어요."
     ],
     "sources": [
      {
       "title": "1,000회 노출당비용(CPM): 정의 - Google Ads 고객센터",
       "url": "https://support.google.com/google-ads/answer/6310?hl=ko",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "노출",
     "note": "CPM은 노출 수를 기준으로 비용을 봅니다."
    },
    {
     "term": "CPC",
     "note": "클릭 기준 비용과 비교해 매체를 고릅니다."
    }
   ],
   "confusable": [
    {
     "term": "CPC",
     "difference": "CPM은 노출 기준, CPC는 클릭 기준으로 돈을 냅니다."
    }
   ]
  },
  {
   "id": "roas",
   "term": "ROAS",
   "original": "Return On Ad Spend",
   "korean": "광고 투자수익률",
   "aliases": [
    "로아스",
    "광고수익률",
    "광고 대비 매출"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "marketing",
      "data"
     ],
     "level": "입문",
     "importance": 5,
     "definition": "광고비로 쓴 돈 대비 광고를 통해 얻은 매출(전환 가치)이 얼마인지 나타낸 값입니다. 보통 퍼센트로 쓰며, 500%면 광고비의 5배 매출이 났다는 뜻입니다.",
     "formula": "ROAS(%) = 광고로 발생한 전환 가치(매출) ÷ 광고비 × 100",
     "examples": [
      "이번 달 ROAS가 300% 아래로 떨어져서 효율 낮은 세트는 끄겠습니다.",
      "ROAS만 보지 말고 마진까지 넣어서 실제 이익이 나는지 봐 주세요."
     ],
     "sources": [
      {
       "title": "타겟 광고 투자수익(ROAS) 입찰에 대한 정보 - Google Ads 고객센터",
       "url": "https://support.google.com/google-ads/answer/6268637?hl=ko",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "CPA",
     "note": "전환 1건 비용 관점의 효율 지표입니다."
    },
    {
     "term": "매출",
     "note": "ROAS의 분자가 광고로 발생한 매출입니다."
    }
   ],
   "confusable": [
    {
     "term": "ROI",
     "difference": "ROAS는 매출 기준, ROI는 비용을 뺀 이익 기준으로 봅니다."
    }
   ]
  },
  {
   "id": "funnel",
   "term": "퍼널",
   "original": "Funnel",
   "korean": "유입경로",
   "aliases": [
    "퍼넬",
    "깔때기",
    "전환 퍼널",
    "구매 퍼널"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "marketing",
      "data",
      "pm"
     ],
     "level": "입문",
     "importance": 5,
     "definition": "사용자가 방문부터 구매·가입 같은 목표까지 거치는 단계를 순서대로 나눈 것입니다. 단계마다 몇 명이 남고 빠지는지 보면서 어디서 이탈이 큰지 찾습니다.",
     "formula": null,
     "examples": [
      "퍼널 보니까 장바구니에서 결제로 넘어가는 단계 이탈이 제일 커요.",
      "가입 퍼널을 앱이랑 웹으로 나눠서 다시 그려 볼게요."
     ],
     "sources": [
      {
       "title": "[GA4] 유입경로 탐색 분석 - 애널리틱스 고객센터",
       "url": "https://support.google.com/analytics/answer/9327974?hl=ko",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "전환율",
     "note": "단계 사이 비율이 전환율입니다."
    },
    {
     "term": "AARRR",
     "note": "퍼널을 단계별 지표로 나눈 틀입니다."
    }
   ],
   "confusable": [
    {
     "term": "리텐션",
     "difference": "퍼널은 한 번의 흐름 속 단계, 리텐션은 시간이 지나도 다시 오는지를 봅니다."
    }
   ]
  },
  {
   "id": "utm",
   "term": "UTM 매개변수",
   "original": "Urchin Tracking Module parameters",
   "korean": "UTM 매개변수",
   "aliases": [
    "UTM",
    "유티엠",
    "UTM 파라미터",
    "utm 태그",
    "캠페인 URL"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "marketing",
      "data"
     ],
     "level": "입문",
     "importance": 4,
     "definition": "링크 주소 뒤에 utm_source, utm_medium, utm_campaign 같은 값을 붙여 방문자가 어느 매체·캠페인에서 왔는지 분석 도구가 구분할 수 있게 하는 표시입니다. 값은 대소문자를 구분하므로 이름 규칙을 맞춰 써야 합니다.",
     "formula": null,
     "examples": [
      "뉴스레터 링크에 UTM 안 붙어서 유입이 다이렉트로 잡혔어요.",
      "utm_source 값은 소문자로 통일하기로 했으니 시트 규칙 따라 주세요."
     ],
     "sources": [
      {
       "title": "URL 작성 도구: 맞춤 URL을 사용한 캠페인 데이터 수집 - 애널리틱스 고객센터",
       "url": "https://support.google.com/analytics/answer/10917952?hl=ko",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "어트리뷰션",
     "note": "UTM 값이 성과를 채널에 나눠 주는 기초 데이터가 됩니다."
    },
    {
     "term": "오가닉 유입",
     "note": "UTM이 없는 유입과 구분해 볼 때 씁니다."
    }
   ],
   "confusable": [
    {
     "term": "딥링크",
     "difference": "UTM은 유입 출처 표시, 딥링크는 앱 안 특정 화면으로 보내는 링크입니다."
    }
   ]
  },
  {
   "id": "remarketing",
   "term": "리타깃팅",
   "original": "Retargeting",
   "korean": "리마케팅",
   "aliases": [
    "리타게팅",
    "리마케팅",
    "Remarketing",
    "재타기팅",
    "리타겟팅"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "marketing"
     ],
     "level": "입문",
     "importance": 4,
     "definition": "이미 사이트나 앱을 방문했거나 상품을 본 적 있는 사람에게 다시 광고를 보여 주는 방식입니다. 처음 보는 사람보다 관심이 높아 재방문이나 구매를 끌어내기 쉽습니다.",
     "formula": null,
     "examples": [
      "장바구니 담고 안 산 사람들 대상으로 리타깃팅 캠페인 돌려 봅시다.",
      "리타깃팅 빈도가 너무 높으면 피로도가 커지니 상한 걸어 둘게요."
     ],
     "sources": [
      {
       "title": "데이터 분류 기준 정보(리마케팅) - Google Ads 고객센터",
       "url": "https://support.google.com/google-ads/answer/2453998?hl=ko",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "장바구니 이탈률",
     "note": "이탈 고객이 리타깃팅의 주요 대상입니다."
    },
    {
     "term": "CRM 마케팅",
     "note": "보유 고객 데이터를 활용한다는 점이 비슷합니다."
    }
   ],
   "confusable": [
    {
     "term": "CRM 마케팅",
     "difference": "리타깃팅은 외부 광고 매체로, CRM 마케팅은 푸시·메일 같은 자체 채널로 다시 접촉합니다."
    }
   ]
  },
  {
   "id": "landing_page",
   "term": "랜딩 페이지",
   "original": "Landing Page",
   "korean": "방문 페이지",
   "aliases": [
    "랜딩페이지",
    "랜딩",
    "LP",
    "도착 페이지"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "marketing"
     ],
     "level": "입문",
     "importance": 3,
     "definition": "광고를 클릭했을 때 처음 열리는 페이지입니다. 광고 내용과 페이지 내용이 맞아야 이탈이 줄고 전환이 잘 일어납니다.",
     "formula": null,
     "examples": [
      "광고 문구는 할인인데 랜딩이 메인으로 가니까 이탈이 많아요. 이벤트 페이지로 바꿉시다.",
      "랜딩 페이지 A/B 테스트 결과 나오면 공유드릴게요."
     ],
     "sources": [
      {
       "title": "방문 페이지 - Google Ads 고객센터",
       "url": "https://support.google.com/google-ads/answer/14086?hl=ko",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "전환율",
     "note": "랜딩 페이지 품질이 전환율에 직접 영향을 줍니다."
    },
    {
     "term": "UTM 매개변수",
     "note": "랜딩 URL에 UTM을 붙여 유입을 구분합니다."
    }
   ],
   "confusable": [
    {
     "term": "딥링크",
     "difference": "랜딩 페이지는 웹 페이지, 딥링크는 앱 안 특정 화면으로 연결합니다."
    }
   ]
  },
  {
   "id": "cac",
   "term": "CAC",
   "original": "Customer Acquisition Cost",
   "korean": "고객 획득 비용",
   "aliases": [
    "씨에이씨",
    "고객획득비용",
    "획득 단가",
    "UAC"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "marketing",
      "data",
      "pm"
     ],
     "level": "실무",
     "importance": 5,
     "definition": "새 고객 한 명을 데려오는 데 평균적으로 든 마케팅·영업 비용입니다. 일정 기간의 획득 비용 합계를 그 기간 새 고객 수로 나눠 봅니다.",
     "formula": "CAC = 광고·영업에 쓴 총비용 ÷ 새로 획득한(첫 구매) 고객 수",
     "examples": [
      "유료 채널만 따로 보면 CAC가 꽤 높아서 오가닉 비중을 같이 봐야 해요.",
      "LTV가 CAC의 몇 배인지부터 보고 예산을 늘릴지 정하죠."
     ],
     "sources": [
      {
       "title": "Measuring marketing performance (Shopify Help Center)",
       "url": "https://help.shopify.com/en/manual/promoting-marketing/analyze-marketing/marketing-performance",
       "kind": "official",
       "checked_at": "2026-10-15"
      },
      {
       "title": "The Complete Guide to Customer Acquisition Cost - Amplitude",
       "url": "https://amplitude.com/explore/metrics/guide-to-customer-acquisition-cost",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "LTV",
     "note": "LTV와 CAC를 비교해 수익성을 판단합니다."
    },
    {
     "term": "CAC 회수 기간",
     "note": "CAC를 얼마 만에 회수하는지 봅니다."
    }
   ],
   "confusable": [
    {
     "term": "CPA",
     "difference": "CPA는 전환 1건 비용, CAC는 실제 고객 1명 획득에 든 전체 비용입니다."
    }
   ]
  },
  {
   "id": "ltv",
   "term": "LTV",
   "original": "Lifetime Value",
   "korean": "고객 생애 가치",
   "aliases": [
    "엘티브이",
    "CLV",
    "고객생애가치",
    "LTV 가치"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "marketing",
      "data",
      "pm"
     ],
     "level": "실무",
     "importance": 5,
     "definition": "고객 한 명이 서비스를 쓰는 동안 평균적으로 가져다줄 것으로 예상하는 매출(또는 이익)입니다. 고객 획득에 얼마까지 써도 되는지 판단하는 기준이 됩니다.",
     "formula": "LTV = 평균 구매 금액 × 구매 횟수 × 유지 기간 (앱 코호트 기준: 설치일부터 X일까지 누적 수익 ÷ 설치일 사용자 수)",
     "examples": [
      "LTV가 CAC의 3배는 넘어야 공격적으로 집행할 수 있을 것 같아요.",
      "첫 구매 쿠폰 받은 고객들 LTV가 낮게 나와서 혜택 구조를 다시 봐야겠어요."
     ],
     "sources": [
      {
       "title": "평생 가치 이해하기 - Google AdMob 고객센터",
       "url": "https://support.google.com/admob/answer/9736630?hl=ko",
       "kind": "official",
       "checked_at": "2026-10-15"
      },
      {
       "title": "What is LTV? - AppsFlyer glossary",
       "url": "https://www.appsflyer.com/glossary/ltv/",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "CAC",
     "note": "LTV와 비교해 획득 비용이 적정한지 봅니다."
    },
    {
     "term": "리텐션",
     "note": "오래 남을수록 LTV가 커집니다."
    }
   ],
   "confusable": [
    {
     "term": "ARPU",
     "difference": "ARPU는 일정 기간 사용자당 평균 매출, LTV는 전체 이용 기간 동안의 가치입니다."
    }
   ]
  },
  {
   "id": "attribution",
   "term": "어트리뷰션",
   "original": "Attribution",
   "korean": "기여 분석",
   "aliases": [
    "어트리뷰션",
    "기여도 분석",
    "성과 기여",
    "어트리뷰션 모델"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "marketing",
      "data"
     ],
     "level": "실무",
     "importance": 5,
     "definition": "구매나 가입 같은 성과가 났을 때 그 전에 거친 여러 광고·채널 가운데 어디에 얼마만큼 공을 돌릴지 정하는 일입니다. 마지막 클릭에 몰아주는지, 데이터로 나누는지 같은 규칙을 기여 모델이라고 합니다.",
     "formula": null,
     "examples": [
      "라스트 클릭 기준이라 검색 광고 성과가 과하게 잡히는 것 같아요.",
      "어트리뷰션 모델 바꾸면 채널별 ROAS가 달라지니까 기준 먼저 맞추죠."
     ],
     "sources": [
      {
       "title": "기여 분석 시작하기 - 애널리틱스 고객센터",
       "url": "https://support.google.com/analytics/answer/10596866?hl=ko",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "UTM 매개변수",
     "note": "UTM 값이 어트리뷰션의 출처 정보가 됩니다."
    },
    {
     "term": "증분 측정",
     "note": "어트리뷰션이 놓치는 실제 효과를 실험으로 확인합니다."
    }
   ],
   "confusable": [
    {
     "term": "증분 측정",
     "difference": "어트리뷰션은 일어난 전환의 공을 나누고, 증분 측정은 광고가 없었어도 났을 전환을 빼고 봅니다."
    }
   ]
  },
  {
   "id": "cpa",
   "term": "CPA",
   "original": "Cost Per Action",
   "korean": "전환당 비용",
   "aliases": [
    "씨피에이",
    "Cost Per Acquisition",
    "액션당비용",
    "전환단가"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "marketing"
     ],
     "level": "실무",
     "importance": 4,
     "definition": "구매·가입 같은 전환 한 건을 얻는 데 평균적으로 든 광고비입니다. 목표 CPA를 정해 두고 입찰을 자동으로 맞추기도 합니다.",
     "formula": "CPA = 광고비 ÷ 전환 수",
     "examples": [
      "가입 CPA가 목표보다 높아서 전환 잘 나오는 소재 위주로 예산 옮길게요.",
      "타겟 CPA 입찰로 바꾼 뒤 학습 기간 끝나면 다시 비교해 봐요."
     ],
     "sources": [
      {
       "title": "타겟 CPA 입찰 정보 - Google Ads 고객센터",
       "url": "https://support.google.com/google-ads/answer/6268632?hl=ko",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "전환율",
     "note": "전환율이 오르면 CPA가 내려갑니다."
    },
    {
     "term": "ROAS",
     "note": "매출 기준 효율과 함께 봅니다."
    }
   ],
   "confusable": [
    {
     "term": "CAC",
     "difference": "CPA는 광고 전환 1건 비용, CAC는 고객 1명 획득에 든 전체 비용입니다."
    }
   ]
  },
  {
   "id": "seo",
   "term": "SEO",
   "original": "Search Engine Optimization",
   "korean": "검색엔진 최적화",
   "aliases": [
    "에스이오",
    "검색 최적화",
    "검색엔진최적화"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "marketing"
     ],
     "level": "실무",
     "importance": 4,
     "definition": "검색엔진이 사이트 내용을 잘 이해하고 사용자가 검색 결과에서 사이트를 찾아 들어오도록 페이지와 콘텐츠를 다듬는 일입니다. 광고비 없이 검색 유입을 늘리는 것이 목표입니다.",
     "formula": null,
     "examples": [
      "상품 상세페이지 제목에 검색어가 안 들어가 있어서 SEO 관점에서 손볼게요.",
      "SEO 효과는 몇 주 걸리니까 검색 광고랑 같이 가져가죠."
     ],
     "sources": [
      {
       "title": "검색엔진 최적화(SEO) 기본 가이드 - Google 검색 센터",
       "url": "https://developers.google.com/search/docs/fundamentals/seo-starter-guide?hl=ko",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "오가닉 유입",
     "note": "SEO는 오가닉 검색 유입을 늘리는 방법입니다."
    },
    {
     "term": "검색 광고",
     "note": "같은 검색 결과 화면을 두고 함께 운영합니다."
    }
   ],
   "confusable": [
    {
     "term": "검색 광고",
     "difference": "SEO는 비용 없이 자연 노출을, 검색 광고는 돈을 내고 광고 자리를 얻습니다."
    }
   ]
  },
  {
   "id": "sem",
   "term": "검색 광고",
   "original": "Search Engine Marketing / Search Ads",
   "korean": "검색 광고",
   "aliases": [
    "SEM",
    "에스이엠",
    "키워드 광고",
    "검색광고",
    "SA"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "marketing"
     ],
     "level": "실무",
     "importance": 3,
     "definition": "사람들이 검색창에 특정 키워드를 입력했을 때 검색 결과에 광고가 함께 보이도록 하는 광고입니다. 이미 찾고 있는 사람에게 보여 주기 때문에 구매 의도가 높은 편입니다.",
     "formula": null,
     "examples": [
      "브랜드 키워드 검색 광고는 CPC가 낮으니까 계속 켜 둡시다.",
      "검색어 보고서 보고 관련 없는 키워드는 제외 키워드로 넣을게요."
     ],
     "sources": [
      {
       "title": "검색 캠페인 만들기 - Google Ads 고객센터",
       "url": "https://support.google.com/google-ads/answer/9510373?hl=ko",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "CPC",
     "note": "검색 광고는 주로 클릭당 과금입니다."
    },
    {
     "term": "SEO",
     "note": "같은 검색 결과에서 자연 노출을 담당합니다."
    }
   ],
   "confusable": [
    {
     "term": "SEO",
     "difference": "검색 광고는 유료 노출, SEO는 무료 자연 노출입니다."
    }
   ]
  },
  {
   "id": "crm_marketing",
   "term": "CRM 마케팅",
   "original": "CRM Marketing",
   "korean": "고객 관계 관리 마케팅",
   "aliases": [
    "씨알엠 마케팅",
    "CRM마케팅",
    "고객관리 마케팅",
    "리텐션 마케팅"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "marketing",
      "cx"
     ],
     "level": "실무",
     "importance": 4,
     "definition": "이미 가입했거나 구매한 고객의 데이터를 바탕으로 그룹을 나누고, 앱 푸시·문자·이메일 같은 자체 채널로 맞춤 메시지를 보내 재구매와 이용을 늘리는 마케팅입니다.",
     "formula": null,
     "examples": [
      "30일 미구매 고객 세그먼트에 CRM 메시지로 쿠폰 보내 볼게요.",
      "CRM 캠페인은 발송량보다 실제 구매 전환을 기준으로 평가합시다."
     ],
     "sources": [
      {
       "title": "Managing customer segments (Shopify Help Center)",
       "url": "https://help.shopify.com/en/manual/customers/customer-segmentation/manage-customer-segments",
       "kind": "official",
       "checked_at": "2026-10-15"
      },
      {
       "title": "How to Use Your CRM to Power Your Marketing - HubSpot",
       "url": "https://blog.hubspot.com/marketing/crm-tips",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "푸시 알림",
     "note": "CRM 마케팅의 대표 발송 채널입니다."
    },
    {
     "term": "리텐션",
     "note": "CRM 마케팅의 주된 목표가 리텐션입니다."
    }
   ],
   "confusable": [
    {
     "term": "리타깃팅",
     "difference": "CRM은 자체 채널로, 리타깃팅은 외부 광고 매체로 다시 접촉합니다."
    }
   ]
  },
  {
   "id": "push_notification",
   "term": "푸시 알림",
   "original": "Push Notification",
   "korean": "푸시 알림",
   "aliases": [
    "푸시",
    "앱 푸시",
    "앱푸시",
    "Push"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "marketing",
      "pm"
     ],
     "level": "실무",
     "importance": 3,
     "definition": "앱이 사용자 휴대폰이나 PC 화면에 띄우는 클릭 가능한 알림 메시지입니다. 앱을 열어 두지 않아도 받을 수 있어 재방문을 유도할 때 씁니다.",
     "formula": null,
     "examples": [
      "저녁 8시 푸시 오픈율이 제일 높아서 발송 시간을 옮기려고요.",
      "푸시 너무 자주 보내면 알림 끄는 사람이 늘어서 주 2회로 제한해요."
     ],
     "sources": [
      {
       "title": "Firebase Cloud Messaging (Firebase 문서)",
       "url": "https://firebase.google.com/docs/cloud-messaging",
       "kind": "official",
       "checked_at": "2026-10-15"
      },
      {
       "title": "What are push notifications? - AppsFlyer mobile glossary",
       "url": "https://www.appsflyer.com/glossary/push-notifications/",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "CRM 마케팅",
     "note": "푸시는 CRM 마케팅의 주요 채널입니다."
    },
    {
     "term": "딥링크",
     "note": "푸시를 누르면 딥링크로 특정 화면에 보냅니다."
    }
   ],
   "confusable": [
    {
     "term": "인앱 메시지",
     "difference": "푸시는 앱 밖에서, 인앱 메시지는 앱을 쓰는 중에 보입니다."
    }
   ]
  },
  {
   "id": "aarrr",
   "term": "AARRR",
   "original": "Acquisition, Activation, Retention, Referral, Revenue",
   "korean": "해적 지표",
   "aliases": [
    "아르르",
    "해적지표",
    "Pirate Metrics",
    "AARRR 프레임워크"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "marketing",
      "pm"
     ],
     "level": "실무",
     "importance": 4,
     "definition": "사용자의 흐름을 획득, 활성화, 유지, 추천, 수익 다섯 단계로 나눠 단계마다 지표를 보는 틀입니다. 데이브 매클루어가 제안했고 첫 글자를 따 해적 지표라고도 부릅니다.",
     "formula": null,
     "examples": [
      "AARRR로 보면 우리는 획득보다 활성화 단계 이탈이 더 문제예요.",
      "이번 분기 OKR은 AARRR 중 리텐션 단계에 집중합시다."
     ],
     "sources": [
      {
       "title": "AARRR: Come Aboard the Pirate Metrics Framework - Amplitude",
       "url": "https://amplitude.com/blog/pirate-metrics-framework",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "퍼널",
     "note": "AARRR은 사용자 퍼널을 다섯 단계로 정리한 것입니다."
    },
    {
     "term": "리텐션",
     "note": "AARRR의 세 번째 단계입니다."
    }
   ],
   "confusable": [
    {
     "term": "퍼널",
     "difference": "퍼널은 특정 목표까지의 단계, AARRR은 사업 전체 성장 단계를 나눈 틀입니다."
    }
   ]
  },
  {
   "id": "growth_hacking",
   "term": "그로스 해킹",
   "original": "Growth Hacking",
   "korean": "그로스 해킹",
   "aliases": [
    "그로스해킹",
    "그로스 해커",
    "성장 해킹",
    "그로스"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "marketing"
     ],
     "level": "실무",
     "importance": 3,
     "definition": "적은 비용으로 빠르게 사용자와 매출을 늘리기 위해 마케팅, 제품 개선, 데이터 분석을 묶어 작은 실험을 반복하는 방식입니다. 무엇이 효과가 있는지 테스트로 확인하는 것이 핵심입니다.",
     "formula": null,
     "examples": [
      "추천인 보상 구조를 바꿔서 이번 주 그로스 실험으로 돌려 볼게요.",
      "그로스 해킹이라고 편법 쓰자는 게 아니라 가설-실험-검증을 빨리 돌리자는 거예요."
     ],
     "sources": [
      {
       "title": "Growth hacking - Optimizely glossary",
       "url": "https://www.optimizely.com/optimization-glossary/growth-hacking",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "AARRR",
     "note": "그로스 실험을 어느 단계에 할지 정할 때 씁니다."
    },
    {
     "term": "바이럴 계수",
     "note": "추천 실험의 성과 지표입니다."
    }
   ],
   "confusable": [
    {
     "term": "퍼포먼스 마케팅",
     "difference": "퍼포먼스 마케팅은 광고 효율 중심, 그로스 해킹은 제품까지 포함한 실험 중심입니다."
    }
   ]
  },
  {
   "id": "organic",
   "term": "오가닉 유입",
   "original": "Organic Traffic / Organic Install",
   "korean": "자연 유입",
   "aliases": [
    "오가닉",
    "오가닉유입",
    "자연 유입",
    "Organic",
    "논페이드"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "marketing",
      "data"
     ],
     "level": "실무",
     "importance": 3,
     "definition": "광고 같은 마케팅 활동 없이 사용자가 검색, 앱스토어, 입소문 등으로 스스로 찾아온 유입입니다. 광고를 봤더라도 측정 기간이 지난 뒤 들어오면 오가닉으로 잡히기도 합니다.",
     "formula": null,
     "examples": [
      "광고 끈 주에도 오가닉 설치가 꽤 유지돼서 브랜드 인지도가 쌓인 것 같아요.",
      "오가닉 비중이 늘면 전체 CAC는 낮아 보이니까 유료만 따로도 봐 주세요."
     ],
     "sources": [
      {
       "title": "기본 채널 그룹 - 애널리틱스 고객센터",
       "url": "https://support.google.com/analytics/answer/9756891?hl=ko",
       "kind": "official",
       "checked_at": "2026-10-15"
      },
      {
       "title": "What is an organic install? - AppsFlyer mobile glossary",
       "url": "https://www.appsflyer.com/glossary/organic-install/",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "SEO",
     "note": "검색 오가닉 유입을 늘리는 방법입니다."
    },
    {
     "term": "어트리뷰션",
     "note": "어느 매체에도 공이 안 돌아가면 오가닉으로 분류됩니다."
    }
   ],
   "confusable": [
    {
     "term": "다이렉트 유입",
     "difference": "오가닉은 마케팅 없이 온 유입 전반, 다이렉트는 주소를 직접 입력하는 등 출처가 없는 유입입니다."
    }
   ]
  },
  {
   "id": "deeplink",
   "term": "딥링크",
   "original": "Deep Link",
   "korean": "딥 링크",
   "aliases": [
    "딥 링크",
    "Deeplink",
    "디퍼드 딥링크",
    "앱 링크"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "marketing",
      "pm"
     ],
     "level": "실무",
     "importance": 3,
     "definition": "누르면 앱 첫 화면이 아니라 앱 안의 특정 상품·이벤트 화면으로 바로 보내 주는 링크입니다. 앱이 없으면 설치 뒤 원래 화면으로 이어 주는 방식은 디퍼드 딥링크라고 합니다.",
     "formula": null,
     "examples": [
      "푸시에 딥링크 안 걸려서 홈으로 가니까 전환이 안 나왔어요.",
      "신규 유저는 앱이 없으니 디퍼드 딥링크로 설정해 주세요."
     ],
     "sources": [
      {
       "title": "About deep links (Android Developers)",
       "url": "https://developer.android.com/training/app-links",
       "kind": "official",
       "checked_at": "2026-10-15"
      },
      {
       "title": "What is deep linking? - AppsFlyer mobile glossary",
       "url": "https://www.appsflyer.com/glossary/deep-linking/",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "푸시 알림",
     "note": "푸시 클릭 시 딥링크로 화면을 연결합니다."
    },
    {
     "term": "CPI",
     "note": "앱 설치 캠페인에서 딥링크로 첫 경험을 개선합니다."
    }
   ],
   "confusable": [
    {
     "term": "랜딩 페이지",
     "difference": "딥링크는 앱 안 화면, 랜딩 페이지는 웹 페이지로 연결합니다."
    }
   ]
  },
  {
   "id": "cpi",
   "term": "CPI",
   "original": "Cost Per Install",
   "korean": "설치당 비용",
   "aliases": [
    "씨피아이",
    "설치단가",
    "eCPI",
    "인스톨당 비용"
   ],
   "senses": [
    {
     "industries": [
      "platform"
     ],
     "roles": [
      "marketing"
     ],
     "level": "실무",
     "importance": 3,
     "definition": "광고를 통해 앱이 한 번 설치될 때 드는 비용, 또는 설치가 일어날 때마다 돈을 내는 과금 방식입니다.",
     "formula": "CPI = 광고비 ÷ 광고로 발생한 앱 설치 수",
     "examples": [
      "CPI는 낮은데 설치 후 가입률이 낮아서 매체 품질을 다시 봐야겠어요.",
      "국가별 CPI 차이가 커서 예산 배분을 나눠 볼게요."
     ],
     "sources": [
      {
       "title": "앱 캠페인의 입찰 정보 - Google Ads 고객센터",
       "url": "https://support.google.com/google-ads/answer/7100895?hl=ko",
       "kind": "official",
       "checked_at": "2026-10-15"
      },
      {
       "title": "What is Cost per install (CPI)? - AppsFlyer glossary",
       "url": "https://www.appsflyer.com/glossary/cost-per-install/",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "CAC",
     "note": "설치 이후 실제 고객이 되기까지 비용은 CAC로 봅니다."
    },
    {
     "term": "오가닉 유입",
     "note": "광고 없이 생긴 설치는 CPI 계산에서 뺍니다."
    }
   ],
   "confusable": [
    {
     "term": "CPA",
     "difference": "CPI는 설치 1건, CPA는 가입·구매 같은 전환 1건 비용입니다."
    }
   ]
  },
  {
   "id": "k_factor",
   "term": "바이럴 계수",
   "original": "K-factor (Viral Coefficient)",
   "korean": "바이럴 계수",
   "aliases": [
    "K-팩터",
    "케이팩터",
    "K factor",
    "바이럴 지수"
   ],
   "senses": [
    {
     "industries": [
      "platform"
     ],
     "roles": [
      "marketing"
     ],
     "level": "심화",
     "importance": 3,
     "definition": "기존 사용자 한 명이 평균적으로 몇 명의 새 사용자를 데려오는지 나타내는 값입니다. 1보다 크면 사용자가 스스로 불어나는 구조라고 봅니다.",
     "formula": "K = 사용자 1명당 평균 초대 수 × 초대받은 사람의 가입 전환율",
     "examples": [
      "친구 초대 리워드 올린 뒤 K-factor가 0.3에서 얼마나 오르는지 볼게요.",
      "바이럴 계수가 1 넘기는 건 어려우니 광고랑 같이 가야 해요."
     ],
     "sources": [
      {
       "title": "What is K-factor? - AppsFlyer marketing glossary",
       "url": "https://www.appsflyer.com/glossary/k-factor/",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "AARRR",
     "note": "추천(Referral) 단계 지표입니다."
    },
    {
     "term": "CAC",
     "note": "바이럴 유입이 늘면 CAC가 낮아집니다."
    }
   ],
   "confusable": [
    {
     "term": "NPS",
     "difference": "NPS는 추천 의향 설문 점수, 바이럴 계수는 실제 초대로 생긴 신규 사용자 수 기준입니다."
    }
   ]
  },
  {
   "id": "incrementality",
   "term": "증분 측정",
   "original": "Incrementality",
   "korean": "증분 측정",
   "aliases": [
    "인크리멘탈리티",
    "리프트 테스트",
    "Lift test",
    "증분 효과",
    "전환 상승도"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "marketing",
      "data"
     ],
     "level": "심화",
     "importance": 4,
     "definition": "광고를 본 그룹과 보지 않은 그룹을 비교해서, 광고가 없었어도 일어났을 전환을 빼고 광고 때문에 추가로 생긴 성과만 재는 방법입니다.",
     "formula": "증분 전환 = 광고 노출 그룹 전환 수 − 통제 그룹 전환 수, 증분 CPA = 광고비 ÷ 증분 전환 수",
     "examples": [
      "리타깃팅 ROAS가 너무 좋게 나와서 증분 측정으로 진짜 효과인지 확인해 봐야겠어요.",
      "리프트 테스트 결과 증분 전환이 생각보다 작아서 예산을 줄이겠습니다."
     ],
     "sources": [
      {
       "title": "전환 상승도에 대한 정보 - Google Ads 고객센터",
       "url": "https://support.google.com/google-ads/answer/12003020?hl=ko",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "홀드아웃 그룹",
     "note": "증분 측정에서 비교 기준이 되는 그룹입니다."
    },
    {
     "term": "어트리뷰션",
     "note": "어트리뷰션 결과를 실험으로 검증할 때 씁니다."
    }
   ],
   "confusable": [
    {
     "term": "어트리뷰션",
     "difference": "어트리뷰션은 이미 난 전환의 공을 나누고, 증분 측정은 광고가 만든 추가분만 셉니다."
    }
   ]
  },
  {
   "id": "mmm",
   "term": "마케팅 믹스 모델링",
   "original": "Marketing Mix Modeling",
   "korean": "마케팅 믹스 모델링",
   "aliases": [
    "MMM",
    "엠엠엠",
    "미디어 믹스 모델링",
    "마케팅믹스모델"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "marketing",
      "data"
     ],
     "level": "심화",
     "importance": 3,
     "definition": "여러 해의 광고비, 가격, 계절 같은 내외부 요인과 매출 데이터를 통계 모델로 분석해 채널별로 성과에 얼마나 기여했는지 추정하는 방법입니다. 사용자 단위 추적 없이 전체 집계 데이터로 봅니다.",
     "formula": null,
     "examples": [
      "쿠키 추적이 약해져서 MMM으로 채널 기여도를 같이 보려고요.",
      "MMM 결과는 분기 단위 예산 배분 참고용으로 쓰고, 일 단위 운영은 기존 지표로 하죠."
     ],
     "sources": [
      {
       "title": "An introduction to Meridian (Google for Developers)",
       "url": "https://developers.google.com/meridian/docs/basics/about-the-project",
       "kind": "official",
       "checked_at": "2026-10-15"
      },
      {
       "title": "What Is Media Mix Modeling (MMM)? - AppsFlyer glossary",
       "url": "https://www.appsflyer.com/glossary/media-mix-modeling/",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "어트리뷰션",
     "note": "사용자 단위 기여 분석과 보완해서 씁니다."
    },
    {
     "term": "증분 측정",
     "note": "실험 결과로 MMM을 보정하기도 합니다."
    }
   ],
   "confusable": [
    {
     "term": "어트리뷰션",
     "difference": "MMM은 집계 데이터 기반 통계 모델, 어트리뷰션은 개별 사용자 경로 기반입니다."
    }
   ]
  },
  {
   "id": "holdout",
   "term": "홀드아웃 그룹",
   "original": "Holdout Group",
   "korean": "홀드아웃 그룹",
   "aliases": [
    "홀드아웃",
    "통제 그룹",
    "컨트롤 그룹",
    "대조군",
    "Holdout"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "marketing",
      "data"
     ],
     "level": "심화",
     "importance": 3,
     "definition": "효과를 비교하려고 일부러 광고·메시지·새 기능을 보여 주지 않고 남겨 두는 사용자 그룹입니다. 이 그룹과 노출 그룹의 차이로 실제 효과를 잽니다.",
     "formula": null,
     "examples": [
      "CRM 캠페인마다 10%는 홀드아웃으로 빼 두고 구매율 차이를 봅시다.",
      "홀드아웃 그룹에 다른 채널로 쿠폰이 나가면 비교가 깨지니 조심해 주세요."
     ],
     "sources": [
      {
       "title": "Holdout groups - Optimizely glossary",
       "url": "https://www.optimizely.com/optimization-glossary/holdout-groups",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      },
      {
       "title": "전환 상승도에 대한 정보 - Google Ads 고객센터",
       "url": "https://support.google.com/google-ads/answer/12003020?hl=ko",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "증분 측정",
     "note": "홀드아웃 그룹이 증분 측정의 비교 기준입니다."
    },
    {
     "term": "CRM 마케팅",
     "note": "CRM 메시지 효과를 볼 때 자주 씁니다."
    }
   ],
   "confusable": [
    {
     "term": "A/B 테스트",
     "difference": "A/B 테스트는 여러 안을 비교하고, 홀드아웃은 아무것도 받지 않은 그룹과 비교합니다."
    }
   ]
  },
  {
   "id": "payback_period",
   "term": "CAC 회수 기간",
   "original": "CAC Payback Period",
   "korean": "CAC 회수 기간",
   "aliases": [
    "페이백 기간",
    "페이백",
    "Payback period",
    "회수기간"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "marketing"
     ],
     "level": "심화",
     "importance": 3,
     "definition": "고객 한 명을 데려오는 데 쓴 비용(CAC)을 그 고객이 매달 남기는 이익으로 다시 벌어들이기까지 걸리는 개월 수입니다. 짧을수록 투자금이 빨리 돌아옵니다.",
     "formula": "CAC 회수 기간(개월) = CAC ÷ 고객 1명당 월평균 매출총이익",
     "examples": [
      "신규 채널은 CAC가 높아서 회수 기간이 1년 넘게 나와요.",
      "페이백 6개월 안쪽인 채널부터 예산 늘리는 걸로 정리하죠."
     ],
     "sources": [
      {
       "title": "How To Calculate and Shorten Your CAC Payback Period - Shopify",
       "url": "https://www.shopify.com/blog/cac-payback-period",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "CAC",
     "note": "회수 기간의 분자입니다."
    },
    {
     "term": "LTV",
     "note": "장기 수익성은 LTV와 함께 봅니다."
    }
   ],
   "confusable": [
    {
     "term": "LTV/CAC 비율",
     "difference": "회수 기간은 언제 본전을 찾는지, LTV/CAC는 전체 기간 동안 몇 배를 버는지 봅니다."
    }
   ]
  },
  {
   "id": "aov",
   "term": "객단가",
   "original": "Average Order Value",
   "korean": "평균 주문 금액",
   "aliases": [
    "AOV",
    "에이오브이",
    "주문당 평균 금액",
    "객단가"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce"
     ],
     "roles": [
      "marketing",
      "data",
      "pm"
     ],
     "level": "입문",
     "importance": 5,
     "definition": "주문 한 건에 고객이 평균적으로 쓰는 금액입니다. 같은 방문·주문 수에서 매출을 늘리려면 객단가를 올리는 방법을 찾습니다.",
     "formula": "AOV = (총매출 − 할인) ÷ 주문 수 (주문 뒤 반품·수정 등 조정은 제외)",
     "examples": [
      "무료배송 기준을 올린 뒤 객단가가 조금 올랐어요.",
      "객단가 올리려고 함께 사면 좋은 상품 추천 영역을 넣어 볼게요."
     ],
     "sources": [
      {
       "title": "Measuring marketing performance (Shopify Help Center)",
       "url": "https://help.shopify.com/en/manual/promoting-marketing/analyze-marketing/marketing-performance",
       "kind": "official",
       "checked_at": "2026-10-15"
      },
      {
       "title": "Analytics fields (Shopify Help Center)",
       "url": "https://help.shopify.com/en/manual/reports-and-analytics/shopify-reports/report-types/analytics-fields",
       "kind": "official",
       "checked_at": "2026-10-15"
      },
      {
       "title": "Average Order Value: Formula and 7 Ways - Shopify",
       "url": "https://www.shopify.com/blog/average-order-value",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "크로스셀",
     "note": "함께 구매를 늘려 객단가를 올립니다."
    },
    {
     "term": "매출",
     "note": "매출 = 주문 수 × 객단가로 나눠 볼 수 있습니다."
    }
   ],
   "confusable": [
    {
     "term": "ARPU",
     "difference": "객단가는 주문 1건 기준, ARPU는 사용자 1명 기준 평균 매출입니다."
    }
   ]
  },
  {
   "id": "cart_abandonment",
   "term": "장바구니 이탈률",
   "original": "Cart Abandonment Rate",
   "korean": "장바구니 이탈률",
   "aliases": [
    "장바구니 포기율",
    "카트 이탈률",
    "장바구니이탈률",
    "Cart abandonment"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce"
     ],
     "roles": [
      "marketing",
      "data",
      "pm"
     ],
     "level": "실무",
     "importance": 4,
     "definition": "장바구니에 상품을 담은 사람 가운데 결제를 마치지 않고 떠난 비율입니다. 배송비, 결제 수단, 복잡한 절차 등이 주요 원인으로 꼽힙니다.",
     "formula": "장바구니 이탈률(%) = 이탈한 장바구니 수 ÷ 생성된 장바구니 수 × 100",
     "examples": [
      "배송비가 결제 단계에서 처음 보이니까 장바구니 이탈률이 높은 것 같아요.",
      "이탈 고객에게 1시간 뒤 리마인드 푸시 보내는 실험 해 봅시다."
     ],
     "sources": [
      {
       "title": "[GA4] 장바구니 이탈자 잠재고객 설정하기 - 애널리틱스 고객센터",
       "url": "https://support.google.com/analytics/answer/13286448?hl=ko",
       "kind": "official",
       "checked_at": "2026-10-15"
      },
      {
       "title": "How To Reduce Shopping Cart Abandonment - Shopify",
       "url": "https://www.shopify.com/enterprise/blog/44272899-how-to-reduce-shopping-cart-abandonment-by-optimizing-the-checkout",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "퍼널",
     "note": "장바구니→결제 단계 이탈을 수치로 본 것입니다."
    },
    {
     "term": "리타깃팅",
     "note": "이탈 고객을 다시 데려올 때 씁니다."
    }
   ],
   "confusable": [
    {
     "term": "결제 이탈률",
     "difference": "장바구니 이탈은 담기 이후 전체, 결제 이탈은 결제를 시작한 뒤 떠난 경우만 셉니다."
    }
   ]
  },
  {
   "id": "cross_sell",
   "term": "크로스셀",
   "original": "Cross-selling",
   "korean": "교차 판매",
   "aliases": [
    "크로스 셀링",
    "크로스셀링",
    "교차판매",
    "Cross-sell"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce"
     ],
     "roles": [
      "marketing"
     ],
     "level": "실무",
     "importance": 3,
     "definition": "고객이 사려는 상품과 함께 쓰면 좋은 다른 관련 상품을 추천해 같이 사게 하는 판매 방식입니다. 예를 들어 노트북을 사는 고객에게 마우스나 가방을 권하는 식입니다.",
     "formula": null,
     "examples": [
      "상세페이지 하단에 같이 산 상품 영역 넣어서 크로스셀 늘려 볼게요.",
      "크로스셀 추천이 너무 많으면 결제까지 방해되니 3개만 노출합시다."
     ],
     "sources": [
      {
       "title": "Customize product recommendations with Shopify Search & Discovery (Shopify Help Center)",
       "url": "https://help.shopify.com/en/manual/online-store/storefront-search/search-and-discovery-recommendations",
       "kind": "official",
       "checked_at": "2026-10-15"
      },
      {
       "title": "Cross Sell vs Upsell: Differences and Examples - Shopify",
       "url": "https://www.shopify.com/ca/blog/upselling-and-cross-selling",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "객단가",
     "note": "크로스셀로 주문 금액이 올라갑니다."
    },
    {
     "term": "CRM 마케팅",
     "note": "구매 후 관련 상품 추천 메시지로 쓰입니다."
    }
   ],
   "confusable": [
    {
     "term": "업셀",
     "difference": "크로스셀은 다른 관련 상품, 업셀은 같은 상품의 더 비싼 버전을 권합니다."
    }
   ]
  },
  {
   "id": "dau",
   "term": "DAU",
   "original": "Daily Active Users",
   "korean": "일간 활성 사용자 수",
   "aliases": [
    "디에이유",
    "일 활성 사용자",
    "일간활성사용자",
    "Daily Active User"
   ],
   "senses": [
    {
     "industries": [
      "platform"
     ],
     "roles": [
      "data",
      "marketing",
      "pm"
     ],
     "level": "입문",
     "importance": 5,
     "definition": "하루 동안 서비스에 들어와 활동한 사용자를 중복 없이 센 숫자입니다. 무엇을 '활동'으로 볼지(앱 실행, 특정 이벤트 등)는 회사마다 정해서 씁니다.",
     "formula": null,
     "examples": [
      "이번 주 DAU가 주말에만 떨어지는데, 활성 기준을 앱 실행으로 잡은 건지 확인해 볼게요.",
      "신규 기능 출시 후 DAU 변화는 대시보드 첫 줄에 올려 주세요."
     ],
     "sources": [
      {
       "title": "You're Measuring Daily Active Users Wrong (Amplitude 블로그)",
       "url": "https://www.amplitude.com/blog/measuring-active-users",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      },
      {
       "title": "애널리틱스 측정기준 및 측정항목 - 애널리틱스 고객센터",
       "url": "https://support.google.com/analytics/answer/9143382?hl=ko",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "MAU",
     "note": "DAU와 함께 보면 사용자가 얼마나 자주 돌아오는지 알 수 있습니다."
    },
    {
     "term": "스티키니스",
     "note": "DAU를 MAU로 나눈 값으로 이용 빈도를 봅니다."
    }
   ],
   "confusable": [
    {
     "term": "방문수(세션 수)",
     "difference": "DAU는 사람 수, 세션 수는 방문 횟수라 한 사람이 여러 번 오면 세션만 늘어납니다."
    }
   ]
  },
  {
   "id": "mau",
   "term": "MAU",
   "original": "Monthly Active Users",
   "korean": "월간 활성 사용자 수",
   "aliases": [
    "엠에이유",
    "월 활성 사용자",
    "월간활성사용자",
    "Monthly Active User"
   ],
   "senses": [
    {
     "industries": [
      "platform"
     ],
     "roles": [
      "data",
      "marketing",
      "pm"
     ],
     "level": "입문",
     "importance": 5,
     "definition": "한 달(보통 최근 30일) 동안 서비스에서 한 번 이상 활동한 사용자를 중복 없이 센 숫자입니다. 서비스 규모를 보여 주는 대표 지표입니다.",
     "formula": null,
     "examples": [
      "MAU는 늘었는데 DAU가 그대로면 가끔 들르는 사용자만 늘어난 거예요.",
      "투자 자료에는 MAU 기준일을 꼭 같이 적어 주세요."
     ],
     "sources": [
      {
       "title": "You're Measuring Daily Active Users Wrong (Amplitude 블로그)",
       "url": "https://www.amplitude.com/blog/measuring-active-users",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      },
      {
       "title": "애널리틱스 측정기준 및 측정항목 - 애널리틱스 고객센터",
       "url": "https://support.google.com/analytics/answer/9143382?hl=ko",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "DAU",
     "note": "MAU와 짝으로 써서 이용 빈도를 계산합니다."
    },
    {
     "term": "리텐션",
     "note": "MAU가 유지되려면 기존 사용자가 계속 돌아와야 합니다."
    }
   ],
   "confusable": [
    {
     "term": "가입자 수",
     "difference": "가입자 수는 누적 계정 수이고, MAU는 그 달에 실제로 활동한 사람만 셉니다."
    }
   ]
  },
  {
   "id": "kpi",
   "term": "KPI",
   "original": "Key Performance Indicator",
   "korean": "핵심 성과 지표",
   "aliases": [
    "케이피아이",
    "핵심성과지표",
    "핵심 지표",
    "성과 지표"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "data",
      "pm",
      "marketing",
      "cx"
     ],
     "level": "입문",
     "importance": 5,
     "definition": "정해 둔 목표에 얼마나 다가가고 있는지를 보여 주는 핵심 숫자입니다. 현재 값, 목표 값, 기준선을 함께 두고 앞서는지 뒤처지는지 판단합니다.",
     "formula": null,
     "examples": [
      "이번 분기 우리 팀 KPI는 재구매율 하나로 좁히죠.",
      "KPI 목표치가 없으면 대시보드에서 잘하고 있는지 판단이 안 돼요."
     ],
     "sources": [
      {
       "title": "핵심 성과 지표(KPI) 시각화 - Power BI | Microsoft Learn",
       "url": "https://learn.microsoft.com/ko-kr/power-bi/visuals/power-bi-visualization-kpi",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "대시보드",
     "note": "KPI는 보통 대시보드 맨 위에 모아 둡니다."
    },
    {
     "term": "OKR",
     "note": "목표(O)의 달성 정도를 KPI 같은 숫자로 측정합니다."
    }
   ],
   "confusable": [
    {
     "term": "측정항목(Metric)",
     "difference": "측정항목은 모든 숫자를 말하고, KPI는 그중 목표와 직접 연결된 핵심 숫자입니다."
    }
   ]
  },
  {
   "id": "metric_dimension",
   "term": "측정기준과 측정항목",
   "original": "Dimension and Metric",
   "korean": "디멘션과 메트릭",
   "aliases": [
    "디멘션",
    "메트릭",
    "Dimension",
    "Metric",
    "측정기준",
    "측정항목"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "data"
     ],
     "level": "입문",
     "importance": 4,
     "definition": "측정기준은 국가·기기·페이지처럼 데이터를 나누는 속성이고, 측정항목은 세션 수·매출처럼 셀 수 있는 숫자입니다. 보고서는 보통 측정기준을 행에, 측정항목을 열에 놓고 봅니다.",
     "formula": null,
     "examples": [
      "측정기준에 기기 카테고리를 넣고 측정항목은 전환수로 뽑아 주세요.",
      "이 측정기준과 측정항목은 범위가 달라서 같이 쓰면 숫자가 이상하게 나와요."
     ],
     "sources": [
      {
       "title": "[UA] 측정기준 및 측정항목 - 애널리틱스 고객센터",
       "url": "https://support.google.com/analytics/answer/1033861?hl=ko",
       "kind": "official",
       "checked_at": "2026-10-15"
      },
      {
       "title": "애널리틱스 측정기준 및 측정항목 - 애널리틱스 고객센터",
       "url": "https://support.google.com/analytics/answer/9143382?hl=ko",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "세그먼트",
     "note": "측정기준·측정항목 조건을 조합해 세그먼트를 만듭니다."
    },
    {
     "term": "KPI",
     "note": "KPI는 측정항목 가운데 목표와 연결된 것입니다."
    }
   ],
   "confusable": [
    {
     "term": "KPI",
     "difference": "측정항목은 숫자 전반, KPI는 목표 관리용으로 고른 핵심 숫자입니다."
    }
   ]
  },
  {
   "id": "dashboard",
   "term": "대시보드",
   "original": "Dashboard",
   "korean": "대시보드",
   "aliases": [
    "대쉬보드",
    "Dashboard",
    "현황판",
    "지표 대시보드"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "data",
      "pm",
      "cx"
     ],
     "level": "입문",
     "importance": 3,
     "definition": "중요한 지표를 차트와 숫자로 한 화면에 모아 한눈에 상태를 볼 수 있게 만든 화면입니다. 데이터가 바뀌면 화면의 숫자도 함께 갱신됩니다.",
     "formula": null,
     "examples": [
      "CS 대시보드에 일별 문의량이랑 응답 시간만 먼저 올려 주세요.",
      "세부 분석은 보고서로 빼고 대시보드는 한 페이지로 유지하죠."
     ],
     "sources": [
      {
       "title": "Power BI 디자이너용 대시보드 소개 - Power BI | Microsoft Learn",
       "url": "https://learn.microsoft.com/ko-kr/power-bi/create-reports/service-dashboards",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "KPI",
     "note": "대시보드에 무엇을 올릴지는 KPI로 정합니다."
    },
    {
     "term": "데이터 웨어하우스",
     "note": "대시보드 숫자는 보통 데이터 웨어하우스에서 가져옵니다."
    }
   ],
   "confusable": [
    {
     "term": "보고서(리포트)",
     "difference": "대시보드는 한 화면의 요약판이고, 보고서는 여러 페이지에 걸쳐 세부 분석을 담습니다."
    }
   ]
  },
  {
   "id": "segment",
   "term": "세그먼트",
   "original": "Segment",
   "korean": "사용자 집단",
   "aliases": [
    "세그",
    "Segment",
    "고객군",
    "세그먼테이션",
    "잠재고객"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "data",
      "marketing"
     ],
     "level": "입문",
     "importance": 4,
     "definition": "국가, 구매 여부, 특정 행동 같은 조건으로 전체 데이터 가운데 일부 사용자·세션·이벤트만 골라낸 집합입니다. 집단별로 지표를 나눠 비교하거나 마케팅 대상을 정할 때 씁니다.",
     "formula": null,
     "examples": [
      "최근 30일 구매자 세그먼트만 따로 전환율 뽑아 볼게요.",
      "앱 설치 후 미구매 세그먼트에 쿠폰 푸시를 보내 보죠."
     ],
     "sources": [
      {
       "title": "세그먼트 작성 도구 - 애널리틱스 고객센터",
       "url": "https://support.google.com/analytics/answer/9304353?hl=ko",
       "kind": "official",
       "checked_at": "2026-10-15"
      },
      {
       "title": "잠재고객 생성, 수정, 보관처리하기 - 애널리틱스 고객센터",
       "url": "https://support.google.com/analytics/answer/9267572?hl=ko",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "코호트 분석",
     "note": "코호트는 시점 기준으로 묶은 특별한 세그먼트입니다."
    },
    {
     "term": "RFM 분석",
     "note": "구매 이력 점수로 고객 세그먼트를 나눕니다."
    }
   ],
   "confusable": [
    {
     "term": "코호트",
     "difference": "세그먼트는 아무 조건으로 묶은 집단이고, 코호트는 같은 시기에 같은 경험을 한 집단을 시간에 따라 추적합니다."
    }
   ]
  },
  {
   "id": "event",
   "term": "이벤트",
   "original": "Event",
   "korean": "이벤트",
   "aliases": [
    "Event",
    "이벤트 로그",
    "행동 로그",
    "판촉 행사",
    "프로모션"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "data",
      "pm"
     ],
     "level": "입문",
     "importance": 4,
     "definition": "페이지 조회, 버튼 클릭, 구매 완료처럼 사용자가 웹·앱에서 한 행동 하나하나를 분석 도구에 기록한 것입니다. 자동으로 수집되는 것과 직접 설계해 심는 것이 있습니다.",
     "formula": null,
     "examples": [
      "장바구니 담기 버튼에 이벤트가 안 심겨 있어서 퍼널이 끊겨요.",
      "이벤트 이름은 소문자와 언더바로 통일해 주세요."
     ],
     "sources": [
      {
       "title": "이벤트 정보 - 애널리틱스 고객센터",
       "url": "https://support.google.com/analytics/answer/9322688?hl=ko",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    },
    {
     "industries": [
      "ecommerce"
     ],
     "roles": [
      "marketing"
     ],
     "level": "입문",
     "importance": 3,
     "definition": "할인, 경품, 쿠폰처럼 상품 수요를 늘려 판매를 늘리려고 여는 판매 촉진 행사입니다. 법령에서는 이름이나 형식과 관계없이 판매 증진이 목적이면 판매촉진행사로 봅니다.",
     "formula": null,
     "examples": [
      "다음 달 브랜드 위크 이벤트 기간에는 쿠폰 중복 사용을 막아 주세요.",
      "이벤트 끝나고 매출이 원래대로 돌아왔는지 같이 봐야 해요."
     ],
     "sources": [
      {
       "title": "대규모유통업에서의 거래 공정화에 관한 법률 (한국법제연구원 영문/국문 법령)",
       "url": "https://elaw.klri.re.kr/kor_service/lawViewMultiContent.do?hseq=68490",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "세션",
     "note": "이벤트가 모여 하나의 세션(방문)을 이룹니다."
    },
    {
     "term": "전환율",
     "note": "구매 같은 핵심 이벤트 비율이 전환율입니다."
    }
   ],
   "confusable": [
    {
     "term": "프로모션(판촉 행사)",
     "difference": "데이터팀의 이벤트는 행동 로그, 마케팅팀의 이벤트는 할인 행사라 대화 맥락으로 구분해야 합니다."
    }
   ]
  },
  {
   "id": "session",
   "term": "세션",
   "original": "Session",
   "korean": "방문",
   "aliases": [
    "Session",
    "세션 수",
    "방문 수",
    "방문"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "data",
      "marketing"
     ],
     "level": "입문",
     "importance": 4,
     "definition": "사용자가 웹사이트나 앱에 들어와 활동한 한 번의 방문 구간입니다. GA4에서는 기본적으로 활동 없이 30분이 지나면 세션이 끝난 것으로 봅니다.",
     "formula": null,
     "examples": [
      "점심에 한 번, 저녁에 한 번 들어오면 사용자는 1명이고 세션은 2개예요.",
      "세션 시간초과 설정을 바꾸면 세션 수가 달라지니 비교할 때 조심하세요."
     ],
     "sources": [
      {
       "title": "애널리틱스 세션에 대한 정보 - 애널리틱스 고객센터",
       "url": "https://support.google.com/analytics/answer/9191807?hl=ko",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "이탈률",
     "note": "GA4 이탈률은 세션 단위로 계산합니다."
    },
    {
     "term": "이벤트",
     "note": "세션 안에서 일어난 행동이 이벤트로 기록됩니다."
    }
   ],
   "confusable": [
    {
     "term": "사용자 수",
     "difference": "사용자 수는 사람 수, 세션은 방문 횟수입니다."
    }
   ]
  },
  {
   "id": "sql",
   "term": "SQL",
   "original": "Structured Query Language",
   "korean": "구조적 쿼리 언어",
   "aliases": [
    "에스큐엘",
    "시퀄",
    "쿼리",
    "Structured Query Language"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "data"
     ],
     "level": "입문",
     "importance": 4,
     "definition": "행과 열로 된 표 형태의 관계형 데이터베이스에서 데이터를 조회·추가·수정·삭제할 때 쓰는 언어입니다. 분석가는 주로 데이터를 뽑아 집계하는 데 씁니다.",
     "formula": null,
     "examples": [
      "지난달 신규 구매자 수는 SQL로 바로 뽑아 드릴게요.",
      "SQL 쿼리 공유할 때 기간 조건도 같이 적어 주세요."
     ],
     "sources": [
      {
       "title": "SQL이란 무엇인가요? - 구조적 쿼리 언어(SQL) 설명 - AWS",
       "url": "https://aws.amazon.com/ko/what-is/sql/",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "데이터 웨어하우스",
     "note": "웨어하우스의 데이터를 SQL로 조회합니다."
    },
    {
     "term": "ETL",
     "note": "ETL의 변환 단계를 SQL로 작성하는 경우가 많습니다."
    }
   ],
   "confusable": [
    {
     "term": "NoSQL",
     "difference": "SQL은 표 형태 관계형 DB용 언어이고, NoSQL은 표 구조가 아닌 데이터베이스를 통틀어 부르는 말입니다."
    }
   ]
  },
  {
   "id": "bounce_churn",
   "term": "이탈률",
   "original": "Bounce rate / Churn rate",
   "korean": "이탈률",
   "aliases": [
    "바운스율",
    "바운스 레이트",
    "Bounce rate",
    "처닝",
    "Churn rate",
    "고객 이탈률"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "data",
      "marketing"
     ],
     "level": "입문",
     "importance": 4,
     "definition": "웹 분석에서 전체 세션 가운데 의미 있는 참여 없이 끝난 세션의 비율입니다. GA4에서는 10초 미만이고 주요 이벤트도 없고 페이지를 1번만 본 세션을 비참여 세션으로 보며, 참여율을 뺀 나머지가 이탈률입니다.",
     "formula": "이탈률 = 참여하지 않은 세션 수 ÷ 전체 세션 수 × 100 (= 100% − 참여율)",
     "examples": [
      "랜딩페이지 이탈률이 80%가 넘는데, 광고 문구와 페이지 내용이 안 맞는 것 같아요.",
      "GA4로 넘어오면서 이탈률 정의가 바뀌었으니 예전 숫자와 바로 비교하면 안 돼요."
     ],
     "sources": [
      {
       "title": "[GA4] 참여율 및 이탈률 - 애널리틱스 고객센터",
       "url": "https://support.google.com/analytics/answer/12195621?hl=ko",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    },
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "data",
      "cx",
      "pm"
     ],
     "level": "실무",
     "importance": 5,
     "definition": "일정 기간 동안 서비스 이용을 멈추거나 구독을 해지한 고객의 비율입니다. 기간 시작 시점 고객 중 얼마나 떠났는지로 계산하며, 리텐션의 반대 방향 지표입니다.",
     "formula": "고객 이탈률 = 기간 중 이탈한 고객 수 ÷ 기간 시작 시점 고객 수 × 100",
     "examples": [
      "요금 인상 후 월 이탈률이 올랐는지 코호트별로 봐 주세요.",
      "CS 응답이 늦은 고객군의 이탈률이 더 높은지 확인해 보죠."
     ],
     "sources": [
      {
       "title": "Metric definitions - App Store Connect Analytics - Apple Developer",
       "url": "https://developer.apple.com/help/app-store-connect-analytics/reference/metrics-definitions",
       "kind": "official",
       "checked_at": "2026-10-15"
      },
      {
       "title": "Churn Rate (First Round Review 용어집)",
       "url": "https://review.firstround.com/glossary/churn-rate/",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      },
      {
       "title": "What is Churn Rate? Definition and Related Resources | Amplitude",
       "url": "https://amplitude.com/glossary/terms/churn-rate.md",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "리텐션",
     "note": "고객 이탈률과 리텐션은 서로 반대 방향으로 움직입니다."
    },
    {
     "term": "LTV",
     "note": "고객 이탈률이 낮을수록 고객 생애 가치가 커집니다."
    }
   ],
   "confusable": [
    {
     "term": "종료율(Exit rate)",
     "difference": "이탈률(Bounce)은 참여 없이 끝난 세션 비율이고, 종료율은 특정 페이지가 마지막 페이지가 된 비율입니다."
    }
   ]
  },
  {
   "id": "retention",
   "term": "리텐션",
   "original": "Retention",
   "korean": "유지율",
   "aliases": [
    "Retention",
    "리텐션율",
    "잔존율",
    "재방문율",
    "유지율"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "data",
      "marketing",
      "pm",
      "cx"
     ],
     "level": "실무",
     "importance": 5,
     "definition": "처음 특정 행동(가입, 첫 구매 등)을 한 사용자 가운데 일정 기간 뒤에도 다시 돌아와 행동한 사용자의 비율입니다. 특정 날에 돌아온 사람만 셀지, 그날 이후 언제든 돌아온 사람까지 셀지에 따라 값이 달라집니다.",
     "formula": "리텐션 = 기간 N에 돌아온 사용자 수 ÷ 시작 행동을 한 사용자 수 × 100",
     "examples": [
      "7일 리텐션이 20% 아래로 떨어졌어요. 온보딩부터 점검해 보죠.",
      "리텐션 차트는 'N일 당일' 기준인지 'N일 이후' 기준인지 꼭 적어 주세요."
     ],
     "sources": [
      {
       "title": "How the Retention Analysis chart calculates retention (Amplitude 문서)",
       "url": "https://amplitude.com/docs/en/analytics/charts/retention-analysis/retention-analysis-calculation",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "코호트 분석",
     "note": "리텐션은 보통 가입 시기별 코호트로 나눠 봅니다."
    },
    {
     "term": "이탈률",
     "note": "고객 이탈률은 리텐션의 반대편 지표입니다."
    }
   ],
   "confusable": [
    {
     "term": "재구매율",
     "difference": "리텐션은 다시 돌아온 비율 전반, 재구매율은 두 번 이상 구매한 고객 비율에 한정됩니다."
    }
   ]
  },
  {
   "id": "cohort",
   "term": "코호트 분석",
   "original": "Cohort Analysis",
   "korean": "동질 집단 분석",
   "aliases": [
    "코호트",
    "Cohort",
    "코호트분석",
    "집단 분석",
    "Cohort Analysis"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "data",
      "marketing"
     ],
     "level": "실무",
     "importance": 5,
     "definition": "같은 시기에 가입하거나 같은 행동을 한 사용자끼리 묶은 집단(코호트)을 만들고, 집단별로 이후 행동이 시간에 따라 어떻게 바뀌는지 비교하는 분석입니다. 전체 평균에 가려진 리텐션·이탈 패턴을 찾는 데 씁니다.",
     "formula": null,
     "examples": [
      "3월 가입 코호트만 유독 리텐션이 낮은데, 그때 유입 채널이 달랐나요?",
      "프로모션으로 들어온 코호트와 자연 유입 코호트를 나눠서 봐 주세요."
     ],
     "sources": [
      {
       "title": "The Complete Guide to Cohort Analysis | Amplitude",
       "url": "https://amplitude.com/explore/analytics/cohort-analysis",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      },
      {
       "title": "How the Retention Analysis chart calculates retention (Amplitude 문서)",
       "url": "https://amplitude.com/docs/en/analytics/charts/retention-analysis/retention-analysis-calculation",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "리텐션",
     "note": "코호트 분석의 가장 흔한 결과물이 리텐션 표입니다."
    },
    {
     "term": "LTV",
     "note": "코호트별 누적 매출로 LTV를 추정합니다."
    }
   ],
   "confusable": [
    {
     "term": "세그먼트",
     "difference": "세그먼트는 조건으로 나눈 단면이고, 코호트는 같은 시점에 묶어 시간 흐름을 추적합니다."
    }
   ]
  },
  {
   "id": "ab_test",
   "term": "A/B 테스트",
   "original": "A/B Testing",
   "korean": "A/B 테스트",
   "aliases": [
    "AB테스트",
    "에이비 테스트",
    "분할 테스트",
    "Split test",
    "버킷 테스트"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "data",
      "marketing",
      "pm"
     ],
     "level": "실무",
     "importance": 5,
     "definition": "사용자를 무작위로 나눠 기존안(A)과 수정안(B)을 각각 보여 준 뒤, 어느 쪽이 목표 지표에서 더 나은지 통계로 비교하는 실험 방법입니다.",
     "formula": null,
     "examples": [
      "상세페이지 버튼 문구는 감으로 정하지 말고 A/B 테스트로 결정하죠.",
      "A/B 테스트는 표본이 다 찰 때까지 중간에 멈추지 말아 주세요."
     ],
     "sources": [
      {
       "title": "About Firebase A/B tests (Firebase 문서)",
       "url": "https://firebase.google.com/docs/ab-testing/ab-concepts",
       "kind": "official",
       "checked_at": "2026-10-15"
      },
      {
       "title": "A/B testing (Optimizely Optimization Glossary)",
       "url": "https://www.optimizely.com/optimization-glossary/ab-testing/",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "통계적 유의성",
     "note": "A/B 테스트 결과가 우연이 아닌지 판단할 때 씁니다."
    },
    {
     "term": "표본 크기",
     "note": "실험 전에 필요한 사용자 수를 정해야 합니다."
    }
   ],
   "confusable": [
    {
     "term": "이중차분법",
     "difference": "A/B 테스트는 무작위 배정 실험이고, 이중차분법은 무작위 배정이 어려울 때 전후 변화를 비교하는 방법입니다."
    }
   ]
  },
  {
   "id": "significance",
   "term": "통계적 유의성",
   "original": "Statistical Significance",
   "korean": "통계적 유의성",
   "aliases": [
    "유의성",
    "유의미",
    "p값",
    "p-value",
    "유의수준"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "data"
     ],
     "level": "실무",
     "importance": 4,
     "definition": "관찰한 차이가 실제로는 차이가 없는데 우연히 생겼을 가능성이 충분히 낮다고 판단할 수 있는 상태입니다. p값(차이가 없다고 가정할 때 지금만큼 극단적인 결과가 나올 확률)이 미리 정한 유의수준(예: 0.05)보다 작으면 유의하다고 봅니다.",
     "formula": null,
     "examples": [
      "전환율이 0.3%p 올랐지만 p값이 0.2라 아직 유의하다고 보긴 어려워요.",
      "유의수준은 실험 시작 전에 0.05로 정해 두죠."
     ],
     "sources": [
      {
       "title": "7.1.3.1. Critical values and p values (NIST/SEMATECH e-Handbook of Statistical Methods)",
       "url": "https://www.itl.nist.gov/div898/handbook/prc/section1/prc131.htm",
       "kind": "official",
       "checked_at": "2026-10-15"
      },
      {
       "title": "Statistical significance (Optimizely Optimization Glossary)",
       "url": "https://www.optimizely.com/optimization-glossary/statistical-significance/",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "신뢰구간",
     "note": "유의성과 함께 효과의 크기 범위를 보여 줍니다."
    },
    {
     "term": "다중 비교 문제",
     "note": "여러 번 검정하면 우연히 유의한 결과가 나올 위험이 커집니다."
    }
   ],
   "confusable": [
    {
     "term": "실질적 의미(효과 크기)",
     "difference": "통계적으로 유의해도 차이가 너무 작으면 사업적으로는 의미가 없을 수 있습니다."
    }
   ]
  },
  {
   "id": "confidence_interval",
   "term": "신뢰구간",
   "original": "Confidence Interval",
   "korean": "신뢰구간",
   "aliases": [
    "CI",
    "씨아이",
    "95% 신뢰구간",
    "신뢰 구간"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "data"
     ],
     "level": "실무",
     "importance": 3,
     "definition": "표본으로 계산한, 모집단의 실제 값(예: 평균, 전환율 차이)이 들어 있을 것으로 보는 범위입니다. 95% 신뢰구간은 같은 방식으로 여러 번 표본을 뽑아 구간을 만들면 그중 약 95%가 실제 값을 포함한다는 뜻입니다.",
     "formula": null,
     "examples": [
      "개선 효과의 95% 신뢰구간이 -0.1%p~0.8%p라 0을 포함하고 있어요.",
      "점 하나만 말하지 말고 신뢰구간도 같이 보고해 주세요."
     ],
     "sources": [
      {
       "title": "7.1.4. What are confidence intervals? (NIST/SEMATECH e-Handbook of Statistical Methods)",
       "url": "https://www.itl.nist.gov/div898/handbook/prc/section1/prc14.htm",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "통계적 유의성",
     "note": "차이의 신뢰구간이 0을 포함하지 않으면 보통 유의하다고 봅니다."
    },
    {
     "term": "표본 크기",
     "note": "표본이 클수록 신뢰구간이 좁아집니다."
    }
   ],
   "confusable": [
    {
     "term": "p값",
     "difference": "p값은 우연일 확률을 하나의 숫자로, 신뢰구간은 효과가 있을 법한 범위를 보여 줍니다."
    }
   ]
  },
  {
   "id": "etl",
   "term": "ETL",
   "original": "Extract, Transform, Load",
   "korean": "추출·변환·적재",
   "aliases": [
    "이티엘",
    "추출 변환 적재",
    "데이터 파이프라인",
    "ELT"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "data"
     ],
     "level": "실무",
     "importance": 3,
     "definition": "여러 시스템에서 데이터를 꺼내(추출) 분석하기 좋은 형태로 정리하고(변환) 데이터 웨어하우스 같은 중앙 저장소에 넣는(적재) 과정입니다.",
     "formula": null,
     "examples": [
      "주문 테이블 ETL이 새벽에 실패해서 오늘 대시보드 숫자가 어제 기준이에요.",
      "광고비 데이터도 ETL에 붙여서 매일 자동으로 들어오게 해 주세요."
     ],
     "sources": [
      {
       "title": "ETL이란 무엇인가요? - 추출, 전환, 적재 설명 - AWS",
       "url": "https://aws.amazon.com/ko/what-is/etl/",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "데이터 웨어하우스",
     "note": "ETL의 도착지가 보통 데이터 웨어하우스입니다."
    },
    {
     "term": "SQL",
     "note": "변환 로직을 SQL로 짜는 경우가 많습니다."
    }
   ],
   "confusable": [
    {
     "term": "ELT",
     "difference": "ETL은 변환 후 적재, ELT는 먼저 적재하고 웨어하우스 안에서 변환합니다."
    }
   ]
  },
  {
   "id": "data_warehouse",
   "term": "데이터 웨어하우스",
   "original": "Data Warehouse",
   "korean": "데이터 웨어하우스",
   "aliases": [
    "DW",
    "디더블유",
    "데이터웨어하우스",
    "DWH",
    "데이터 창고"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "data"
     ],
     "level": "실무",
     "importance": 3,
     "definition": "주문·회원·로그 등 여러 시스템의 데이터를 정기적으로 모아 분석에 쓰도록 만든 중앙 저장소입니다. 여러 사람이 BI 도구나 SQL로 동시에 조회하는 분석 용도에 맞춰져 있습니다.",
     "formula": null,
     "examples": [
      "운영 DB 말고 웨어하우스에서 조회해 주세요. 서비스에 부하가 가요.",
      "CS 티켓 데이터도 웨어하우스에 넣으면 주문 데이터랑 붙여 볼 수 있어요."
     ],
     "sources": [
      {
       "title": "데이터 웨어하우스란? - 데이터 웨어하우스 설명 - AWS",
       "url": "https://aws.amazon.com/ko/what-is/data-warehouse/",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "ETL",
     "note": "ETL로 데이터를 웨어하우스에 채웁니다."
    },
    {
     "term": "대시보드",
     "note": "대시보드는 웨어하우스 데이터를 시각화합니다."
    }
   ],
   "confusable": [
    {
     "term": "데이터 레이크",
     "difference": "웨어하우스는 정리된 분석용 데이터를, 데이터 레이크는 가공 전 원본 데이터를 형식 제한 없이 쌓습니다."
    }
   ]
  },
  {
   "id": "stickiness",
   "term": "스티키니스",
   "original": "Stickiness",
   "korean": "고착도",
   "aliases": [
    "Stickiness",
    "DAU/MAU",
    "스티키니스 비율",
    "고착도",
    "점착도"
   ],
   "senses": [
    {
     "industries": [
      "platform"
     ],
     "roles": [
      "data",
      "pm"
     ],
     "level": "실무",
     "importance": 4,
     "definition": "한 달 동안 활동한 사용자 가운데 하루에 실제로 들어오는 사용자의 비율로, 사용자가 서비스를 얼마나 자주 쓰는지 보여 줍니다. 값이 높을수록 습관처럼 자주 쓰는 서비스입니다.",
     "formula": "스티키니스 = DAU ÷ MAU × 100",
     "examples": [
      "MAU는 비슷한데 DAU/MAU가 15%에서 25%로 올랐어요. 자주 쓰는 사용자가 늘었네요.",
      "스티키니스는 서비스 성격마다 기준이 달라서 업계 평균과 단순 비교하면 안 돼요."
     ],
     "sources": [
      {
       "title": "애널리틱스 측정기준 및 측정항목 - 애널리틱스 고객센터 (DAU/MAU 항목)",
       "url": "https://support.google.com/analytics/answer/9143382?hl=ko",
       "kind": "official",
       "checked_at": "2026-10-15"
      },
      {
       "title": "You're Measuring Daily Active Users Wrong (Amplitude 블로그)",
       "url": "https://www.amplitude.com/blog/measuring-active-users",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "DAU",
     "note": "스티키니스의 분자입니다."
    },
    {
     "term": "MAU",
     "note": "스티키니스의 분모입니다."
    }
   ],
   "confusable": [
    {
     "term": "리텐션",
     "difference": "리텐션은 다시 돌아오는지, 스티키니스는 활동 사용자가 얼마나 자주 오는지를 봅니다."
    }
   ]
  },
  {
   "id": "gmv",
   "term": "GMV",
   "original": "Gross Merchandise Value",
   "korean": "총 거래액",
   "aliases": [
    "지엠브이",
    "거래액",
    "총거래액",
    "Gross Merchandise Volume"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce"
     ],
     "roles": [
      "data",
      "pm",
      "marketing"
     ],
     "level": "실무",
     "importance": 5,
     "definition": "일정 기간 동안 플랫폼에서 상품·서비스 거래가 일어난 총 금액으로, 판매가에 판매 수량을 곱해 구합니다. 통계청 온라인쇼핑 거래액처럼 부가세·배송비까지 포함해 세는 경우가 많고, 수수료·할인·반품을 빼기 전 금액이라 회사가 실제로 가져가는 매출과는 다릅니다.",
     "formula": "GMV = 판매가 × 판매 수량 (기간 합계, 반품·할인·수수료 차감 전)",
     "examples": [
      "이번 행사로 GMV는 늘었지만 쿠폰 비용 때문에 매출은 생각보다 적어요.",
      "보고서에 GMV에 취소·반품을 포함했는지 기준을 적어 주세요."
     ],
     "sources": [
      {
       "title": "서비스업동향조사 및 온라인쇼핑동향조사 관련 문의 - KOSIS 국가통계포털",
       "url": "https://kosis.kr/civilComplaint/qnaDetail.do?boardIdx=21551",
       "kind": "official",
       "checked_at": "2026-10-15"
      },
      {
       "title": "Gross Merchandise Value (GMV) (First Round Review 용어집)",
       "url": "https://review.firstround.com/glossary/gross-merchandise-value-gmv/",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "매출",
     "note": "GMV 중 회사가 수수료 등으로 실제 가져가는 몫이 매출입니다."
    },
    {
     "term": "객단가(AOV)",
     "note": "GMV를 주문 수로 나누면 평균 주문 금액이 됩니다."
    }
   ],
   "confusable": [
    {
     "term": "매출(Revenue)",
     "difference": "GMV는 거래된 총 금액, 매출은 회사가 수수료·직매입 판매 등으로 실제 인식하는 수익입니다."
    }
   ]
  },
  {
   "id": "repurchase_rate",
   "term": "재구매율",
   "original": "Repeat Purchase Rate",
   "korean": "재구매율",
   "aliases": [
    "RPR",
    "리피트 구매율",
    "재구매 비율",
    "Repurchase rate"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce"
     ],
     "roles": [
      "data",
      "marketing",
      "cx"
     ],
     "level": "실무",
     "importance": 4,
     "definition": "정한 기간 동안 구매한 고객 가운데 두 번 이상 산 고객의 비율입니다. 고객 충성도와 리텐션 활동의 효과를 볼 때 씁니다.",
     "formula": "재구매율 = 기간 내 2회 이상 구매한 고객 수 ÷ 기간 내 구매 고객 수 × 100",
     "examples": [
      "첫 구매 쿠폰 고객의 90일 재구매율이 일반 고객보다 낮은지 봐 주세요.",
      "재구매율 기간을 30일로 할지 90일로 할지 먼저 합의하죠."
     ],
     "sources": [
      {
       "title": "What Is Repeat Purchase Rate? How to Calculate It? (Storyly 용어집)",
       "url": "https://www.storyly.io/glossary/repeat-purchase-rate-rpr",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      },
      {
       "title": "애널리틱스 측정기준 및 측정항목 - 애널리틱스 고객센터 (재구매자 수 항목)",
       "url": "https://support.google.com/analytics/answer/9143382?hl=ko",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "리텐션",
     "note": "재구매율은 커머스에서 쓰는 리텐션 지표입니다."
    },
    {
     "term": "LTV",
     "note": "재구매가 늘면 고객 생애 가치가 커집니다."
    }
   ],
   "confusable": [
    {
     "term": "구매 빈도",
     "difference": "재구매율은 다시 산 고객의 비율, 구매 빈도는 고객 1명이 평균 몇 번 샀는지입니다."
    }
   ]
  },
  {
   "id": "rfm",
   "term": "RFM 분석",
   "original": "Recency, Frequency, Monetary Analysis",
   "korean": "최근성·빈도·금액 분석",
   "aliases": [
    "알에프엠",
    "RFM",
    "RFM 세그먼테이션",
    "RFM분석"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce"
     ],
     "roles": [
      "data",
      "marketing"
     ],
     "level": "실무",
     "importance": 3,
     "definition": "고객을 최근에 언제 샀는지(R), 얼마나 자주 샀는지(F), 얼마나 많이 썼는지(M) 세 기준으로 점수를 매겨 묶는 고객 분류 방법입니다. 우수 고객과 휴면 위험 고객을 골라 마케팅 대상을 정할 때 씁니다.",
     "formula": null,
     "examples": [
      "R 점수는 낮고 M 점수가 높은 고객에게 복귀 쿠폰을 보내 보죠.",
      "RFM 점수 구간은 분위수로 5등분해서 잡았어요."
     ],
     "sources": [
      {
       "title": "RFM analysis (recency, frequency, monetary) - TechTarget",
       "url": "https://www.techtarget.com/data-technologies/definition/RFM-analysis-recency-frequency-monetary",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "세그먼트",
     "note": "RFM 점수로 고객 세그먼트를 만듭니다."
    },
    {
     "term": "LTV",
     "note": "RFM 상위 고객이 대체로 LTV도 높습니다."
    }
   ],
   "confusable": [
    {
     "term": "코호트 분석",
     "difference": "RFM은 구매 이력 점수로 고객을 나누고, 코호트는 같은 시점 집단을 시간 흐름으로 추적합니다."
    }
   ]
  },
  {
   "id": "arpu",
   "term": "ARPU",
   "original": "Average Revenue Per User",
   "korean": "사용자당 평균 수익",
   "aliases": [
    "알푸",
    "에이알피유",
    "인당 매출",
    "사용자당평균수익"
   ],
   "senses": [
    {
     "industries": [
      "platform"
     ],
     "roles": [
      "data",
      "pm",
      "marketing"
     ],
     "level": "실무",
     "importance": 4,
     "definition": "일정 기간 동안 사용자 한 명이 평균적으로 만들어 낸 수익입니다. 구매하지 않은 사용자까지 포함한 활성 사용자 전체로 나눈다는 점이 특징입니다.",
     "formula": "ARPU = 기간 총수익(광고 + 구매 + 인앱 구매 + 구독 − 환불) ÷ 활성 사용자 수",
     "examples": [
      "유료 전환율은 그대로인데 ARPU가 올랐어요. 광고 수익이 늘었나 봐요.",
      "ARPU 비교할 때 분모가 활성 사용자인지 전체 가입자인지 맞춰 주세요."
     ],
     "sources": [
      {
       "title": "애널리틱스 측정기준 및 측정항목 - 애널리틱스 고객센터 (ARPU 항목)",
       "url": "https://support.google.com/analytics/answer/9143382?hl=ko",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "LTV",
     "note": "ARPU에 평균 이용 기간을 곱해 LTV를 어림합니다."
    },
    {
     "term": "MAU",
     "note": "월 ARPU는 보통 MAU를 분모로 씁니다."
    }
   ],
   "confusable": [
    {
     "term": "ARPPU",
     "difference": "ARPU는 전체 활성 사용자, ARPPU는 결제한 사용자만 분모로 씁니다."
    }
   ]
  },
  {
   "id": "sample_size",
   "term": "표본 크기",
   "original": "Sample Size",
   "korean": "표본 크기",
   "aliases": [
    "샘플 사이즈",
    "표본수",
    "Sample size",
    "검정력",
    "표본 수"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "data"
     ],
     "level": "심화",
     "importance": 4,
     "definition": "실험이나 조사에 포함할 관측(사용자) 수입니다. 필요한 표본 크기는 유의수준, 실제 차이를 놓칠 위험(β, 1−β가 검정력), 데이터의 흩어진 정도, 찾고 싶은 차이의 크기에 따라 정해집니다.",
     "formula": null,
     "examples": [
      "이 트래픽이면 0.5%p 차이를 잡는 데 표본이 3주는 쌓여야 해요.",
      "검정력 80% 기준으로 그룹당 필요한 표본 크기부터 계산하죠."
     ],
     "sources": [
      {
       "title": "7.2.2.2. Sample sizes required (NIST/SEMATECH e-Handbook of Statistical Methods)",
       "url": "https://www.itl.nist.gov/div898/handbook/prc/section2/prc222.htm",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "A/B 테스트",
     "note": "실험 기간은 필요한 표본 크기로 정합니다."
    },
    {
     "term": "신뢰구간",
     "note": "표본이 클수록 신뢰구간이 좁아집니다."
    }
   ],
   "confusable": [
    {
     "term": "통계적 유의성",
     "difference": "표본 크기는 실험 전 설계값이고, 유의성은 실험 후 결과 판단입니다."
    }
   ]
  },
  {
   "id": "multiple_comparisons",
   "term": "다중 비교 문제",
   "original": "Multiple Comparisons Problem",
   "korean": "다중 비교 문제",
   "aliases": [
    "다중 검정 문제",
    "Multiple testing",
    "다중비교",
    "본페로니 보정"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "data"
     ],
     "level": "심화",
     "importance": 3,
     "definition": "여러 그룹이나 여러 지표를 한꺼번에 반복해서 검정하면, 검정 하나에서 정한 유의수준보다 전체적으로 우연히 '유의한' 결과가 나올 확률이 커지는 문제입니다. 본페로니, 튜키 같은 보정 방법으로 줄입니다.",
     "formula": null,
     "examples": [
      "지표를 20개나 봤으니 하나쯤 유의하게 나온 건 우연일 수 있어요.",
      "변형안이 4개라 다중 비교 보정을 적용한 p값으로 판단할게요."
     ],
     "sources": [
      {
       "title": "7.4.7. How can we make multiple comparisons? (NIST/SEMATECH e-Handbook of Statistical Methods)",
       "url": "https://www.itl.nist.gov/div898/handbook/prc/section4/prc47.htm",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "통계적 유의성",
     "note": "검정 횟수가 늘면 유의성 판단 기준을 보정해야 합니다."
    },
    {
     "term": "A/B 테스트",
     "note": "변형안·지표가 많은 실험에서 자주 생깁니다."
    }
   ],
   "confusable": [
    {
     "term": "p-해킹",
     "difference": "다중 비교 문제는 통계적 현상이고, p-해킹은 유의한 결과가 나올 때까지 분석을 바꾸는 잘못된 관행입니다."
    }
   ]
  },
  {
   "id": "simpsons_paradox",
   "term": "심슨의 역설",
   "original": "Simpson's Paradox",
   "korean": "심슨의 역설",
   "aliases": [
    "심슨 역설",
    "심슨 패러독스",
    "Simpson's paradox",
    "심슨의역설"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "data"
     ],
     "level": "심화",
     "importance": 3,
     "definition": "집단별로 나눠 보면 보이던 경향이, 집단을 합쳐 전체로 보면 사라지거나 반대로 뒤집히는 현상입니다. 그룹 구성 비율이 다를 때 전체 평균만 보면 잘못된 결론을 낼 수 있습니다.",
     "formula": null,
     "examples": [
      "기기별로는 B안이 모두 이겼는데 전체로는 A안이 이겨요. 심슨의 역설인지 트래픽 비율부터 볼게요.",
      "채널 구성이 달라졌으니 전체 전환율만 보지 말고 채널별로도 쪼개 주세요."
     ],
     "sources": [
      {
       "title": "Simpson's Paradox | Wingify Glossary",
       "url": "https://wingify.com/glossary/simpsons-paradox/",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "세그먼트",
     "note": "세그먼트별로 나눠 보면 역설을 발견할 수 있습니다."
    },
    {
     "term": "A/B 테스트",
     "note": "실험 중 트래픽 배분이 바뀌면 생길 수 있습니다."
    }
   ],
   "confusable": [
    {
     "term": "교란 변수",
     "difference": "심슨의 역설은 나타나는 현상이고, 교란 변수는 그 현상을 일으키는 숨은 원인입니다."
    }
   ]
  },
  {
   "id": "did",
   "term": "이중차분법",
   "original": "Difference-in-Differences",
   "korean": "이중차분법",
   "aliases": [
    "DiD",
    "디아이디",
    "이중 차분",
    "차이의 차이",
    "Diff-in-Diff"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "data"
     ],
     "level": "심화",
     "importance": 3,
     "definition": "정책이나 기능을 적용한 집단과 적용하지 않은 집단의 전후 변화량을 각각 구한 뒤, 그 두 변화량의 차이를 효과로 보는 방법입니다. 무작위 실험이 어려울 때 쓰며, 개입이 없었다면 두 집단이 비슷하게 움직였을 것(평행 추세)이라는 가정이 필요합니다.",
     "formula": "효과 = (처리 집단 사후 − 처리 집단 사전) − (비교 집단 사후 − 비교 집단 사전)",
     "examples": [
      "서울에만 무료배송을 먼저 열었으니 다른 지역과 이중차분법으로 효과를 보죠.",
      "출시 전 두 지역 추세가 나란했는지부터 그래프로 확인해 주세요."
     ],
     "sources": [
      {
       "title": "Difference-in-differences: Causal product inference (Statsig)",
       "url": "https://www.statsig.com/perspectives/diff-in-diff-causal-inference",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "A/B 테스트",
     "note": "무작위 실험이 불가능할 때 대안으로 씁니다."
    },
    {
     "term": "코호트 분석",
     "note": "집단별 시간 흐름 비교라는 점에서 닮았습니다."
    }
   ],
   "confusable": [
    {
     "term": "전후 비교",
     "difference": "단순 전후 비교는 계절성 같은 공통 변화를 못 걸러내고, 이중차분법은 비교 집단 변화를 빼서 보정합니다."
    }
   ]
  },
  {
   "id": "prd",
   "term": "PRD",
   "original": "Product Requirements Document",
   "korean": "제품 요구사항 문서",
   "aliases": [
    "피알디",
    "제품 요구사항 정의서",
    "기획서",
    "요구사항 문서",
    "PRD 문서"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "pm"
     ],
     "level": "입문",
     "importance": 5,
     "definition": "만들 제품이나 기능의 목적, 대상 사용자, 핵심 기능과 동작, 성공 기준을 한곳에 정리한 문서입니다. 기획·디자인·개발이 같은 내용을 보고 일하도록 맞추는 기준이 됩니다.",
     "formula": null,
     "examples": [
      "이번 장바구니 개편 PRD에 성공 지표랑 범위 밖 항목까지 적어서 내일 리뷰 때 공유할게요.",
      "개발 착수 전에 PRD에서 예외 케이스가 빠진 게 없는지 한 번 더 봐 주세요."
     ],
     "sources": [
      {
       "title": "What is a Product Requirements Document (PRD)? | Atlassian",
       "url": "https://www.atlassian.com/agile/product-management/requirements",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "사용자 스토리",
     "note": "PRD 안의 요구사항을 사용자 관점의 작은 작업 단위로 쪼갠 것입니다."
    },
    {
     "term": "인수 조건",
     "note": "PRD의 요구사항이 충족됐는지 판단하는 구체적 기준입니다."
    },
    {
     "term": "로드맵",
     "note": "여러 PRD가 다루는 기능들이 언제 나올지 보여 줍니다."
    }
   ],
   "confusable": [
    {
     "term": "로드맵",
     "difference": "로드맵은 시간 축의 방향·순서를, PRD는 한 제품·기능의 상세 요구사항을 다룹니다."
    }
   ]
  },
  {
   "id": "mvp",
   "term": "MVP",
   "original": "Minimum Viable Product",
   "korean": "최소 기능 제품",
   "aliases": [
    "엠브이피",
    "최소 실행 가능 제품",
    "최소기능제품",
    "최소 기능 상품"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "pm",
      "marketing"
     ],
     "level": "입문",
     "importance": 5,
     "definition": "최소한의 노력으로 고객에 대해 가장 많이 배울 수 있도록 핵심만 담아 내놓는 첫 버전 제품입니다. 실제 사용자 반응으로 가설을 검증하고 다음에 무엇을 만들지 정하는 것이 목적입니다.",
     "formula": null,
     "examples": [
      "MVP는 결제 없이 예약 신청만 받아 보고 수요부터 확인하죠.",
      "MVP 범위에 알림 기능까지 넣으면 출시가 너무 늦어질 것 같아요."
     ],
     "sources": [
      {
       "title": "Minimum Viable Product: a guide (Eric Ries)",
       "url": "https://www.startuplessonslearned.com/2009/08/minimum-viable-product-guide.html",
       "kind": "official",
       "checked_at": "2026-10-15"
      },
      {
       "title": "What is a Minimum Viable Product (MVP)? | Atlassian",
       "url": "https://www.atlassian.com/agile/product-management/minimum-viable-product",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "PMF",
     "note": "MVP로 얻은 반응을 바탕으로 제품-시장 적합성을 찾아 갑니다."
    },
    {
     "term": "백로그",
     "note": "MVP에서 뺀 기능은 백로그에 남겨 우선순위를 다시 매깁니다."
    }
   ],
   "confusable": [
    {
     "term": "프로토타입",
     "difference": "프로토타입은 주로 검증용 시안이고, MVP는 실제 사용자에게 내놓는 작동하는 제품입니다."
    }
   ]
  },
  {
   "id": "backlog",
   "term": "백로그",
   "original": "Backlog",
   "korean": "백로그",
   "aliases": [
    "백 로그",
    "제품 백로그",
    "프로덕트 백로그",
    "티켓 백로그",
    "미처리 티켓"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "pm"
     ],
     "level": "입문",
     "importance": 5,
     "definition": "제품을 더 좋게 만들기 위해 해야 할 일을 우선순위대로 늘어놓은 목록입니다. 스크럼에서는 팀이 할 일은 모두 이 목록에서 나오고, 제품 책임자(PO)가 순서를 관리합니다.",
     "formula": null,
     "examples": [
      "그 요청은 이번 스프린트엔 못 넣고 백로그에 올려 둘게요.",
      "백로그 상위 10개는 다음 플래닝 전에 상세 내용 채워 두세요."
     ],
     "sources": [
      {
       "title": "The 2020 Scrum Guide",
       "url": "https://scrumguides.org/scrum-guide.html",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    },
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "cx"
     ],
     "level": "실무",
     "importance": 3,
     "definition": "상담팀에서 아직 해결하지 못하고 쌓여 있는 문의 티켓 묶음을 말합니다. 신규·진행 중·대기·보류 상태로 남아 있는 미해결 티켓 수를 보고 처리 여력을 판단합니다.",
     "formula": null,
     "examples": [
      "연휴 끝나고 백로그가 두 배로 늘어서 오늘은 오래된 티켓부터 처리할게요.",
      "백로그 중에 우선순위 높은 티켓이 몇 건인지 따로 뽑아 주세요."
     ],
     "sources": [
      {
       "title": "Analyzing the metrics that matter to improve customer support | Zendesk help",
       "url": "https://support.zendesk.com/hc/en-us/articles/4408832234394-Analyzing-the-metrics-that-matter-to-improve-customer-support",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "스프린트",
     "note": "스프린트 계획 때 제품 백로그에서 이번에 할 일을 골라옵니다."
    },
    {
     "term": "칸반",
     "note": "백로그 항목이 진행되는 흐름을 보드로 보여 줍니다."
    }
   ],
   "confusable": [
    {
     "term": "스프린트 백로그",
     "difference": "제품 백로그는 제품 전체의 할 일 목록이고, 스프린트 백로그는 이번 스프린트에 하기로 고른 일만 담습니다."
    }
   ]
  },
  {
   "id": "sprint",
   "term": "스프린트",
   "original": "Sprint",
   "korean": "스프린트",
   "aliases": [
    "스플린트",
    "반복 주기",
    "이터레이션",
    "Iteration",
    "스프린트 주기"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "pm"
     ],
     "level": "입문",
     "importance": 5,
     "definition": "스크럼에서 한 달 이하로 정해 둔 짧은 작업 기간입니다. 이 기간 안에 계획·데일리 스크럼·리뷰·회고가 모두 이뤄지고, 쓸 수 있는 결과물을 만들어 냅니다.",
     "formula": null,
     "examples": [
      "이번 스프린트는 2주라 금요일에 리뷰하고 바로 회고까지 할게요.",
      "스프린트 중간에 새 요구가 들어오면 PO랑 먼저 상의해 주세요."
     ],
     "sources": [
      {
       "title": "The 2020 Scrum Guide",
       "url": "https://scrumguides.org/scrum-guide.html",
       "kind": "official",
       "checked_at": "2026-10-15"
      },
      {
       "title": "Scrum sprints | Atlassian",
       "url": "https://www.atlassian.com/agile/scrum/sprints",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "백로그",
     "note": "스프린트에서 할 일은 백로그에서 골라옵니다."
    },
    {
     "term": "회고",
     "note": "스프린트를 마무리하며 일하는 방식을 돌아보는 시간입니다."
    },
    {
     "term": "스토리 포인트",
     "note": "한 스프린트에 얼마나 할 수 있을지 가늠하는 데 씁니다."
    }
   ],
   "confusable": [
    {
     "term": "릴리스",
     "difference": "스프린트는 작업 기간 단위이고, 릴리스는 결과물을 사용자에게 내놓는 일입니다. 스프린트마다 꼭 릴리스하는 것은 아닙니다."
    }
   ]
  },
  {
   "id": "user_story",
   "term": "사용자 스토리",
   "original": "User Story",
   "korean": "사용자 스토리",
   "aliases": [
    "유저 스토리",
    "유저스토리",
    "사용자스토리",
    "스토리"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "pm"
     ],
     "level": "입문",
     "importance": 4,
     "definition": "기능을 사용자 입장에서 짧게 적은 애자일의 가장 작은 작업 단위입니다. 기능 목록이 아니라 그 일이 사용자에게 주는 가치와 목적이 드러나도록 씁니다.",
     "formula": null,
     "examples": [
      "'재구매 고객으로서 지난 주문을 한 번에 다시 담고 싶다'로 유저 스토리 하나 만들어 주세요.",
      "이 스토리는 너무 커서 두 개로 나누는 게 좋겠어요."
     ],
     "sources": [
      {
       "title": "What are work types? | Jira Cloud | Atlassian Support",
       "url": "https://support.atlassian.com/jira-cloud-administration/docs/what-are-issue-types/",
       "kind": "official",
       "checked_at": "2026-10-15"
      },
      {
       "title": "User Stories | Atlassian",
       "url": "https://www.atlassian.com/agile/project-management/user-stories",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "에픽",
     "note": "여러 사용자 스토리를 묶은 큰 단위입니다."
    },
    {
     "term": "인수 조건",
     "note": "스토리가 완료됐다고 볼 조건을 적습니다."
    },
    {
     "term": "스토리 포인트",
     "note": "스토리의 상대적 크기를 추정합니다."
    }
   ],
   "confusable": [
    {
     "term": "인수 조건",
     "difference": "사용자 스토리는 무엇을 왜 원하는지, 인수 조건은 무엇이 충족돼야 완료인지를 적습니다."
    }
   ]
  },
  {
   "id": "roadmap",
   "term": "로드맵",
   "original": "Product Roadmap",
   "korean": "제품 로드맵",
   "aliases": [
    "로드 맵",
    "제품 로드맵",
    "프로덕트 로드맵",
    "Roadmap"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "pm"
     ],
     "level": "입문",
     "importance": 4,
     "definition": "제품이 어떤 방향으로 언제쯤 무엇을 해 나갈지를 시간 흐름에 따라 보여 주는 계획표입니다. 팀과 이해관계자가 같은 그림을 보도록 하는 공통 기준 역할을 합니다.",
     "formula": null,
     "examples": [
      "하반기 로드맵에서 판매자 정산 개선을 3분기로 당기는 건 어떨까요?",
      "로드맵에는 날짜보다 분기 단위로만 적어 두죠."
     ],
     "sources": [
      {
       "title": "Product Roadmap Guide | Atlassian",
       "url": "https://www.atlassian.com/agile/product-management/product-roadmaps",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "OKR",
     "note": "로드맵의 항목이 어떤 목표에 기여하는지 연결합니다."
    },
    {
     "term": "백로그",
     "note": "로드맵의 큰 주제가 실제 할 일로 쪼개져 백로그에 들어갑니다."
    }
   ],
   "confusable": [
    {
     "term": "PRD",
     "difference": "로드맵은 여러 일의 순서·시기를, PRD는 한 기능의 상세 요구사항을 다룹니다."
    },
    {
     "term": "릴리스 계획",
     "difference": "릴리스 계획은 특정 배포 묶음의 일정이고, 로드맵은 더 긴 기간의 방향입니다."
    }
   ]
  },
  {
   "id": "wireframe",
   "term": "와이어프레임",
   "original": "Wireframe",
   "korean": "와이어프레임",
   "aliases": [
    "와이어 프레임",
    "화면 설계도",
    "화면 뼈대",
    "로우파이",
    "Lo-fi 와이어프레임"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "pm"
     ],
     "level": "입문",
     "importance": 3,
     "definition": "색이나 이미지 없이 박스와 글자로 화면 구성과 정보 배치를 잡아 둔 뼈대 그림입니다. 디자인을 다듬기 전에 화면에 무엇이 어디 들어갈지 합의하는 데 쓰며, 실제처럼 눌러 볼 수 있게 만든 것은 프로토타입이라고 합니다.",
     "formula": null,
     "examples": [
      "상세 페이지 와이어프레임 먼저 공유드리니 정보 순서만 봐 주세요.",
      "와이어프레임 합의되면 그다음에 클릭 가능한 프로토타입으로 사용성 테스트 할게요."
     ],
     "sources": [
      {
       "title": "Wireframes | Digital.gov",
       "url": "https://digital.gov/guides/research-collaboration/designing/wireframing",
       "kind": "official",
       "checked_at": "2026-10-15"
      },
      {
       "title": "What is wireframing? | Figma",
       "url": "https://www.figma.com/resource-library/what-is-wireframing/",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "PRD",
     "note": "와이어프레임은 PRD의 요구사항을 화면으로 옮긴 첫 단계입니다."
    },
    {
     "term": "사용자 스토리",
     "note": "스토리 단위로 필요한 화면을 와이어프레임으로 그립니다."
    }
   ],
   "confusable": [
    {
     "term": "프로토타입",
     "difference": "와이어프레임은 정적인 화면 뼈대이고, 프로토타입은 흐름을 직접 눌러 볼 수 있게 만든 시안입니다."
    },
    {
     "term": "목업",
     "difference": "목업은 색·폰트 등 시각 디자인까지 입힌 정적 화면입니다."
    }
   ]
  },
  {
   "id": "release",
   "term": "릴리스",
   "original": "Release",
   "korean": "출시",
   "aliases": [
    "릴리즈",
    "제품 출시",
    "버전 출시",
    "Product Release"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "pm"
     ],
     "level": "입문",
     "importance": 3,
     "definition": "새 제품이나 바뀐 기능을 고객이 쓸 수 있게 내놓는 일과 그 과정을 말합니다. 준비·테스트·배포·출시 후 지원까지 포함하며, 코드를 서버에 올리는 배포는 그중 기술적 단계 하나입니다.",
     "formula": null,
     "examples": [
      "배포는 화요일에 해 두고, 릴리스는 공지 준비되는 목요일에 플래그를 켜서 하죠.",
      "이번 릴리스 노트에 결제 오류 수정 건도 넣어 주세요."
     ],
     "sources": [
      {
       "title": "What is a version? | Jira Cloud | Atlassian Support",
       "url": "https://support.atlassian.com/jira-software-cloud/docs/what-is-a-version/",
       "kind": "official",
       "checked_at": "2026-10-15"
      },
      {
       "title": "Product release guide | Atlassian",
       "url": "https://www.atlassian.com/agile/product-management/product-release",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "피처 플래그",
     "note": "배포와 릴리스 시점을 분리할 때 씁니다."
    },
    {
     "term": "QA",
     "note": "릴리스 전에 품질을 확인하는 단계입니다."
    }
   ],
   "confusable": [
    {
     "term": "배포",
     "difference": "배포는 코드를 운영 환경에 올리는 기술 작업이고, 릴리스는 사용자가 쓰도록 내놓는 것입니다."
    }
   ]
  },
  {
   "id": "qa",
   "term": "QA",
   "original": "Quality Assurance",
   "korean": "품질 보증",
   "aliases": [
    "큐에이",
    "품질보증",
    "QA 테스트",
    "상담 품질 평가",
    "품질 평가"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "pm"
     ],
     "level": "입문",
     "importance": 4,
     "definition": "제품이나 서비스가 정해진 요구사항을 만족하는지 체계적으로 확인하는 활동입니다. IT에서는 출시 전에 기능·회귀·인수 테스트 등으로 결함을 찾고 예방하는 일을 주로 가리킵니다.",
     "formula": null,
     "examples": [
      "QA 기간에 쿠폰 중복 적용 버그가 나와서 릴리스를 하루 미룰게요.",
      "QA 체크리스트에 품절 상품 결제 시나리오도 추가해 주세요."
     ],
     "sources": [
      {
       "title": "What is quality assurance (QA)? | TechTarget",
       "url": "https://www.techtarget.com/searchsoftwarequality/definition/quality-assurance",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      },
      {
       "title": "The different types of software testing | Atlassian",
       "url": "https://www.atlassian.com/continuous-delivery/software-testing/types-of-software-testing",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    },
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "cx"
     ],
     "level": "실무",
     "importance": 3,
     "definition": "상담사가 처리한 대화를 정해진 평가표 기준(정확성, 공감, 정책 준수 등)으로 점수 매기고 피드백하는 상담 품질 평가 활동입니다.",
     "formula": null,
     "examples": [
      "이번 주 QA에서 환불 안내 정확도 점수가 낮아서 스크립트를 다시 보죠.",
      "신규 상담사 대화는 QA 표본을 늘려서 매일 피드백 주세요."
     ],
     "sources": [
      {
       "title": "Getting started with Zendesk QA: Admin guide | Zendesk help",
       "url": "https://support.zendesk.com/hc/en-us/articles/10093676975898-Getting-started-with-Zendesk-QA-Admin-guide",
       "kind": "official",
       "checked_at": "2026-10-15"
      },
      {
       "title": "Using the Conversations view | Zendesk help",
       "url": "https://support.zendesk.com/hc/en-us/articles/7043661945370-Using-the-Conversations-view",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "인수 조건",
     "note": "출시 전 QA에서 확인할 기준이 됩니다."
    },
    {
     "term": "CSAT",
     "note": "상담 QA 점수와 고객 만족도를 함께 비교해 봅니다."
    }
   ],
   "confusable": [
    {
     "term": "QC",
     "difference": "QC(품질 관리)는 결과물을 검사해 결함을 잡는 데, QA는 결함이 생기지 않도록 과정 전체를 관리하는 데 초점이 있습니다."
    }
   ]
  },
  {
   "id": "agile",
   "term": "애자일",
   "original": "Agile",
   "korean": "애자일",
   "aliases": [
    "에자일",
    "애자일 방법론",
    "애자일 개발",
    "Agile 방법론"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "pm"
     ],
     "level": "입문",
     "importance": 4,
     "definition": "큰 계획을 한 번에 실행하기보다 짧은 주기로 만들고 고객 피드백을 받아 계속 고쳐 나가는 일하는 방식입니다. 애자일 선언문은 절차보다 사람과 소통, 문서보다 작동하는 소프트웨어, 계획 고수보다 변화 대응을 더 중시합니다.",
     "formula": null,
     "examples": [
      "애자일로 간다고 문서를 아예 안 쓰자는 건 아니에요.",
      "분기 계획은 잡되 2주마다 우선순위를 다시 보는 애자일 방식으로 하죠."
     ],
     "sources": [
      {
       "title": "Manifesto for Agile Software Development",
       "url": "https://agilemanifesto.org/",
       "kind": "official",
       "checked_at": "2026-10-15"
      },
      {
       "title": "What is Agile? | Atlassian",
       "url": "https://www.atlassian.com/agile",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "스크럼",
     "note": "애자일을 실천하는 대표적인 프레임워크입니다."
    },
    {
     "term": "칸반",
     "note": "흐름 관리에 초점을 둔 또 다른 애자일 방식입니다."
    }
   ],
   "confusable": [
    {
     "term": "워터폴",
     "difference": "워터폴은 기획→개발→테스트를 순서대로 한 번에 진행하고, 애자일은 짧은 주기로 반복합니다."
    }
   ]
  },
  {
   "id": "scrum",
   "term": "스크럼",
   "original": "Scrum",
   "korean": "스크럼",
   "aliases": [
    "스크럼 프레임워크",
    "데일리 스크럼",
    "데일리 스탠드업",
    "Daily Scrum"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "pm"
     ],
     "level": "실무",
     "importance": 4,
     "definition": "복잡한 문제를 짧은 스프린트 반복으로 풀어 가는 애자일 프레임워크입니다. PO·개발자·스크럼 마스터의 역할과 스프린트 계획, 매일 15분 동안 진행 상황을 맞추는 데일리 스크럼, 리뷰, 회고 같은 정해진 이벤트로 운영됩니다.",
     "formula": null,
     "examples": [
      "데일리 스크럼은 15분 안에 어제 한 일·오늘 할 일·막힌 점만 말하죠.",
      "우리 팀은 스크럼 이벤트는 지키되 스프린트는 2주로 할게요."
     ],
     "sources": [
      {
       "title": "The 2020 Scrum Guide",
       "url": "https://scrumguides.org/scrum-guide.html",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "스프린트",
     "note": "스크럼의 기본 작업 주기입니다."
    },
    {
     "term": "백로그",
     "note": "스크럼 팀이 할 일의 유일한 출처입니다."
    },
    {
     "term": "완료의 정의",
     "note": "스크럼에서 결과물의 품질 기준입니다."
    }
   ],
   "confusable": [
    {
     "term": "칸반",
     "difference": "스크럼은 정해진 주기(스프린트)와 역할이 있고, 칸반은 주기 없이 진행 중 작업 수를 제한하며 흐름을 관리합니다."
    }
   ]
  },
  {
   "id": "kanban",
   "term": "칸반",
   "original": "Kanban",
   "korean": "칸반",
   "aliases": [
    "간반",
    "칸반 보드",
    "Kanban board",
    "칸반보드"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "pm",
      "cx"
     ],
     "level": "실무",
     "importance": 3,
     "definition": "할 일·진행 중·완료 같은 열로 된 보드에 카드를 옮기며 일의 흐름을 눈으로 보는 애자일 방식입니다. 동시에 진행하는 작업 수(WIP)를 제한해 병목을 찾고 꾸준히 개선합니다.",
     "formula": null,
     "examples": [
      "상담 개선 과제는 칸반 보드로 관리하고 진행 중 칸은 3개까지만 두죠.",
      "검수 칸에 카드가 계속 쌓이는 게 병목 같아요."
     ],
     "sources": [
      {
       "title": "Configure columns | Jira Cloud | Atlassian Support",
       "url": "https://support.atlassian.com/jira-software-cloud/docs/configure-columns/",
       "kind": "official",
       "checked_at": "2026-10-15"
      },
      {
       "title": "What is Kanban in Project Management? | Atlassian",
       "url": "https://www.atlassian.com/agile/kanban",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "백로그",
     "note": "칸반 보드의 첫 열이 보통 백로그입니다."
    },
    {
     "term": "애자일",
     "note": "칸반은 애자일 실천 방식 중 하나입니다."
    }
   ],
   "confusable": [
    {
     "term": "스크럼",
     "difference": "칸반은 고정 주기 없이 흐름을 관리하고, 스크럼은 스프린트 단위로 계획하고 마무리합니다."
    }
   ]
  },
  {
   "id": "epic",
   "term": "에픽",
   "original": "Epic",
   "korean": "에픽",
   "aliases": [
    "에픽 이슈",
    "Epic 티켓",
    "큰 스토리",
    "대과제"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "pm"
     ],
     "level": "실무",
     "importance": 3,
     "definition": "여러 개의 작은 사용자 스토리로 나눌 수 있는 큰 작업 덩어리입니다. 보통 여러 스프린트에 걸쳐 완료되고, 여러 팀이 함께 맡기도 합니다.",
     "formula": null,
     "examples": [
      "'판매자 정산 개편'은 에픽으로 만들고 하위에 스토리를 쪼개 붙여 주세요.",
      "이 에픽은 이번 분기 안에 끝내는 걸 목표로 잡죠."
     ],
     "sources": [
      {
       "title": "What is an epic? | Jira Cloud | Atlassian Support",
       "url": "https://support.atlassian.com/jira-software-cloud/docs/what-is-an-epic/",
       "kind": "official",
       "checked_at": "2026-10-15"
      },
      {
       "title": "What is an Agile epic? | Atlassian",
       "url": "https://www.atlassian.com/agile/project-management/epics",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "사용자 스토리",
     "note": "에픽을 쪼갠 작은 단위입니다."
    },
    {
     "term": "로드맵",
     "note": "로드맵에는 주로 에픽 단위로 일정을 표시합니다."
    }
   ],
   "confusable": [
    {
     "term": "사용자 스토리",
     "difference": "스토리는 한 스프린트 안에 끝낼 만한 작은 단위이고, 에픽은 여러 스토리를 묶은 큰 단위입니다."
    }
   ]
  },
  {
   "id": "acceptance_criteria",
   "term": "인수 조건",
   "original": "Acceptance Criteria",
   "korean": "인수 조건",
   "aliases": [
    "AC",
    "인수 기준",
    "수락 조건",
    "완료 조건",
    "에이씨"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "pm"
     ],
     "level": "실무",
     "importance": 4,
     "definition": "하나의 사용자 스토리나 기능이 완료로 인정받으려면 반드시 충족해야 하는 구체적인 조건입니다. 미리 정해 두면 개발자·QA·기획자가 '다 됐다'의 기준을 똑같이 이해할 수 있습니다.",
     "formula": null,
     "examples": [
      "인수 조건에 '품절 옵션은 선택 불가로 표시된다'를 꼭 넣어 주세요.",
      "인수 조건을 테스트 케이스로 바로 옮길 수 있게 문장으로 적어 둘게요."
     ],
     "sources": [
      {
       "title": "What is Acceptance Criteria? | Atlassian",
       "url": "https://www.atlassian.com/work-management/project-management/acceptance-criteria",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "사용자 스토리",
     "note": "인수 조건은 각 스토리에 붙습니다."
    },
    {
     "term": "QA",
     "note": "QA는 인수 조건을 기준으로 테스트합니다."
    }
   ],
   "confusable": [
    {
     "term": "완료의 정의",
     "difference": "인수 조건은 스토리마다 다른 개별 기준이고, 완료의 정의는 모든 작업에 공통으로 적용되는 품질 기준입니다."
    }
   ]
  },
  {
   "id": "dod",
   "term": "완료의 정의",
   "original": "Definition of Done",
   "korean": "완료의 정의",
   "aliases": [
    "DoD",
    "디오디",
    "완료 정의",
    "Done 기준"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "pm"
     ],
     "level": "실무",
     "importance": 3,
     "definition": "결과물이 '완료'로 인정받기 위해 갖춰야 할 품질 기준을 팀이 함께 정한 것입니다. 이 기준을 만족하지 못한 작업은 이번 스프린트 결과물에 포함하지 않습니다.",
     "formula": null,
     "examples": [
      "우리 DoD에 코드 리뷰와 QA 통과가 들어가 있으니 이 건은 아직 완료가 아니에요.",
      "DoD에 모니터링 대시보드 추가도 넣을지 회고 때 정하죠."
     ],
     "sources": [
      {
       "title": "The 2020 Scrum Guide",
       "url": "https://scrumguides.org/scrum-guide.html",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "스크럼",
     "note": "스크럼 가이드에서 결과물 품질 기준으로 정의합니다."
    },
    {
     "term": "인수 조건",
     "note": "개별 스토리 기준인 인수 조건과 함께 씁니다."
    }
   ],
   "confusable": [
    {
     "term": "인수 조건",
     "difference": "완료의 정의는 모든 작업 공통 기준, 인수 조건은 스토리별 기준입니다."
    }
   ]
  },
  {
   "id": "retrospective",
   "term": "회고",
   "original": "Sprint Retrospective",
   "korean": "스프린트 회고",
   "aliases": [
    "레트로",
    "레트로스펙티브",
    "Retro",
    "스프린트 회고"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "pm"
     ],
     "level": "실무",
     "importance": 3,
     "definition": "스프린트를 마무리하며 팀이 사람·도구·과정 등 일하는 방식을 돌아보고 다음에 무엇을 개선할지 정하는 시간입니다. 스크럼의 마지막 이벤트입니다.",
     "formula": null,
     "examples": [
      "회고에서 나온 '배포 전 체크리스트 만들기'는 담당자를 정해 다음 스프린트에 넣죠.",
      "이번 회고는 잘한 점·아쉬운 점·시도할 점 세 칸으로 진행할게요."
     ],
     "sources": [
      {
       "title": "The 2020 Scrum Guide",
       "url": "https://scrumguides.org/scrum-guide.html",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "스프린트",
     "note": "회고는 스프린트 마지막에 합니다."
    },
    {
     "term": "스크럼",
     "note": "스크럼의 정해진 이벤트 중 하나입니다."
    }
   ],
   "confusable": [
    {
     "term": "스프린트 리뷰",
     "difference": "리뷰는 만든 결과물을 이해관계자와 점검하고, 회고는 팀의 일하는 방식을 돌아봅니다."
    }
   ]
  },
  {
   "id": "okr",
   "term": "OKR",
   "original": "Objectives and Key Results",
   "korean": "목표와 핵심 결과",
   "aliases": [
    "오케이알",
    "OKRs",
    "목표 및 핵심결과",
    "목표·핵심 결과"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "pm",
      "data",
      "marketing"
     ],
     "level": "실무",
     "importance": 4,
     "definition": "이루고 싶은 방향을 담은 정성적인 목표(Objective)와 그 달성 여부를 숫자로 확인하는 핵심 결과(Key Results)를 짝지어 관리하는 목표 설정 방식입니다. 보통 목표 1~3개에 목표마다 핵심 결과 3~5개를 둡니다.",
     "formula": null,
     "examples": [
      "이번 분기 OKR 목표는 '첫 구매 경험을 쉽게'로, 핵심 결과는 첫 구매 전환율로 잡죠.",
      "이건 해야 할 프로젝트지 핵심 결과는 아니니까 측정 가능한 숫자로 바꿔 주세요."
     ],
     "sources": [
      {
       "title": "Objectives and Key Results (OKRs) | Atlassian Team Playbook",
       "url": "https://www.atlassian.com/team-playbook/plays/okrs",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "KPI",
     "note": "핵심 결과에는 KPI가 자주 쓰입니다."
    },
    {
     "term": "북극성 지표",
     "note": "OKR 목표가 북극성 지표를 움직이도록 연결합니다."
    },
    {
     "term": "로드맵",
     "note": "로드맵 과제가 어떤 OKR에 기여하는지 연결합니다."
    }
   ],
   "confusable": [
    {
     "term": "KPI",
     "difference": "KPI는 꾸준히 지켜보는 성과 지표이고, OKR은 일정 기간 도전적 목표와 그 측정 결과를 묶은 틀입니다."
    }
   ]
  },
  {
   "id": "rice",
   "term": "RICE",
   "original": "Reach, Impact, Confidence, Effort",
   "korean": "RICE 우선순위 점수",
   "aliases": [
    "라이스",
    "RICE 점수",
    "RICE 스코어",
    "RICE 프레임워크"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "pm"
     ],
     "level": "실무",
     "importance": 3,
     "definition": "아이디어마다 도달 범위(Reach), 영향도(Impact), 확신도(Confidence), 노력(Effort)을 추정해 하나의 점수로 비교하는 우선순위 방법입니다. 노력이 클수록 점수가 낮아지도록 노력으로 나누어 계산합니다.",
     "formula": "RICE 점수 = (Reach × Impact × Confidence) ÷ Effort",
     "examples": [
      "후보 기능 다섯 개를 RICE로 매겨 보니 재입고 알림이 1등이네요.",
      "Confidence가 50%밖에 안 되면 먼저 작게 실험해 보는 게 낫겠어요."
     ],
     "sources": [
      {
       "title": "RICE: Simple prioritization for product managers | Intercom",
       "url": "https://www.intercom.com/blog/rice-simple-prioritization-for-product-managers/",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "백로그",
     "note": "백로그 항목 순서를 정할 때 씁니다."
    },
    {
     "term": "로드맵",
     "note": "RICE 결과로 로드맵에 올릴 과제를 고릅니다."
    }
   ],
   "confusable": [
    {
     "term": "ICE",
     "difference": "ICE는 영향·확신·쉬움 세 요소만 쓰고 도달 범위(Reach)를 따로 보지 않습니다."
    }
   ]
  },
  {
   "id": "persona",
   "term": "페르소나",
   "original": "Persona",
   "korean": "페르소나",
   "aliases": [
    "퍼소나",
    "사용자 페르소나",
    "고객 페르소나",
    "유저 페르소나"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "pm",
      "marketing"
     ],
     "level": "실무",
     "importance": 3,
     "definition": "제품의 대표 사용자나 목표 사용자를 가상의 한 사람처럼 구체적으로 그려 낸 설명입니다. 실제 조사를 바탕으로 목표·불편·행동을 담아, 팀이 누구를 위해 만드는지 같은 그림을 보게 합니다.",
     "formula": null,
     "examples": [
      "'퇴근길에 모바일로 장보는 30대 맞벌이' 페르소나 기준으로 홈 화면을 다시 보죠.",
      "페르소나가 너무 많으면 우선순위가 흐려지니 핵심 두 개만 남겨요."
     ],
     "sources": [
      {
       "title": "Understand your users by developing profiles | Digital.gov",
       "url": "https://digital.gov/guides/research-collaboration/user-needs/user-profiles",
       "kind": "official",
       "checked_at": "2026-10-15"
      },
      {
       "title": "Personas | Nielsen Norman Group",
       "url": "https://www.nngroup.com/articles/persona/",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "고객 여정 지도",
     "note": "페르소나 한 명을 정해 그 사람의 여정을 그립니다."
    },
    {
     "term": "JTBD",
     "note": "사람 특성 대신 '해결하려는 일'로 고객을 보는 관점입니다."
    }
   ],
   "confusable": [
    {
     "term": "고객 세그먼트",
     "difference": "세그먼트는 데이터로 나눈 고객 집단이고, 페르소나는 그 집단을 한 사람처럼 그린 이야기입니다."
    }
   ]
  },
  {
   "id": "journey_map",
   "term": "고객 여정 지도",
   "original": "Customer Journey Map",
   "korean": "고객 여정 지도",
   "aliases": [
    "고객 여정 맵",
    "저니맵",
    "저니 맵",
    "CJM",
    "여정 지도"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "pm",
      "cx",
      "marketing"
     ],
     "level": "실무",
     "importance": 3,
     "definition": "한 사람이 목표를 이루기까지 거치는 과정을 단계별로 시각화한 그림입니다. 단계마다 고객의 행동·생각·감정과 접점을 함께 적어 불편한 곳을 찾고 개선 과제를 정하는 데 씁니다.",
     "formula": null,
     "examples": [
      "반품 여정 지도를 그려 보니 '회수 일정 확인' 단계에서 문의가 가장 많네요.",
      "여정 지도의 감정 곡선이 떨어지는 구간부터 개선 과제를 뽑죠."
     ],
     "sources": [
      {
       "title": "Map your users' and system's journeys | Digital.gov",
       "url": "https://digital.gov/guides/research-collaboration/user-needs/journeys",
       "kind": "official",
       "checked_at": "2026-10-15"
      },
      {
       "title": "Journey Mapping 101 | Nielsen Norman Group",
       "url": "https://www.nngroup.com/articles/journey-mapping-101/",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "페르소나",
     "note": "여정 지도는 보통 특정 페르소나를 기준으로 그립니다."
    },
    {
     "term": "전환율",
     "note": "여정 단계별 이탈을 전환율로 확인합니다."
    }
   ],
   "confusable": [
    {
     "term": "퍼널",
     "difference": "퍼널은 단계별 숫자(전환·이탈)를, 여정 지도는 고객의 행동·감정·접점을 정성적으로 보여 줍니다."
    }
   ]
  },
  {
   "id": "feature_flag",
   "term": "피처 플래그",
   "original": "Feature Flag",
   "korean": "기능 플래그",
   "aliases": [
    "피처 토글",
    "Feature Toggle",
    "피처플래그",
    "기능 토글"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "pm"
     ],
     "level": "실무",
     "importance": 3,
     "definition": "코드를 새로 배포하지 않고도 설정만 바꿔 특정 기능을 켜고 끌 수 있게 하는 개발 기법입니다. 여러 버전의 동작을 한 번에 배포해 두고 실행 중에 어느 쪽을 쓸지 고릅니다.",
     "formula": null,
     "examples": [
      "새 결제 화면은 피처 플래그로 직원한테만 먼저 켜 볼게요.",
      "문제 생기면 롤백 말고 플래그만 끄면 됩니다."
     ],
     "sources": [
      {
       "title": "Get started with LaunchDarkly | LaunchDarkly Docs",
       "url": "https://launchdarkly.com/docs/home/getting-started",
       "kind": "official",
       "checked_at": "2026-10-15"
      },
      {
       "title": "Feature Toggles (aka Feature Flags) | martinfowler.com",
       "url": "https://martinfowler.com/articles/feature-toggles.html",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "릴리스",
     "note": "플래그로 배포와 릴리스 시점을 나눌 수 있습니다."
    },
    {
     "term": "A/B 테스트",
     "note": "플래그로 사용자 일부에게만 기능을 보여 실험합니다."
    }
   ],
   "confusable": [
    {
     "term": "배포",
     "difference": "배포는 코드를 올리는 것이고, 피처 플래그는 이미 올라간 기능을 켜고 끄는 스위치입니다."
    }
   ]
  },
  {
   "id": "tech_debt",
   "term": "기술 부채",
   "original": "Technical Debt",
   "korean": "기술 부채",
   "aliases": [
    "테크 뎁트",
    "기술부채",
    "Tech Debt",
    "기술적 부채"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "pm"
     ],
     "level": "실무",
     "importance": 3,
     "definition": "코드나 구조의 내부 품질이 떨어져서 나중에 기능을 고치거나 더할 때 추가로 드는 노력을 빚에 빗댄 말입니다. 그 추가 노력을 이자처럼 계속 내게 되므로 적절한 때에 정리해(갚아) 줘야 합니다.",
     "formula": null,
     "examples": [
      "주문 모듈 기술 부채 때문에 간단한 변경도 일주일씩 걸려요.",
      "이번 분기엔 스프린트마다 20%를 기술 부채 정리에 쓰죠."
     ],
     "sources": [
      {
       "title": "The WyCash Portfolio Management System (Ward Cunningham, OOPSLA '92)",
       "url": "https://c2.com/doc/oopsla92.html",
       "kind": "official",
       "checked_at": "2026-10-15"
      },
      {
       "title": "Technical Debt | martinfowler.com",
       "url": "https://martinfowler.com/bliki/TechnicalDebt.html",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "백로그",
     "note": "기술 부채 정리 작업도 백로그에 올려 우선순위를 매깁니다."
    },
    {
     "term": "MVP",
     "note": "MVP를 서두르면 기술 부채가 생기기 쉽습니다."
    }
   ],
   "confusable": [
    {
     "term": "버그",
     "difference": "버그는 지금 잘못 동작하는 문제이고, 기술 부채는 지금은 동작하지만 앞으로 변경을 어렵게 만드는 구조 문제입니다."
    }
   ]
  },
  {
   "id": "north_star",
   "term": "북극성 지표",
   "original": "North Star Metric",
   "korean": "북극성 지표",
   "aliases": [
    "노스스타 메트릭",
    "NSM",
    "북극성 메트릭",
    "North Star"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "pm",
      "data"
     ],
     "level": "실무",
     "importance": 4,
     "definition": "고객이 제품에서 얻는 핵심 가치를 가장 잘 나타내는 단 하나의 지표입니다. 제품·마케팅이 움직일 수 있고, 매출보다 먼저 움직이는 선행 지표여야 좋습니다.",
     "formula": null,
     "examples": [
      "우리 북극성 지표는 '주간 재구매 고객 수'로 하고 팀별 입력 지표를 연결하죠.",
      "가입자 수는 가치를 직접 보여 주지 않아서 북극성 지표로는 약해요."
     ],
     "sources": [
      {
       "title": "What Makes a Good vs Bad North Star Metric | Amplitude",
       "url": "https://www.amplitude.com/blog/good-bad-north-star-metric",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "OKR",
     "note": "OKR 목표를 북극성 지표와 연결합니다."
    },
    {
     "term": "리텐션",
     "note": "북극성 지표는 리텐션 같은 가치 지표와 맞닿아 있는 경우가 많습니다."
    }
   ],
   "confusable": [
    {
     "term": "KPI",
     "difference": "KPI는 여러 개 둘 수 있는 성과 지표이고, 북극성 지표는 회사 전체가 맞추는 단 하나의 핵심 지표입니다."
    },
    {
     "term": "매출",
     "difference": "매출은 결과를 보여 주는 후행 지표이고, 북극성 지표는 앞으로의 성장을 가리키는 선행 지표입니다."
    }
   ]
  },
  {
   "id": "pmf",
   "term": "PMF",
   "original": "Product-Market Fit",
   "korean": "제품-시장 적합성",
   "aliases": [
    "피엠에프",
    "프로덕트 마켓 핏",
    "제품 시장 적합성",
    "PM 핏"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "pm",
      "marketing"
     ],
     "level": "심화",
     "importance": 4,
     "definition": "제품이 목표 고객의 필요를 제대로 채워 시장에서 받아들여지는 상태를 말합니다. 스타트업만의 과제가 아니라, 시장과 고객 기대가 바뀌면 이미 자리 잡은 회사도 계속 다시 찾아야 하는 상태입니다.",
     "formula": null,
     "examples": [
      "신규 판매자 쪽은 아직 PMF 전이라 확장보다 리텐션부터 보죠.",
      "재구매율이 안정되면 PMF 신호로 볼 수 있을 것 같아요."
     ],
     "sources": [
      {
       "title": "Part 4: The only thing that matters (Marc Andreessen)",
       "url": "https://pmarchive.com/guide_to_startups_part4.html",
       "kind": "official",
       "checked_at": "2026-10-15"
      },
      {
       "title": "Navigating product-market fit: Intercom's PMF Panel | Intercom",
       "url": "https://www.intercom.com/blog/navigating-product-market-fit-pmf-panel/",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "MVP",
     "note": "MVP로 실험하며 PMF를 찾아 갑니다."
    },
    {
     "term": "리텐션",
     "note": "리텐션이 PMF를 판단하는 대표 신호로 쓰입니다."
    }
   ],
   "confusable": [
    {
     "term": "MVP",
     "difference": "MVP는 제품의 첫 버전이고, PMF는 그 제품이 시장에 맞아떨어진 상태입니다."
    }
   ]
  },
  {
   "id": "jtbd",
   "term": "JTBD",
   "original": "Jobs To Be Done",
   "korean": "해결할 과업",
   "aliases": [
    "제이티비디",
    "잡투비던",
    "Jobs-to-be-Done",
    "JTBD 프레임워크"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "pm"
     ],
     "level": "심화",
     "importance": 3,
     "definition": "고객이 이루려는 '일(과업)'을 해결하려고 제품을 고용한다고 보는 관점입니다. 나이·직업 같은 고객 특성보다 고객이 해결하려는 일을 중심으로 제품과 마케팅을 설계합니다.",
     "formula": null,
     "examples": [
      "새벽배송 고객의 JTBD는 '아침 식사 걱정 없이 출근하기'에 가까운 것 같아요.",
      "인터뷰 질문을 JTBD 관점으로 바꿔서 '그 전에는 어떻게 해결했나요?'를 꼭 넣죠."
     ],
     "sources": [
      {
       "title": "Jobs to Be Done Theory - Christensen Institute",
       "url": "https://www.christenseninstitute.org/theory/jobs-to-be-done/",
       "kind": "official",
       "checked_at": "2026-10-15"
      },
      {
       "title": "How to market the Job-to-be-Done | Intercom",
       "url": "https://www.intercom.com/blog/videos/marketing-the-job-to-be-done/",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "페르소나",
     "note": "JTBD는 페르소나의 사람 특성 대신 고객의 과업에 초점을 둡니다."
    },
    {
     "term": "사용자 스토리",
     "note": "JTBD를 상황 중심의 잡 스토리로 적기도 합니다."
    }
   ],
   "confusable": [
    {
     "term": "페르소나",
     "difference": "페르소나는 '누구인가'를, JTBD는 '무엇을 해결하려 하는가'를 중심에 둡니다."
    }
   ]
  },
  {
   "id": "story_point",
   "term": "스토리 포인트",
   "original": "Story Point",
   "korean": "스토리 포인트",
   "aliases": [
    "SP",
    "스토리포인트",
    "포인트",
    "벨로시티",
    "Velocity"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "pm"
     ],
     "level": "심화",
     "importance": 3,
     "definition": "작업을 시간 대신 다른 작업과 비교한 상대적인 크기(노력·복잡도)로 추정하는 단위로, 시간이나 일수와 직접 대응하지 않습니다. 한 스프린트에 팀이 완료하는 포인트 양을 벨로시티라고 하며, 벨로시티가 안정되면 남은 일이 몇 스프린트 걸릴지 예측하는 데 씁니다.",
     "formula": null,
     "examples": [
      "이 스토리는 지난번 3포인트짜리보다 조금 커 보여서 5로 할게요.",
      "최근 세 스프린트 벨로시티가 30 정도라 이번에도 30포인트까지만 담죠."
     ],
     "sources": [
      {
       "title": "What are story points? | Jira Cloud | Atlassian Support",
       "url": "https://support.atlassian.com/jira-software-cloud/docs/what-are-story-points/",
       "kind": "official",
       "checked_at": "2026-10-15"
      },
      {
       "title": "Estimate a work item | Jira Cloud | Atlassian Support",
       "url": "https://support.atlassian.com/jira-software-cloud/docs/estimate-an-issue/",
       "kind": "official",
       "checked_at": "2026-10-15"
      },
      {
       "title": "Story points and estimation | Atlassian",
       "url": "https://www.atlassian.com/agile/project-management/estimation",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      },
      {
       "title": "Sprint velocity in Scrum | Atlassian",
       "url": "https://www.atlassian.com/agile/project-management/velocity-scrum",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "사용자 스토리",
     "note": "스토리 포인트는 스토리 단위로 매깁니다."
    },
    {
     "term": "스프린트",
     "note": "벨로시티로 한 스프린트 분량을 정합니다."
    }
   ],
   "confusable": [
    {
     "term": "작업 시간",
     "difference": "시간 추정은 절대값이고, 스토리 포인트는 팀 안에서만 의미 있는 상대값이라 팀끼리 비교하면 안 됩니다."
    }
   ]
  },
  {
   "id": "pdp",
   "term": "상품 상세 페이지",
   "original": "Product Detail Page",
   "korean": "상품 상세 페이지",
   "aliases": [
    "PDP",
    "피디피",
    "상세페이지",
    "상품상세",
    "상세 페이지"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce"
     ],
     "roles": [
      "pm",
      "marketing"
     ],
     "level": "입문",
     "importance": 4,
     "definition": "상품 하나의 사진, 설명, 가격, 옵션, 리뷰 등 구매 결정에 필요한 정보를 모아 보여 주는 페이지입니다. 고객이 장바구니에 담을지 결정하는 핵심 화면입니다.",
     "formula": null,
     "examples": [
      "PDP에서 장바구니 담기 버튼이 스크롤 아래로 밀려서 전환율이 떨어진 것 같아요.",
      "PDP 상단에 배송 도착 예정일을 노출하는 실험 해 보죠."
     ],
     "sources": [
      {
       "title": "방문 페이지 요구사항 - Google Merchant Center 고객센터",
       "url": "https://support.google.com/merchants/answer/4752265?hl=ko",
       "kind": "official",
       "checked_at": "2026-10-15"
      },
      {
       "title": "What Is a PDP in Ecommerce? | Shopify",
       "url": "https://www.shopify.com/blog/what-is-pdp-in-ecommerce",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "체크아웃",
     "note": "PDP 다음 단계로 이어지는 구매 흐름입니다."
    },
    {
     "term": "전환율",
     "note": "PDP 개선 효과는 장바구니 담기·구매 전환율로 확인합니다."
    },
    {
     "term": "SKU",
     "note": "옵션별 SKU 정보가 PDP에 표시됩니다."
    }
   ],
   "confusable": [
    {
     "term": "PLP",
     "difference": "PLP(상품 목록 페이지)는 여러 상품을 나열하고, PDP는 상품 하나를 자세히 보여 줍니다."
    }
   ]
  },
  {
   "id": "checkout",
   "term": "체크아웃",
   "original": "Checkout",
   "korean": "주문·결제 단계",
   "aliases": [
    "체크 아웃",
    "결제 페이지",
    "주문서",
    "결제 단계",
    "Checkout 페이지"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce"
     ],
     "roles": [
      "pm",
      "data"
     ],
     "level": "입문",
     "importance": 4,
     "definition": "고객이 장바구니에 상품을 담은 뒤 배송 정보와 결제 정보를 입력하고 주문을 완료하는 단계입니다. 이 단계의 이탈을 줄이는 것이 이커머스 기획의 주요 과제입니다.",
     "formula": null,
     "examples": [
      "체크아웃 단계에서 배송지 입력 칸이 많아 이탈이 커요.",
      "체크아웃 진입 대비 주문 완료율을 매일 대시보드로 봐 주세요."
     ],
     "sources": [
      {
       "title": "Shopify Checkout | Shopify Help Center",
       "url": "https://help.shopify.com/en/manual/checkout-settings",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "PG",
     "note": "체크아웃의 결제는 보통 PG를 통해 처리됩니다."
    },
    {
     "term": "전환율",
     "note": "체크아웃 전환율로 결제 흐름의 건강도를 봅니다."
    },
    {
     "term": "상품 상세 페이지",
     "note": "PDP에서 체크아웃으로 이어집니다."
    }
   ],
   "confusable": [
    {
     "term": "장바구니",
     "difference": "장바구니는 살 상품을 모아 두는 곳이고, 체크아웃은 실제로 주문·결제하는 단계입니다."
    }
   ]
  },
  {
   "id": "sku",
   "term": "SKU",
   "original": "Stock Keeping Unit",
   "korean": "재고 관리 단위",
   "aliases": [
    "에스케이유",
    "품목 코드",
    "상품 코드",
    "재고관리코드",
    "SKU 코드"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce"
     ],
     "roles": [
      "pm",
      "cx",
      "data"
     ],
     "level": "입문",
     "importance": 4,
     "definition": "재고를 관리하고 판매를 집계하려고 상품마다 붙이는 내부 코드입니다. 같은 상품이라도 색상·사이즈 같은 옵션이 다르면 보통 SKU를 따로 둡니다.",
     "formula": null,
     "examples": [
      "이 티셔츠는 색상 3개, 사이즈 4개라 SKU가 12개예요.",
      "품절 문의가 오면 상품명 말고 SKU로 재고를 조회해 주세요."
     ],
     "sources": [
      {
       "title": "SKU | Shopify Help Center",
       "url": "https://help.shopify.com/en/manual/products/details/sku",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "상품 상세 페이지",
     "note": "옵션별 SKU의 재고 상태가 PDP에 반영됩니다."
    },
    {
     "term": "GMV",
     "note": "SKU별 판매 금액을 모으면 거래액을 볼 수 있습니다."
    }
   ],
   "confusable": [
    {
     "term": "바코드(GTIN)",
     "difference": "바코드는 제조사가 붙이는 국제 공통 코드이고, SKU는 판매자가 내부 관리용으로 정하는 코드입니다."
    }
   ]
  },
  {
   "id": "open_market",
   "term": "오픈마켓",
   "original": "Open Market",
   "korean": "오픈마켓",
   "aliases": [
    "오픈 마켓",
    "마켓플레이스",
    "통신판매중개",
    "중개형 쇼핑몰",
    "Marketplace"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce"
     ],
     "roles": [
      "pm",
      "marketing"
     ],
     "level": "입문",
     "importance": 3,
     "definition": "여러 판매자가 입점해 상품을 팔고 플랫폼은 거래를 연결해 주는 온라인 장터입니다. 법률상으로는 사이버몰을 이용하게 해 거래 당사자 사이의 통신판매를 알선하는 '통신판매중개'에 해당하며, 플랫폼이 직접 판매 당사자가 아닌 경우가 많습니다.",
     "formula": null,
     "examples": [
      "오픈마켓 상품은 판매자가 직접 배송해서 CS도 판매자 연결이 필요해요.",
      "직매입 상품과 오픈마켓 상품을 PDP에서 구분해 보여 주죠."
     ],
     "sources": [
      {
       "title": "전자상거래 등에서의 소비자보호에 관한 법률 제2조 (한국법제연구원 영문/국문 법령)",
       "url": "https://elaw.klri.re.kr/kor_service/lawViewMultiContent.do?hseq=38513",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "양면 시장",
     "note": "오픈마켓은 판매자와 구매자를 잇는 대표적인 양면 시장입니다."
    },
    {
     "term": "테이크 레이트",
     "note": "오픈마켓 수익은 거래액에서 가져가는 수수료율로 봅니다."
    },
    {
     "term": "정산",
     "note": "판매자에게 판매 대금을 정산해 줍니다."
    }
   ],
   "confusable": [
    {
     "term": "직매입",
     "difference": "직매입은 플랫폼이 상품을 사서 직접 파는 것이고, 오픈마켓은 판매자의 거래를 중개합니다."
    }
   ]
  },
  {
   "id": "pg",
   "term": "PG",
   "original": "Payment Gateway",
   "korean": "전자지급결제대행",
   "aliases": [
    "피지",
    "PG사",
    "결제대행사",
    "결제 대행",
    "전자결제대행"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce"
     ],
     "roles": [
      "pm",
      "cx"
     ],
     "level": "실무",
     "importance": 4,
     "definition": "온라인에서 상품을 살 때 결제 정보를 주고받고, 대금 결제를 대신 처리하거나 중개해 주는 서비스나 회사입니다. 쇼핑몰이 카드사 등과 일일이 계약하지 않아도 여러 결제 수단을 받을 수 있게 해 줍니다.",
     "formula": null,
     "examples": [
      "간편결제 추가는 PG사 쪽 연동 일정부터 확인해 볼게요.",
      "결제 실패 문의는 PG 거래 번호로 먼저 조회해 주세요."
     ],
     "sources": [
      {
       "title": "전자금융거래법 제2조 (한국법제연구원 영문/국문 법령)",
       "url": "https://elaw.klri.re.kr/kor_service/lawViewMultiContent.do?hseq=38503",
       "kind": "official",
       "checked_at": "2026-10-15"
      },
      {
       "title": "사장님이 꼭 알아야 할 PG 용어 정리 | 토스페이먼츠",
       "url": "https://www.tosspayments.com/blog/articles/semo-8",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "체크아웃",
     "note": "체크아웃 단계의 결제를 PG가 처리합니다."
    },
    {
     "term": "정산",
     "note": "PG는 수수료를 떼고 가맹점에 대금을 정산합니다."
    }
   ],
   "confusable": [
    {
     "term": "VAN",
     "difference": "VAN은 카드 결제 승인 정보를 카드사와 주고받는 망을 주로 맡고, PG는 온라인 결제와 대금 정산을 대행합니다."
    }
   ]
  },
  {
   "id": "settlement",
   "term": "정산",
   "original": "Settlement",
   "korean": "정산",
   "aliases": [
    "판매자 정산",
    "대금 정산",
    "정산금",
    "정산 주기",
    "셀러 정산"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce"
     ],
     "roles": [
      "pm",
      "cx"
     ],
     "level": "실무",
     "importance": 3,
     "definition": "판매된 금액에서 카드사·결제대행·플랫폼 수수료 등을 뺀 뒤 판매자(가맹점)에게 줄 금액을 계산해 지급하는 과정입니다. 일·주·월 단위 등 계약에 따라 정산 주기가 달라집니다.",
     "formula": null,
     "examples": [
      "이번 달 정산금이 적다는 판매자 문의가 늘어서 수수료 내역 화면을 보강하죠.",
      "반품 건은 다음 정산에서 차감된다고 안내해 주세요."
     ],
     "sources": [
      {
       "title": "[보도자료] 티메프 사태 재발 방지를 위한 전자지급결제대행(PG)업 제도개선안 발표 - 금융위원회",
       "url": "https://fsc.go.kr/no010101/83047?curPage=&srchBeginDt=&srchCtgry=&srchEndDt=&srchKey=&srchText=",
       "kind": "official",
       "checked_at": "2026-10-15"
      },
      {
       "title": "PG업자의 정산자금 보호 및 관리·감독 장치 마련을 위한 「전자금융거래법」 개정법률안 공포 - 금융위원회",
       "url": "https://www.fsc.go.kr/po010101/85855?srchCtgry=&curPage=&srchKey=&srchText=&srchBeginDt=&srchEndDt=",
       "kind": "official",
       "checked_at": "2026-10-15"
      },
      {
       "title": "사장님이 꼭 알아야 할 PG 용어 정리 | 토스페이먼츠",
       "url": "https://www.tosspayments.com/blog/articles/semo-8",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "PG",
     "note": "결제 대금 정산은 PG를 거치는 경우가 많습니다."
    },
    {
     "term": "테이크 레이트",
     "note": "정산 전에 떼는 플랫폼 수수료율입니다."
    },
    {
     "term": "매출",
     "note": "정산금은 매출에서 수수료를 뺀 금액이라 매출과 다릅니다."
    }
   ],
   "confusable": [
    {
     "term": "매출",
     "difference": "매출은 고객이 결제한 금액이고, 정산금은 수수료를 뺀 뒤 판매자에게 실제로 지급되는 금액입니다."
    }
   ]
  },
  {
   "id": "api",
   "term": "API",
   "original": "Application Programming Interface",
   "korean": "응용 프로그램 인터페이스",
   "aliases": [
    "에이피아이",
    "오픈 API",
    "API 연동",
    "인터페이스"
   ],
   "senses": [
    {
     "industries": [
      "platform"
     ],
     "roles": [
      "pm",
      "cx"
     ],
     "level": "입문",
     "importance": 4,
     "definition": "서로 다른 소프트웨어가 기능이나 데이터를 주고받을 수 있도록 정해 둔 규칙과 기능의 묶음입니다. 정해진 형식으로 요청하면 약속된 형식의 응답을 돌려줍니다.",
     "formula": null,
     "examples": [
      "배송 조회는 택배사 API로 받아와서 주문 상세에 보여 줄게요.",
      "판매자 API 문서에 오류 코드 설명이 없다는 문의가 많아요."
     ],
     "sources": [
      {
       "title": "API - MDN Web Docs 용어 사전",
       "url": "https://developer.mozilla.org/ko/docs/Glossary/API",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "SDK",
     "note": "SDK는 API를 쉽게 쓰도록 도구를 묶어 줍니다."
    },
    {
     "term": "온보딩",
     "note": "플랫폼 파트너 온보딩에서 API 연동이 첫 관문입니다."
    }
   ],
   "confusable": [
    {
     "term": "SDK",
     "difference": "API는 소프트웨어끼리 주고받는 규칙이고, SDK는 개발에 필요한 도구·라이브러리·문서를 묶은 꾸러미입니다."
    }
   ]
  },
  {
   "id": "sdk",
   "term": "SDK",
   "original": "Software Development Kit",
   "korean": "소프트웨어 개발 키트",
   "aliases": [
    "에스디케이",
    "개발 키트",
    "개발도구 키트",
    "SDK 연동"
   ],
   "senses": [
    {
     "industries": [
      "platform"
     ],
     "roles": [
      "pm"
     ],
     "level": "실무",
     "importance": 3,
     "definition": "특정 플랫폼용 앱을 만들 때 필요한 라이브러리, 코드 예제, 문서 등을 한데 묶은 개발 도구 모음입니다. API를 직접 다루는 수고를 줄여 연동을 빠르게 해 줍니다.",
     "formula": null,
     "examples": [
      "결제 SDK 새 버전이 나와서 앱 업데이트 일정에 넣어야 해요.",
      "파트너사가 SDK로 붙이면 연동 기간을 일주일 안으로 줄일 수 있어요."
     ],
     "sources": [
      {
       "title": "What is an SDK? | AWS",
       "url": "https://aws.amazon.com/what-is/sdk/",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "API",
     "note": "SDK 안에는 API를 쉽게 부르는 코드가 들어 있습니다."
    }
   ],
   "confusable": [
    {
     "term": "API",
     "difference": "API는 주고받는 규칙(창구)이고, SDK는 그 창구를 쓰기 쉽게 만든 도구 꾸러미입니다."
    }
   ]
  },
  {
   "id": "onboarding",
   "term": "온보딩",
   "original": "Onboarding",
   "korean": "신규 사용자 안내",
   "aliases": [
    "온 보딩",
    "사용자 온보딩",
    "유저 온보딩",
    "고객 온보딩",
    "Onboarding flow"
   ],
   "senses": [
    {
     "industries": [
      "platform"
     ],
     "roles": [
      "pm",
      "marketing",
      "cx"
     ],
     "level": "입문",
     "importance": 4,
     "definition": "새로 가입한 사용자나 고객을 맞이하고 제품을 익히게 도와, 제품이 주는 가치를 빨리 경험하게 하는 과정입니다. 첫인상을 결정하고 이후 이용 습관과 리텐션에 큰 영향을 줍니다.",
     "formula": null,
     "examples": [
      "가입 후 첫 주문까지 온보딩 단계를 세 개로 줄여 보죠.",
      "온보딩 중 이탈이 많은 화면에 툴팁 대신 예시 데이터를 보여 주면 어떨까요?"
     ],
     "sources": [
      {
       "title": "Onboarding - Growth & communications - Material Design",
       "url": "https://m1.material.io/growth-communications/onboarding.html",
       "kind": "official",
       "checked_at": "2026-10-15"
      },
      {
       "title": "What is customer onboarding? | Intercom",
       "url": "https://www.intercom.com/blog/what-is-customer-onboarding/",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "리텐션",
     "note": "온보딩 품질이 초기 리텐션을 좌우합니다."
    },
    {
     "term": "전환율",
     "note": "온보딩 단계별 완료율로 개선 효과를 봅니다."
    }
   ],
   "confusable": [
    {
     "term": "직원 온보딩",
     "difference": "인사 분야의 온보딩은 신규 입사자 적응 과정을 말하고, 제품 기획에서는 신규 사용자 안내를 뜻합니다."
    }
   ]
  },
  {
   "id": "two_sided_market",
   "term": "양면 시장",
   "original": "Two-Sided Market",
   "korean": "양면 시장",
   "aliases": [
    "양면시장",
    "투사이드 마켓",
    "양면 플랫폼",
    "Two-sided marketplace"
   ],
   "senses": [
    {
     "industries": [
      "platform"
     ],
     "roles": [
      "pm"
     ],
     "level": "심화",
     "importance": 3,
     "definition": "공급자(판매자·기사 등)와 수요자(구매자·승객 등)라는 두 고객 집단을 플랫폼이 연결하는 시장입니다. 한쪽이 늘수록 다른 쪽이 얻는 가치도 커지는 양면 네트워크 효과가 특징입니다.",
     "formula": null,
     "examples": [
      "양면 시장이라 판매자만 늘리면 안 되고 구매자 유입도 같이 봐야 해요.",
      "초기엔 공급 쪽을 먼저 채우는 게 양면 시장의 닭과 달걀 문제를 푸는 방법이에요."
     ],
     "sources": [
      {
       "title": "The Marketplace Glossary | a16z",
       "url": "https://a16z.com/the-marketplace-glossary/",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "오픈마켓",
     "note": "대표적인 양면 시장 형태입니다."
    },
    {
     "term": "테이크 레이트",
     "note": "양면 시장 플랫폼의 수익성을 보는 지표입니다."
    },
    {
     "term": "GMV",
     "note": "양면 시장의 거래 규모를 나타냅니다."
    }
   ],
   "confusable": [
    {
     "term": "단면 시장",
     "difference": "일반 유통은 한쪽 고객(구매자)에게 파는 구조이고, 양면 시장은 두 고객 집단을 모두 고객으로 둡니다."
    }
   ]
  },
  {
   "id": "take_rate",
   "term": "테이크 레이트",
   "original": "Take Rate",
   "korean": "플랫폼 수수료율",
   "aliases": [
    "테이크레이트",
    "레이크",
    "Rake",
    "수수료율",
    "TR"
   ],
   "senses": [
    {
     "industries": [
      "platform"
     ],
     "roles": [
      "pm",
      "data"
     ],
     "level": "심화",
     "importance": 3,
     "definition": "플랫폼을 거쳐 간 전체 거래액(GMV) 가운데 플랫폼이 수수료 등으로 가져가는 몫의 비율입니다. 시장 특성과 플랫폼이 제공하는 운영 가치에 따라 한 자릿수부터 수십 %까지 다양합니다.",
     "formula": "테이크 레이트(%) = 플랫폼이 가져간 금액 ÷ GMV × 100",
     "examples": [
      "광고 매출을 빼고 수수료만으로 테이크 레이트를 다시 계산해 보죠.",
      "테이크 레이트를 올리면 판매자 이탈이 생길 수 있어서 단계적으로 봐야 해요."
     ],
     "sources": [
      {
       "title": "The Marketplace Glossary | a16z",
       "url": "https://a16z.com/the-marketplace-glossary/",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "GMV",
     "note": "테이크 레이트의 분모가 되는 거래액입니다."
    },
    {
     "term": "매출",
     "note": "GMV × 테이크 레이트가 플랫폼 수수료 매출에 해당합니다."
    },
    {
     "term": "정산",
     "note": "판매자 정산 때 이 수수료를 뺍니다."
    }
   ],
   "confusable": [
    {
     "term": "GMV",
     "difference": "GMV는 플랫폼을 거쳐 간 전체 거래액이고, 테이크 레이트는 그중 플랫폼 몫의 비율입니다."
    }
   ]
  },
  {
   "id": "voc",
   "term": "VOC",
   "original": "Voice of the Customer",
   "korean": "고객의 소리",
   "aliases": [
    "브이오씨",
    "VoC",
    "고객 피드백",
    "고객의소리"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "cx",
      "pm",
      "marketing"
     ],
     "level": "입문",
     "importance": 5,
     "definition": "문의, 리뷰, 설문, 상담 기록 등으로 들어온 고객의 의견과 불만을 모아 분석하는 일, 또는 그렇게 모인 의견 자체를 말합니다. 제품과 서비스 개선의 근거로 씁니다.",
     "formula": null,
     "examples": [
      "이번 주 VOC 상위 3개가 전부 배송 지연이라 물류팀이랑 같이 봐야 할 것 같아요.",
      "앱 리뷰랑 상담 VOC를 묶어서 월간 리포트로 PM팀에 공유드릴게요."
     ],
     "sources": [
      {
       "title": "Voice of the Customer: How to collect and use this data",
       "url": "https://www.zendesk.kr/blog/analytics-and-data/customer-analytics/amplify-voice-of-customer/",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "CSAT",
     "note": "VOC 중 만족도를 숫자로 재는 대표 지표입니다."
    },
    {
     "term": "티켓 태그",
     "note": "VOC를 주제별로 분류·집계할 때 태그를 씁니다."
    }
   ],
   "confusable": [
    {
     "term": "NPS",
     "difference": "NPS는 추천 의향을 묻는 하나의 점수이고, VOC는 의견 전반을 모으는 활동입니다."
    }
   ]
  },
  {
   "id": "ticket",
   "term": "티켓",
   "original": "Support Ticket",
   "korean": "상담 티켓",
   "aliases": [
    "티켓",
    "문의 건",
    "지원 티켓",
    "케이스",
    "Ticket"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "cx"
     ],
     "level": "입문",
     "importance": 5,
     "definition": "고객 문의 한 건을 접수부터 해결까지 기록하고 추적하는 단위입니다. 고객 메시지, 고객 정보, 담당자, 상태 등이 함께 담깁니다.",
     "formula": null,
     "examples": [
      "어제 들어온 티켓 중 아직 미해결이 40건 남아 있어요.",
      "같은 고객 문의가 채팅이랑 메일로 두 번 들어와서 티켓 하나로 병합했습니다."
     ],
     "sources": [
      {
       "title": "Lesson 1: From support requests to tickets – Zendesk help",
       "url": "https://support.zendesk.com/hc/en-us/articles/4408881925786-Lesson-1-From-support-requests-to-tickets",
       "kind": "official",
       "checked_at": "2026-10-15"
      },
      {
       "title": "지원 티켓이란?",
       "url": "https://www.zendesk.kr/blog/customer-service/ticketing-system/ticketing-system/what-is-a-support-ticket/",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "티켓 태그",
     "note": "티켓을 분류하고 집계하는 라벨입니다."
    },
    {
     "term": "첫 응답 시간",
     "note": "티켓 단위로 측정하는 대표 응대 지표입니다."
    }
   ],
   "confusable": [
    {
     "term": "VOC",
     "difference": "티켓은 문의 한 건의 처리 단위이고, VOC는 여러 티켓 등에서 모은 고객 의견 전반입니다."
    }
   ]
  },
  {
   "id": "help_center",
   "term": "헬프센터",
   "original": "Help Center",
   "korean": "헬프센터",
   "aliases": [
    "헬프 센터",
    "고객센터 페이지",
    "FAQ",
    "지식 베이스",
    "Knowledge Base"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "cx"
     ],
     "level": "입문",
     "importance": 4,
     "definition": "고객이 상담원에게 묻지 않고도 스스로 답을 찾을 수 있도록 FAQ와 도움말 문서를 모아 둔 공개 페이지입니다. 그 안의 문서 묶음을 지식 베이스라고 부릅니다.",
     "formula": null,
     "examples": [
      "환불 문의가 많으니 헬프센터에 환불 절차 문서를 먼저 올리죠.",
      "챗봇이 헬프센터 아티클을 찾아서 답하도록 연결해 두었어요."
     ],
     "sources": [
      {
       "title": "Getting started with self-service - Introduction: Elements of a self-service channel",
       "url": "https://support.zendesk.com/hc/en-us/articles/4408885576346-Getting-started-with-self-service-Introduction-Elements-of-a-self-service-channel",
       "kind": "official",
       "checked_at": "2026-10-15"
      },
      {
       "title": "성공적인 헬프 센터 구축을 위한 6가지 팁",
       "url": "https://www.zendesk.kr/blog/help-center/knowledge-base/help-center-tips/",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "셀프서비스",
     "note": "헬프센터는 셀프서비스의 대표 채널입니다."
    },
    {
     "term": "챗봇",
     "note": "챗봇이 헬프센터 문서를 근거로 답하는 경우가 많습니다."
    }
   ],
   "confusable": [
    {
     "term": "매크로",
     "difference": "헬프센터는 고객이 보는 문서이고, 매크로는 상담원이 쓰는 답변 상용구입니다."
    }
   ]
  },
  {
   "id": "chatbot",
   "term": "챗봇",
   "original": "Chatbot",
   "korean": "챗봇",
   "aliases": [
    "채팅봇",
    "상담 봇",
    "AI 챗봇",
    "봇"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "cx"
     ],
     "level": "입문",
     "importance": 3,
     "definition": "사람처럼 대화하며 고객 질문에 자동으로 답하는 프로그램입니다. 웹사이트, 앱, 메신저에서 24시간 기본 문의를 처리하고 필요하면 상담원에게 넘깁니다.",
     "formula": null,
     "examples": [
      "배송 조회 문의는 챗봇이 먼저 받고, 해결 안 되면 상담원 연결로 넘기게 해 주세요.",
      "챗봇 도입 후 단순 문의 비중이 얼마나 줄었는지 확인해 볼게요."
     ],
     "sources": [
      {
       "title": "About AI agents – Zendesk help",
       "url": "https://support.zendesk.com/hc/en-us/articles/6970583409690-About-AI-agents",
       "kind": "official",
       "checked_at": "2026-10-15"
      },
      {
       "title": "The complete guide to customer service chatbots in 2026",
       "url": "https://www.zendesk.kr/service/ai/chatbots-customer-service/",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "셀프서비스",
     "note": "챗봇은 고객 스스로 해결하게 돕는 수단입니다."
    },
    {
     "term": "에스컬레이션",
     "note": "봇이 못 푸는 문의를 상담원에게 넘기는 흐름과 이어집니다."
    }
   ],
   "confusable": [
    {
     "term": "매크로",
     "difference": "챗봇은 고객과 직접 대화하는 자동 응답이고, 매크로는 상담원이 직접 골라 적용하는 템플릿입니다."
    }
   ]
  },
  {
   "id": "macro",
   "term": "매크로",
   "original": "Macro",
   "korean": "상담 상용구",
   "aliases": [
    "매크로 답변",
    "템플릿 답변",
    "상용구",
    "Canned Response"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "cx"
     ],
     "level": "입문",
     "importance": 3,
     "definition": "자주 쓰는 답변 문구와 티켓 처리 동작(태그 추가, 상태 변경 등)을 미리 저장해 두고 상담원이 클릭 한 번으로 적용하는 기능입니다.",
     "formula": null,
     "examples": [
      "교환 안내는 매크로로 만들어 두었으니 그대로 쓰시고 주문번호만 확인해 주세요.",
      "매크로 적용하면 '배송문의' 태그도 자동으로 붙어요."
     ],
     "sources": [
      {
       "title": "Creating macros for repetitive ticket responses and actions",
       "url": "https://support.zendesk.com/hc/en-us/articles/4408844187034-Creating-macros-for-repetitive-ticket-responses-and-actions",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "티켓 태그",
     "note": "매크로 적용 시 태그를 함께 붙여 분류를 자동화합니다."
    },
    {
     "term": "AHT",
     "note": "매크로는 처리 시간을 줄이는 데 쓰입니다."
    }
   ],
   "confusable": [
    {
     "term": "챗봇",
     "difference": "매크로는 상담원이 직접 적용하고, 챗봇은 고객에게 자동으로 응답합니다."
    }
   ]
  },
  {
   "id": "escalation",
   "term": "에스컬레이션",
   "original": "Escalation",
   "korean": "상위 이관",
   "aliases": [
    "에스컬",
    "이관",
    "상향 이관",
    "티켓 에스컬레이션"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "cx"
     ],
     "level": "입문",
     "importance": 4,
     "definition": "1차 상담에서 해결하기 어려운 문의를 더 경험 많은 상담원, 관리자, 전문 부서로 넘겨 처리하게 하는 절차입니다.",
     "formula": null,
     "examples": [
      "결제 오류 건은 1차에서 못 풀면 바로 개발팀으로 에스컬레이션해 주세요.",
      "VIP 고객 불만이라 팀장님께 에스컬 올렸습니다."
     ],
     "sources": [
      {
       "title": "Using intelligent triage to identify and act on ticket escalations – Zendesk help",
       "url": "https://support.zendesk.com/hc/en-us/articles/6353620565530-Using-intelligent-triage-to-identify-and-act-on-ticket-escalations",
       "kind": "official",
       "checked_at": "2026-10-15"
      },
      {
       "title": "Ticket escalation: What it is + 8 ways to manage it",
       "url": "https://www.zendesk.kr/blog/customer-service/ticketing-system/ticketing-system/art-ticket-escalation-process/",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "SLA",
     "note": "정해진 시간 안에 해결이 어려우면 에스컬레이션 기준이 됩니다."
    },
    {
     "term": "FCR",
     "note": "에스컬레이션이 잦으면 첫 접촉 해결률이 낮아집니다."
    }
   ],
   "confusable": [
    {
     "term": "장애",
     "difference": "에스컬레이션은 문의를 넘기는 절차이고, 장애는 서비스 자체가 멈추거나 나빠진 상황입니다."
    }
   ]
  },
  {
   "id": "frt",
   "term": "첫 응답 시간",
   "original": "First Reply Time",
   "korean": "첫 응답 시간",
   "aliases": [
    "FRT",
    "에프알티",
    "첫응답시간",
    "최초 응답 시간",
    "First Response Time"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "cx"
     ],
     "level": "입문",
     "importance": 4,
     "definition": "티켓이 생성된 때부터 상담원이 고객에게 처음 답장할 때까지 걸린 시간입니다. 자동 응답은 빼고 실제 사람이 답한 시점을 기준으로 봅니다.",
     "formula": "첫 응답 시간 = 상담원 첫 답장 시각 − 티켓 생성 시각",
     "examples": [
      "주말에 첫 응답 시간이 6시간까지 늘어서 당번 인력을 더 둬야 할 것 같아요.",
      "채팅 FRT 목표는 3분 이내로 잡겠습니다."
     ],
     "sources": [
      {
       "title": "Analyzing the metrics that matter to improve customer support",
       "url": "https://support.zendesk.com/hc/en-us/articles/4408832234394-Analyzing-the-metrics-that-matter-to-improve-customer-support",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "SLA",
     "note": "첫 응답 시간 목표를 SLA로 정해 관리합니다."
    },
    {
     "term": "CSAT",
     "note": "첫 응답이 빠를수록 만족도에 영향을 줍니다."
    }
   ],
   "confusable": [
    {
     "term": "해결 시간",
     "difference": "첫 응답 시간은 처음 답할 때까지, 해결 시간은 문제가 풀릴 때까지의 시간입니다."
    }
   ]
  },
  {
   "id": "csat",
   "term": "CSAT",
   "original": "Customer Satisfaction Score",
   "korean": "고객 만족도 점수",
   "aliases": [
    "씨샛",
    "고객만족도",
    "만족도 점수",
    "CSAT 점수"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "cx",
      "marketing"
     ],
     "level": "입문",
     "importance": 5,
     "definition": "상담이나 구매 직후 짧은 설문으로 고객이 얼마나 만족했는지 묻고, 만족했다고 답한 비율을 점수로 나타낸 지표입니다.",
     "formula": "CSAT(%) = 만족(좋음) 응답 수 ÷ 평가를 남긴 응답 수 × 100 (5점 척도라면 보통 4~5점을 만족으로 셉니다)",
     "examples": [
      "이번 달 상담 CSAT가 82%로 지난달보다 3%p 올랐어요.",
      "만족도 낮은 티켓만 모아서 원인 태그를 붙여 볼게요."
     ],
     "sources": [
      {
       "title": "Metrics and attributes for Zendesk messaging – Zendesk help",
       "url": "https://support.zendesk.com/hc/en-us/articles/4724624097818-Metrics-and-attributes-for-Zendesk-messaging",
       "kind": "official",
       "checked_at": "2026-10-15"
      },
      {
       "title": "Analyzing the metrics that matter to improve customer support – Zendesk help",
       "url": "https://support.zendesk.com/hc/en-us/articles/4408832234394-Analyzing-the-metrics-that-matter-to-improve-customer-support",
       "kind": "official",
       "checked_at": "2026-10-15"
      },
      {
       "title": "What is customer satisfaction score (CSAT) and how to measure It",
       "url": "https://www.zendesk.kr/blog/customer-experience/loyalty/customer-loyalty/customer-satisfaction-score/",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      },
      {
       "title": "5 methods for measuring customer satisfaction",
       "url": "https://www.zendesk.kr/blog/customer-service/satisfaction/measure-customer-satisfaction/",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "NPS",
     "note": "함께 보는 대표 고객 경험 지표입니다."
    },
    {
     "term": "CES",
     "note": "만족도 대신 고객이 들인 노력을 묻는 지표입니다."
    }
   ],
   "confusable": [
    {
     "term": "NPS",
     "difference": "CSAT는 특정 상호작용의 만족을, NPS는 회사 전체를 추천할 의향을 묻습니다."
    }
   ]
  },
  {
   "id": "omnichannel",
   "term": "옴니채널",
   "original": "Omnichannel",
   "korean": "옴니채널",
   "aliases": [
    "옴니 채널",
    "통합 채널",
    "Omni-channel"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "cx",
      "marketing"
     ],
     "level": "입문",
     "importance": 3,
     "definition": "채팅, 이메일, 전화, 메신저 등 여러 상담 채널을 하나로 연결해 고객이 채널을 바꿔도 이전 대화와 맥락이 이어지게 하는 운영 방식입니다.",
     "formula": null,
     "examples": [
      "옴니채널로 바꾸면 고객이 전화로 다시 걸어도 채팅 이력을 바로 볼 수 있어요.",
      "인스타 DM도 상담툴에 붙여서 옴니채널로 묶어 보죠."
     ],
     "sources": [
      {
       "title": "About the Zendesk Agent Workspace",
       "url": "https://support.zendesk.com/hc/en-us/articles/4408821259930-About-the-Zendesk-Agent-Workspace",
       "kind": "official",
       "checked_at": "2026-10-15"
      },
      {
       "title": "What is omnichannel customer service? Definition, importance & strategy",
       "url": "https://www.zendesk.kr/blog/customer-service/support/omnichannel-really-means/",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "티켓",
     "note": "채널이 달라도 한 고객의 문의를 하나의 기록으로 이어 봅니다."
    },
    {
     "term": "CES",
     "note": "고객이 같은 말을 반복하지 않아 노력이 줄어듭니다."
    }
   ],
   "confusable": [
    {
     "term": "멀티채널",
     "difference": "멀티채널은 채널이 여러 개일 뿐 서로 연결되지 않고, 옴니채널은 대화가 채널 간에 이어집니다."
    }
   ]
  },
  {
   "id": "nps",
   "term": "NPS",
   "original": "Net Promoter Score",
   "korean": "순추천지수",
   "aliases": [
    "엔피에스",
    "순추천 지수",
    "고객 추천 지수",
    "넷 프로모터 스코어"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "cx",
      "marketing",
      "pm"
     ],
     "level": "실무",
     "importance": 5,
     "definition": "'이 회사를 친구나 동료에게 추천할 가능성은?'을 0~10점으로 묻고, 9~10점(추천 고객) 비율에서 0~6점(비추천 고객) 비율을 뺀 점수입니다.",
     "formula": "NPS = 추천 고객(9~10점) 비율(%) − 비추천 고객(0~6점) 비율(%)",
     "examples": [
      "이번 분기 NPS가 +12에서 +20으로 올랐는데, 배송 개선 효과로 보고 있어요.",
      "비추천 응답의 주관식 이유를 VOC 태그로 분류해 주세요."
     ],
     "sources": [
      {
       "title": "Measuring Your Net Promoter Score",
       "url": "https://nps.bain.com/about/measuring-your-net-promoter-score/",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "CSAT",
     "note": "함께 보는 고객 경험 지표입니다."
    },
    {
     "term": "리텐션",
     "note": "NPS는 재구매·유지와의 관계를 볼 때 자주 씁니다."
    }
   ],
   "confusable": [
    {
     "term": "CSAT",
     "difference": "NPS는 전체 관계의 추천 의향, CSAT는 특정 경험의 만족을 잽니다."
    }
   ]
  },
  {
   "id": "ces",
   "term": "CES",
   "original": "Customer Effort Score",
   "korean": "고객 노력 점수",
   "aliases": [
    "씨이에스",
    "고객 노력 지수",
    "고객노력점수"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "cx"
     ],
     "level": "실무",
     "importance": 3,
     "definition": "문제를 해결하거나 원하는 일을 끝내기까지 고객이 얼마나 쉽게, 또는 힘들게 했는지를 설문으로 묻는 지표입니다. 점수가 좋을수록 고객의 수고가 적다는 뜻입니다.",
     "formula": "CES = 응답 점수 합계 ÷ 응답 수 (숫자 척도 기준)",
     "examples": [
      "반품 절차 CES가 낮게 나와서 신청 단계를 줄여 보려고 해요.",
      "상담 종료 후 '해결이 얼마나 쉬웠나요?' 질문으로 CES를 받아 봅시다."
     ],
     "sources": [
      {
       "title": "고객 노력 지수, 설명 (+5가지 개선 방법)",
       "url": "https://www.zendesk.kr/blog/customer-service/satisfaction/customer-effort-score/",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "CSAT",
     "note": "같이 받는 상담 후 설문 지표입니다."
    },
    {
     "term": "셀프서비스",
     "note": "셀프서비스 품질은 고객 노력에 직접 영향을 줍니다."
    }
   ],
   "confusable": [
    {
     "term": "CSAT",
     "difference": "CES는 얼마나 쉬웠는지, CSAT는 얼마나 만족했는지를 묻습니다."
    }
   ]
  },
  {
   "id": "fcr",
   "term": "FCR",
   "original": "First Contact Resolution",
   "korean": "첫 접촉 해결률",
   "aliases": [
    "에프씨알",
    "1차 해결률",
    "First Call Resolution",
    "원터치 해결률"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "cx"
     ],
     "level": "실무",
     "importance": 4,
     "definition": "고객 문의를 첫 번째 응대(전화 한 통, 채팅 한 번, 메일 답장 한 번)만으로 해결한 비율입니다.",
     "formula": "FCR(%) = 한 번의 응대로 해결된 티켓 수 ÷ 전체 접수 티켓 수 × 100",
     "examples": [
      "FCR이 낮은 문의 유형부터 매크로랑 가이드를 보강하죠.",
      "에스컬레이션이 늘면서 이번 달 FCR이 70% 아래로 떨어졌어요."
     ],
     "sources": [
      {
       "title": "Metric definitions in Connect Customer (Cases resolved on first contact)",
       "url": "https://docs.aws.amazon.com/connect/latest/adminguide/metrics-definitions.html",
       "kind": "official",
       "checked_at": "2026-10-15"
      },
      {
       "title": "Analyzing the metrics that matter to improve customer support – Zendesk help",
       "url": "https://support.zendesk.com/hc/en-us/articles/4408832234394-Analyzing-the-metrics-that-matter-to-improve-customer-support",
       "kind": "official",
       "checked_at": "2026-10-15"
      },
      {
       "title": "What is first contact resolution (FCR)? Benefits + best practices",
       "url": "https://www.zendesk.kr/blog/customer-experience/retention/first-contact-resolution-friend-foe-frenemy/",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "에스컬레이션",
     "note": "이관이 많아지면 FCR이 떨어집니다."
    },
    {
     "term": "CSAT",
     "note": "한 번에 해결될수록 만족도가 높아지는 경향이 있습니다."
    }
   ],
   "confusable": [
    {
     "term": "해결 시간",
     "difference": "FCR은 한 번에 해결했는지의 비율이고, 해결 시간은 걸린 시간입니다."
    }
   ]
  },
  {
   "id": "aht",
   "term": "AHT",
   "original": "Average Handle Time",
   "korean": "평균 처리 시간",
   "aliases": [
    "에이에이치티",
    "평균처리시간",
    "평균 상담 시간",
    "핸들 타임"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "cx"
     ],
     "level": "실무",
     "importance": 4,
     "definition": "상담 한 건에 상담원이 실제로 쓰는 평균 시간입니다. 통화(대화) 시간, 고객 대기 시간, 상담 후 후속 작업 시간을 더해 건수로 나눕니다.",
     "formula": "AHT = (대화 시간 + 대기 시간 + 후속 작업 시간) ÷ 처리 건수",
     "examples": [
      "신규 상담원 AHT가 평균보다 4분 길어서 매크로 교육을 다시 할게요.",
      "AHT만 줄이다 재문의가 늘면 안 되니 FCR도 같이 봐 주세요."
     ],
     "sources": [
      {
       "title": "Metric definitions in Connect Customer (Average handle time)",
       "url": "https://docs.aws.amazon.com/connect/latest/adminguide/metrics-definitions.html",
       "kind": "official",
       "checked_at": "2026-10-15"
      },
      {
       "title": "평균 처리 시간이란? 계산 방법 + 적합한 AHT의 정의",
       "url": "https://www.zendesk.kr/blog/customer-service/satisfaction/average-handle-time/",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "WFM",
     "note": "필요 인력을 계산할 때 AHT가 핵심 입력값입니다."
    },
    {
     "term": "FCR",
     "note": "처리 시간을 줄이다 해결률이 떨어지지 않는지 함께 봅니다."
    }
   ],
   "confusable": [
    {
     "term": "해결 시간",
     "difference": "AHT는 상담원이 실제로 일한 시간이고, 해결 시간은 고객 대기 기간까지 포함한 전체 기간입니다."
    }
   ]
  },
  {
   "id": "resolution_time",
   "term": "해결 시간",
   "original": "Resolution Time",
   "korean": "해결 시간",
   "aliases": [
    "처리 완료 시간",
    "Full Resolution Time",
    "해결시간",
    "리졸루션 타임"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "cx"
     ],
     "level": "실무",
     "importance": 3,
     "definition": "티켓이 생성된 때부터 문제가 해결 처리될 때까지 걸린 시간입니다. 재오픈된 티켓은 첫 해결까지(첫 해결 시간)와 최종 해결까지(전체 해결 시간)를 나눠 봅니다.",
     "formula": "해결 시간 = 해결 처리 시각 − 티켓 생성 시각",
     "examples": [
      "환불 문의 해결 시간 중앙값이 2일이라 정산팀 확인 단계가 병목 같아요.",
      "재오픈이 많아서 첫 해결 시간보다 전체 해결 시간을 기준으로 보죠."
     ],
     "sources": [
      {
       "title": "Analyzing the metrics that matter to improve customer support",
       "url": "https://support.zendesk.com/hc/en-us/articles/4408832234394-Analyzing-the-metrics-that-matter-to-improve-customer-support",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "첫 응답 시간",
     "note": "응대 속도를 함께 보는 짝 지표입니다."
    },
    {
     "term": "SLA",
     "note": "해결 시간 목표를 SLA로 정하기도 합니다."
    }
   ],
   "confusable": [
    {
     "term": "AHT",
     "difference": "해결 시간은 생성부터 해결까지의 전체 기간이고, AHT는 상담원이 직접 일한 시간입니다."
    }
   ]
  },
  {
   "id": "self_service",
   "term": "셀프서비스",
   "original": "Self-service",
   "korean": "셀프서비스",
   "aliases": [
    "셀프 서비스",
    "자가 해결",
    "고객 셀프서비스",
    "Self Service"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "cx"
     ],
     "level": "실무",
     "importance": 3,
     "definition": "고객이 상담원에게 연락하지 않고 헬프센터 문서, FAQ, 챗봇 등을 통해 스스로 답을 찾고 문제를 해결하게 하는 방식입니다.",
     "formula": null,
     "examples": [
      "배송지 변경은 셀프서비스로 돌리면 문의가 꽤 줄 것 같아요.",
      "셀프서비스 문서 조회 후 문의 전환이 얼마나 되는지 봐 주세요."
     ],
     "sources": [
      {
       "title": "Getting started with self-service - Introduction: Elements of a self-service channel",
       "url": "https://support.zendesk.com/hc/en-us/articles/4408885576346-Getting-started-with-self-service-Introduction-Elements-of-a-self-service-channel",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "헬프센터",
     "note": "셀프서비스 콘텐츠를 올리는 대표 공간입니다."
    },
    {
     "term": "챗봇",
     "note": "대화형 셀프서비스 수단입니다."
    }
   ],
   "confusable": [
    {
     "term": "챗봇",
     "difference": "셀프서비스는 고객 스스로 해결하게 하는 전략 전체이고, 챗봇은 그 수단 중 하나입니다."
    }
   ]
  },
  {
   "id": "sla",
   "term": "SLA",
   "original": "Service Level Agreement",
   "korean": "서비스 수준 협약",
   "aliases": [
    "에스엘에이",
    "서비스 수준 목표",
    "서비스수준협약",
    "응답 목표 시간"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "cx"
     ],
     "level": "실무",
     "importance": 4,
     "definition": "상담팀이 고객 문의에 얼마나 빨리 응답하고 해결할지 정한 목표 시간 기준입니다. 보통 티켓 우선순위별로 첫 응답·해결 목표를 다르게 정해 위반 여부를 추적합니다.",
     "formula": null,
     "examples": [
      "긴급 티켓 SLA가 1시간인데 3건이 넘어가서 원인 확인 중이에요.",
      "SLA 임박 티켓을 뷰 상단에 올려서 먼저 처리해 주세요."
     ],
     "sources": [
      {
       "title": "About SLA policies and how they work",
       "url": "https://support.zendesk.com/hc/en-us/articles/5600997516058-About-SLA-policies-and-how-they-work",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    },
    {
     "industries": [
      "platform"
     ],
     "roles": [
      "pm",
      "cx"
     ],
     "level": "실무",
     "importance": 4,
     "definition": "서비스 제공자가 사용자와 맺는 약속으로, 가용성 같은 서비스 수준 목표와 이를 지키지 못했을 때의 결과(환불, 크레딧 등)를 담은 협약입니다.",
     "formula": null,
     "examples": [
      "엔터프라이즈 고객 계약에 가용성 99.9% SLA가 들어가 있어서 이번 장애는 크레딧 보상 대상이에요.",
      "SLA 위반 여부를 판단하려면 장애 시간을 분 단위로 정리해 주세요."
     ],
     "sources": [
      {
       "title": "Service Level Objectives (Google SRE Book, Chapter 4)",
       "url": "https://sre.google/sre-book/service-level-objectives/",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "첫 응답 시간",
     "note": "상담 SLA의 대표 측정 항목입니다."
    },
    {
     "term": "가용성",
     "note": "플랫폼 SLA에서 약속하는 대표 수준입니다."
    }
   ],
   "confusable": [
    {
     "term": "SLO",
     "difference": "SLO는 내부 목표치이고, SLA는 미달 시 결과까지 정한 대외 약속입니다."
    }
   ]
  },
  {
   "id": "ticket_tag",
   "term": "티켓 태그",
   "original": "Ticket Tag",
   "korean": "티켓 태그",
   "aliases": [
    "태그",
    "상담 태그",
    "문의 유형 태그",
    "티켓태그"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "cx",
      "data"
     ],
     "level": "실무",
     "importance": 3,
     "definition": "티켓에 붙이는 짧은 키워드 라벨입니다. 문의 유형을 분류하고, 자동화 규칙과 검색, 통계 집계에 활용합니다.",
     "formula": null,
     "examples": [
      "이번 주 '배송지연' 태그 티켓이 두 배로 늘었어요.",
      "태그 이름 규칙이 제각각이라 refund_request로 통일하겠습니다."
     ],
     "sources": [
      {
       "title": "Working with ticket tags",
       "url": "https://support.zendesk.com/hc/en-us/articles/4408835059482-Working-with-ticket-tags",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "VOC",
     "note": "태그로 분류한 티켓을 모아 VOC 분석을 합니다."
    },
    {
     "term": "매크로",
     "note": "매크로 적용 시 태그가 자동으로 붙게 할 수 있습니다."
    }
   ],
   "confusable": [
    {
     "term": "카테고리 필드",
     "difference": "필드는 정해진 선택지 값이고, 태그는 자유롭게 여러 개 붙일 수 있는 라벨입니다."
    }
   ]
  },
  {
   "id": "returns",
   "term": "반품",
   "original": "Return",
   "korean": "반품",
   "aliases": [
    "반품 처리",
    "청약철회",
    "환불 반품",
    "리턴"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce"
     ],
     "roles": [
      "cx"
     ],
     "level": "입문",
     "importance": 4,
     "definition": "고객이 받은 상품을 판매자에게 돌려보내고 구매를 취소하는 것입니다. 온라인 구매는 법에 따라 원칙적으로 계약 서면을 받은 날(상품 공급이 늦으면 받은 날)부터 7일 안에 청약철회를 할 수 있으며, 이 내용은 학습용 일반 설명입니다.",
     "formula": null,
     "examples": [
      "단순 변심 반품은 왕복 배송비 안내 매크로로 답변해 주세요.",
      "상품이 광고와 다른 경우라 반품 배송비는 판매자 부담으로 처리했어요."
     ],
     "sources": [
      {
       "title": "인터넷 쇼핑 > 반품 및 환불하기 > 반품·환불 > 반품 및 환불 | 찾기쉬운 생활법령정보",
       "url": "https://www.easylaw.go.kr/CSP/CnpClsMain.laf?csmSeq=835&ccfNo=4&cciNo=1&cnpClsNo=2",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "반품률",
     "note": "반품이 얼마나 자주 일어나는지 보는 지표입니다."
    },
    {
     "term": "풀필먼트",
     "note": "반품 입고·검수까지 물류사가 대행하기도 합니다."
    }
   ],
   "confusable": [
    {
     "term": "교환",
     "difference": "반품은 구매를 취소하고 돌려받는 것이고, 교환은 다른 상품으로 바꿔 받는 것입니다."
    }
   ]
  },
  {
   "id": "stockout",
   "term": "품절",
   "original": "Stockout",
   "korean": "품절",
   "aliases": [
    "재고 소진",
    "아웃오브스톡",
    "Out of Stock",
    "결품",
    "솔드아웃"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce"
     ],
     "roles": [
      "cx"
     ],
     "level": "입문",
     "importance": 3,
     "definition": "고객이 사려는 시점에 해당 상품의 재고가 없어 판매할 수 없는 상태입니다.",
     "formula": null,
     "examples": [
      "품절 상품 재입고 알림 문의가 많아서 안내 매크로를 만들었어요.",
      "주문 후 품절 취소가 생기면 바로 고객에게 사과 메시지 보내 주세요."
     ],
     "sources": [
      {
       "title": "Selling out of stock products · Shopify Help Center",
       "url": "https://help.shopify.com/en/manual/products/inventory/setup/selling-when-out-of-stock",
       "kind": "official",
       "checked_at": "2026-10-15"
      },
      {
       "title": "out of stock, stockouts: Causes and Prevention",
       "url": "https://www.shopify.com/blog/what-causes-a-stockout",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "리드타임",
     "note": "발주 리드타임이 길면 품절 위험이 커집니다."
    },
    {
     "term": "재고 회전율",
     "note": "재고를 적게 들고 빠르게 돌릴수록 품절 관리가 중요해집니다."
    }
   ],
   "confusable": [
    {
     "term": "일시품절",
     "difference": "품절은 지금 재고가 없는 상태 전반이고, 일시품절은 재입고 예정이 있는 경우를 따로 부르는 말입니다."
    }
   ]
  },
  {
   "id": "fulfillment",
   "term": "풀필먼트",
   "original": "Fulfillment",
   "korean": "주문 이행 대행",
   "aliases": [
    "풀필먼트 서비스",
    "주문처리",
    "풀필",
    "Order Fulfillment"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce"
     ],
     "roles": [
      "cx",
      "pm"
     ],
     "level": "실무",
     "importance": 4,
     "definition": "주문이 들어온 뒤 상품을 보관·선별·포장해 배송하고, 교환·반품까지 처리하는 주문 이행 전 과정입니다. 이 과정을 물류 전문업체가 판매자 대신 맡는 서비스를 가리키기도 합니다.",
     "formula": null,
     "examples": [
      "풀필먼트 센터 입고가 늦어져서 이번 주 출고가 하루씩 밀려요.",
      "반품 검수도 풀필먼트사에서 하니까 처리 현황은 그쪽 시스템에서 확인해 주세요."
     ],
     "sources": [
      {
       "title": "Fulfilling orders · Shopify Help Center",
       "url": "https://help.shopify.com/en/manual/fulfillment/setup/fulfillment-options",
       "kind": "official",
       "checked_at": "2026-10-15"
      },
      {
       "title": "What Is Fulfillment? Definition, Meaning, and Guide",
       "url": "https://www.shopify.com/blog/what-is-fulfillment",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      },
      {
       "title": "풀필먼트(Fulfillment) 정의와 유형 총정리 | 첼로스퀘어",
       "url": "https://www.cello-square.com/kr-ko/blog/view-111.do",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "3PL",
     "note": "풀필먼트를 외부 물류사에 맡기는 방식과 겹칩니다."
    },
    {
     "term": "라스트마일",
     "note": "풀필먼트의 마지막 배송 구간입니다."
    }
   ],
   "confusable": [
    {
     "term": "3PL",
     "difference": "3PL은 물류 업무를 외부에 맡기는 방식 전반이고, 풀필먼트는 주문 처리 전 과정을 일괄 대행하는 쪽에 초점이 있습니다."
    }
   ]
  },
  {
   "id": "3pl",
   "term": "3PL",
   "original": "Third-Party Logistics",
   "korean": "제3자 물류",
   "aliases": [
    "쓰리피엘",
    "삼자물류",
    "물류 대행",
    "3자 물류"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce"
     ],
     "roles": [
      "cx"
     ],
     "level": "실무",
     "importance": 3,
     "definition": "창고 보관, 재고 관리, 포장, 배송 같은 물류 업무를 외부 전문 물류업체에 맡기는 방식, 또는 그 업체를 말합니다.",
     "formula": null,
     "examples": [
      "3PL 쪽 출고 마감이 오후 2시라 그 이후 주문은 다음 날 출발이에요.",
      "배송 누락 건은 3PL에 확인 요청 넣고 결과 공유드릴게요."
     ],
     "sources": [
      {
       "title": "Fulfillment Network · Shopify Help Center",
       "url": "https://help.shopify.com/en/manual/fulfillment/shopify-fulfillment-network",
       "kind": "official",
       "checked_at": "2026-10-15"
      },
      {
       "title": "풀필먼트(Fulfillment) 정의와 유형 총정리 | 첼로스퀘어",
       "url": "https://www.cello-square.com/kr-ko/blog/view-111.do",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      },
      {
       "title": "3PL in Ecommerce: How to Choose the Right Partner (2026)",
       "url": "https://www.shopify.com/blog/3pl-ecommerce",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "풀필먼트",
     "note": "3PL이 제공하는 대표 서비스 형태입니다."
    },
    {
     "term": "리드타임",
     "note": "3PL의 처리 속도가 배송 리드타임에 영향을 줍니다."
    }
   ],
   "confusable": [
    {
     "term": "풀필먼트",
     "difference": "3PL은 물류 위탁이라는 방식이고, 풀필먼트는 주문부터 배송·반품까지 일괄 처리하는 서비스입니다."
    }
   ]
  },
  {
   "id": "last_mile",
   "term": "라스트마일",
   "original": "Last Mile Delivery",
   "korean": "최종 배송 구간",
   "aliases": [
    "라스트 마일",
    "라스트마일 배송",
    "막배송",
    "Last Mile"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce"
     ],
     "roles": [
      "cx"
     ],
     "level": "실무",
     "importance": 3,
     "definition": "물류센터나 지역 거점, 매장에서 고객 문 앞까지 상품을 전달하는 배송의 마지막 구간입니다.",
     "formula": null,
     "examples": [
      "배송 지연 VOC 대부분이 라스트마일 구간에서 생기고 있어요.",
      "새벽배송 지역은 라스트마일 업체가 달라서 조회 링크도 다르게 안내해야 해요."
     ],
     "sources": [
      {
       "title": "Last Mile Delivery Management Solution: 2026 Guide",
       "url": "https://www.shopify.com/enterprise/blog/last-mile-delivery-management-solution",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "풀필먼트",
     "note": "풀필먼트의 마지막 단계가 라스트마일 배송입니다."
    },
    {
     "term": "리드타임",
     "note": "라스트마일 속도가 고객이 체감하는 리드타임을 좌우합니다."
    }
   ],
   "confusable": [
    {
     "term": "3PL",
     "difference": "3PL은 물류 업무 전반의 위탁이고, 라스트마일은 그중 고객에게 전달하는 마지막 구간만 가리킵니다."
    }
   ]
  },
  {
   "id": "lead_time",
   "term": "리드타임",
   "original": "Lead Time",
   "korean": "소요 기간",
   "aliases": [
    "리드 타임",
    "LT",
    "배송 리드타임",
    "발주 리드타임"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce"
     ],
     "roles": [
      "cx",
      "pm"
     ],
     "level": "실무",
     "importance": 3,
     "definition": "주문(요청)이 들어온 때부터 상품이 도착할 때까지 걸리는 기간입니다. 고객 주문의 배송 기간이나 공급업체 발주 기간을 말할 때 씁니다.",
     "formula": "리드타임(일) = 받은 날짜 − 주문(요청) 날짜",
     "examples": [
      "해외 직배송 상품은 리드타임이 7~10일이라 상세페이지에 꼭 표시해 주세요.",
      "공급사 리드타임이 길어져서 재입고 일정 문의 답변을 업데이트했어요."
     ],
     "sources": [
      {
       "title": "Purchase Order Lead Time: What It Is and How to Reduce It",
       "url": "https://www.shopify.com/blog/order-lead-time",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "품절",
     "note": "발주 리드타임을 고려해 재주문하지 않으면 품절이 납니다."
    },
    {
     "term": "라스트마일",
     "note": "배송 리드타임의 마지막 구간입니다."
    }
   ],
   "confusable": [
    {
     "term": "해결 시간",
     "difference": "리드타임은 상품이 도착하기까지의 기간이고, 해결 시간은 상담 티켓이 풀리기까지의 시간입니다."
    }
   ]
  },
  {
   "id": "return_rate",
   "term": "반품률",
   "original": "Return Rate",
   "korean": "반품률",
   "aliases": [
    "반품 비율",
    "리턴율",
    "반품율"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce"
     ],
     "roles": [
      "cx",
      "data"
     ],
     "level": "실무",
     "importance": 3,
     "definition": "판매한 상품 수 가운데 고객이 반품한 상품 수의 비율입니다. 상품별·채널별로 나눠 보면 문제 상품을 찾기 좋습니다.",
     "formula": "반품률(%) = 반품된 수량 ÷ 주문(판매) 수량 × 100",
     "examples": [
      "이 상품 반품률이 20%가 넘어서 사이즈 안내 문구를 바꿔 보려고요.",
      "반품 사유 태그를 붙여서 반품률이 높은 원인을 같이 봐 주세요."
     ],
     "sources": [
      {
       "title": "Sales reports · Shopify Help Center (Returned quantity rate)",
       "url": "https://help.shopify.com/en/manual/reports-and-analytics/shopify-reports/report-types/default-reports/sales-report",
       "kind": "official",
       "checked_at": "2026-10-15"
      },
      {
       "title": "25 Key Ecommerce Metrics to Track in 2026",
       "url": "https://www.shopify.com/blog/basic-ecommerce-metrics",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "반품",
     "note": "반품률의 집계 대상이 되는 처리입니다."
    },
    {
     "term": "전환율",
     "note": "상세 정보가 부족하면 전환은 오르고 반품이 늘 수 있어 함께 봅니다."
    }
   ],
   "confusable": [
    {
     "term": "환불률",
     "difference": "반품률은 수량 기준 반품 비율이고, 환불률은 금액이나 주문 기준 환불 비율로 따로 볼 수 있습니다."
    }
   ]
  },
  {
   "id": "inventory_turnover",
   "term": "재고 회전율",
   "original": "Inventory Turnover Ratio",
   "korean": "재고 회전율",
   "aliases": [
    "재고회전율",
    "재고 회전",
    "ITR",
    "Stock Turnover"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce"
     ],
     "roles": [
      "cx",
      "data"
     ],
     "level": "심화",
     "importance": 3,
     "definition": "일정 기간 동안 재고가 몇 번 팔리고 다시 채워졌는지를 나타내는 지표입니다. 높을수록 재고가 빨리 팔린다는 뜻입니다.",
     "formula": "재고 회전율 = 매출원가 ÷ 평균 재고, 평균 재고 = (기초 재고 + 기말 재고) ÷ 2",
     "examples": [
      "이 카테고리는 재고 회전율이 낮아서 기획전으로 소진해 보죠.",
      "회전율 높은 상품은 품절 나기 쉬우니 재입고 알림을 먼저 걸어 둘게요."
     ],
     "sources": [
      {
       "title": "Inventory Turnover Ratio: Formula and How to Improve",
       "url": "https://www.shopify.com/blog/inventory-turnover-ratio",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "품절",
     "note": "회전율이 높은 상품은 품절 관리가 중요합니다."
    },
    {
     "term": "리드타임",
     "note": "발주 리드타임과 함께 적정 재고를 정합니다."
    }
   ],
   "confusable": [
    {
     "term": "재고 일수",
     "difference": "재고 회전율은 기간 중 회전 횟수이고, 재고 일수는 재고를 다 파는 데 걸리는 일수입니다."
    }
   ]
  },
  {
   "id": "incident",
   "term": "장애",
   "original": "Incident",
   "korean": "장애",
   "aliases": [
    "인시던트",
    "서비스 장애",
    "장애 상황",
    "이슈"
   ],
   "senses": [
    {
     "industries": [
      "platform"
     ],
     "roles": [
      "cx",
      "pm"
     ],
     "level": "입문",
     "importance": 4,
     "definition": "서비스가 예기치 않게 멈추거나 품질이 떨어진 상황, 또는 그럴 위험이 생긴 사건입니다. 영향이 크고 긴급 대응이 필요하면 주요 장애로 따로 관리합니다.",
     "formula": null,
     "examples": [
      "결제 장애 공지 나갔으니 관련 문의는 장애 안내 매크로로 답해 주세요.",
      "장애 복구 시각 확정되면 상태 페이지랑 고객 공지 같이 업데이트할게요."
     ],
     "sources": [
      {
       "title": "What are incidents? | Jira Service Management Cloud",
       "url": "https://support.atlassian.com/jira-service-management-cloud/docs/what-are-incidents/",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "상태 페이지",
     "note": "장애 상황을 고객에게 알리는 창구입니다."
    },
    {
     "term": "포스트모템",
     "note": "장애 후 원인과 재발 방지를 정리하는 문서입니다."
    }
   ],
   "confusable": [
    {
     "term": "버그",
     "difference": "버그는 코드 결함이고, 장애는 서비스 이용에 실제로 지장이 생긴 상황입니다."
    }
   ]
  },
  {
   "id": "availability",
   "term": "가용성",
   "original": "Availability",
   "korean": "가용성",
   "aliases": [
    "업타임",
    "Uptime",
    "서비스 가용률",
    "가용률"
   ],
   "senses": [
    {
     "industries": [
      "platform"
     ],
     "roles": [
      "cx",
      "pm",
      "data"
     ],
     "level": "실무",
     "importance": 4,
     "definition": "서비스를 정상적으로 쓸 수 있었던 시간의 비율입니다. 요청 단위로 보면 전체 요청 중 성공한 요청의 비율로 잽니다.",
     "formula": "가용성(%) = 정상 이용 가능 시간 ÷ 전체 시간 × 100 (요청 기준: 성공 요청 수 ÷ 전체 요청 수 × 100)",
     "examples": [
      "지난달 가용성이 99.95%라 SLA 99.9%는 지켰어요.",
      "가용성 계산할 때 예정된 점검 시간은 빼는지 계약서 기준 확인해 주세요."
     ],
     "sources": [
      {
       "title": "Service Level Objectives (Google SRE Book, Chapter 4)",
       "url": "https://sre.google/sre-book/service-level-objectives/",
       "kind": "official",
       "checked_at": "2026-10-15"
      },
      {
       "title": "Embracing Risk (Google SRE Book, Chapter 3)",
       "url": "https://sre.google/sre-book/embracing-risk/",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "SLA",
     "note": "가용성 목표를 대외적으로 약속한 것이 SLA입니다."
    },
    {
     "term": "장애",
     "note": "장애 시간이 가용성을 떨어뜨립니다."
    }
   ],
   "confusable": [
    {
     "term": "응답 속도",
     "difference": "가용성은 쓸 수 있느냐의 비율이고, 응답 속도는 얼마나 빨리 반응하느냐입니다."
    }
   ]
  },
  {
   "id": "status_page",
   "term": "상태 페이지",
   "original": "Status Page",
   "korean": "서비스 상태 페이지",
   "aliases": [
    "스테이터스 페이지",
    "상태페이지",
    "Statuspage",
    "서비스 현황 페이지"
   ],
   "senses": [
    {
     "industries": [
      "platform"
     ],
     "roles": [
      "cx"
     ],
     "level": "실무",
     "importance": 3,
     "definition": "서비스 장애나 예정된 점검 상황을 사용자에게 실시간으로 알리는 공개 페이지입니다. 구독자에게 메일·문자 알림을 보내기도 합니다.",
     "formula": null,
     "examples": [
      "문의 폭주 전에 상태 페이지에 '결제 지연 확인 중'부터 올려 주세요.",
      "고객 답변에 상태 페이지 링크를 같이 넣으면 재문의가 줄어요."
     ],
     "sources": [
      {
       "title": "What is Statuspage?",
       "url": "https://support.atlassian.com/statuspage/docs/what-is-statuspage/",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "장애",
     "note": "상태 페이지는 장애 커뮤니케이션 도구입니다."
    },
    {
     "term": "가용성",
     "note": "구성 요소별 정상 여부를 보여 줍니다."
    }
   ],
   "confusable": [
    {
     "term": "공지사항",
     "difference": "공지사항은 일반 안내 게시판이고, 상태 페이지는 장애·점검 상태를 실시간으로 보여 주는 전용 페이지입니다."
    }
   ]
  },
  {
   "id": "moderation",
   "term": "콘텐츠 모더레이션",
   "original": "Content Moderation",
   "korean": "콘텐츠 검수",
   "aliases": [
    "모더레이션",
    "콘텐츠 관리",
    "게시물 검수",
    "콘텐츠모더레이션"
   ],
   "senses": [
    {
     "industries": [
      "platform"
     ],
     "roles": [
      "cx"
     ],
     "level": "실무",
     "importance": 3,
     "definition": "사용자가 올린 글, 이미지, 영상 등이 플랫폼 운영 정책(커뮤니티 가이드)에 맞는지 검토하고 위반 시 삭제·노출 제한 등의 조치를 하는 일입니다. 사람과 자동화 도구가 함께 수행합니다.",
     "formula": null,
     "examples": [
      "신고 들어온 리뷰는 모더레이션 큐에서 24시간 안에 판단해 주세요.",
      "자동 필터가 놓친 욕설 패턴을 모더레이션 기준에 추가했어요."
     ],
     "sources": [
      {
       "title": "What Is Content Moderation? - Trust & Safety Professional Association",
       "url": "https://www.tspa.org/curriculum/ts-fundamentals/content-moderation-and-operations/what-is-content-moderation/",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "어뷰징",
     "note": "모더레이션은 어뷰징 콘텐츠를 걸러내는 주요 수단입니다."
    },
    {
     "term": "VOC",
     "note": "신고·이의 제기도 고객 의견으로 함께 봅니다."
    }
   ],
   "confusable": [
    {
     "term": "어뷰징 대응",
     "difference": "모더레이션은 콘텐츠를 정책 기준으로 검토하는 일이고, 어뷰징 대응은 계정·행동의 부정 이용을 막는 일입니다."
    }
   ]
  },
  {
   "id": "abuse",
   "term": "어뷰징",
   "original": "Abuse",
   "korean": "부정 이용",
   "aliases": [
    "어뷰즈",
    "악용",
    "프로모션 어뷰징",
    "다계정 어뷰징"
   ],
   "senses": [
    {
     "industries": [
      "platform"
     ],
     "roles": [
      "cx",
      "data"
     ],
     "level": "실무",
     "importance": 3,
     "definition": "여러 계정 만들기, 자기 추천, 쿠폰 반복 사용처럼 플랫폼의 규칙을 악용해 원래 받을 수 없는 이득을 챙기는 행위입니다.",
     "formula": null,
     "examples": [
      "신규 가입 쿠폰을 같은 기기에서 반복 사용한 계정이 많아서 어뷰징 의심 목록 넘겨드려요.",
      "어뷰징으로 판단된 주문은 취소 안내 매크로로 답해 주세요."
     ],
     "sources": [
      {
       "title": "Account and promotion abuse: How to detect and prevent it",
       "url": "https://stripe.com/resources/more/account-and-promotion-abuse",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "콘텐츠 모더레이션",
     "note": "플랫폼 신뢰·안전을 지키는 짝 업무입니다."
    },
    {
     "term": "CAC",
     "note": "프로모션 어뷰징은 고객 획득 비용을 부풀립니다."
    }
   ],
   "confusable": [
    {
     "term": "사기(Fraud)",
     "difference": "어뷰징은 규칙의 허점을 악용하는 행위이고, 사기는 도용·위조 등으로 직접 속여 피해를 주는 행위로 더 무겁게 다룹니다."
    }
   ]
  },
  {
   "id": "postmortem",
   "term": "포스트모템",
   "original": "Postmortem",
   "korean": "사후 분석",
   "aliases": [
    "포스트 모템",
    "장애 회고",
    "사후 검토",
    "인시던트 리뷰",
    "Post-mortem"
   ],
   "senses": [
    {
     "industries": [
      "platform"
     ],
     "roles": [
      "cx",
      "pm"
     ],
     "level": "심화",
     "importance": 3,
     "definition": "장애가 끝난 뒤 무슨 일이 있었는지, 영향과 대응 과정, 근본 원인, 재발 방지 조치를 정리한 기록입니다. 개인을 탓하지 않는(blameless) 방식으로 쓰는 것이 원칙입니다.",
     "formula": null,
     "examples": [
      "어제 결제 장애 포스트모템에 CS 문의량 추이도 넣어 주세요.",
      "포스트모템 액션 아이템 중 고객 공지 지연 건은 CX팀이 맡을게요."
     ],
     "sources": [
      {
       "title": "Postmortem Culture: Learning from Failure (Google SRE Book, Chapter 15)",
       "url": "https://sre.google/sre-book/postmortem-culture/",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "근본 원인 분석",
     "note": "포스트모템의 핵심 단계입니다."
    },
    {
     "term": "장애",
     "note": "포스트모템의 대상이 되는 사건입니다."
    }
   ],
   "confusable": [
    {
     "term": "회고",
     "difference": "회고는 프로젝트·스프린트 전반을 돌아보는 것이고, 포스트모템은 특정 장애를 분석한 기록입니다."
    }
   ]
  },
  {
   "id": "rca",
   "term": "근본 원인 분석",
   "original": "Root Cause Analysis",
   "korean": "근본 원인 분석",
   "aliases": [
    "RCA",
    "알씨에이",
    "원인 분석",
    "근본원인분석",
    "5 Whys"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "cx",
      "pm"
     ],
     "level": "심화",
     "importance": 3,
     "definition": "겉으로 드러난 증상이 아니라 문제를 일으킨 밑바닥 원인을 찾아 고치는 분석입니다. '왜?'를 여러 번 묻는 5 Whys가 대표 기법이며, 장애 포스트모템에서도 핵심 단계로 씁니다.",
     "formula": null,
     "examples": [
      "배송 누락 VOC가 반복되니 RCA 해서 출고 프로세스부터 보죠.",
      "RCA 결과 원인이 상품 옵션 매핑 오류로 나와서 개발팀에 수정 요청했어요."
     ],
     "sources": [
      {
       "title": "5 Whys Analysis",
       "url": "https://www.atlassian.com/team-playbook/plays/5-whys",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      },
      {
       "title": "Postmortem Culture: Learning from Failure (Google SRE Book, Chapter 15)",
       "url": "https://sre.google/sre-book/postmortem-culture/",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "포스트모템",
     "note": "포스트모템 안에서 근본 원인을 정리합니다."
    },
    {
     "term": "VOC",
     "note": "반복 VOC의 원인을 찾을 때 RCA를 합니다."
    }
   ],
   "confusable": [
    {
     "term": "직접 원인",
     "difference": "직접 원인은 문제를 바로 촉발한 요인이고, 근본 원인은 고치면 같은 유형의 문제가 다시 생기지 않는 깊은 원인입니다."
    }
   ]
  },
  {
   "id": "wfm",
   "term": "WFM",
   "original": "Workforce Management",
   "korean": "인력 운영 관리",
   "aliases": [
    "더블유에프엠",
    "인력 관리",
    "상담 인력 운영",
    "상담량 예측"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce",
      "platform"
     ],
     "roles": [
      "cx"
     ],
     "level": "심화",
     "importance": 3,
     "definition": "과거 문의량과 처리 시간 등을 바탕으로 앞으로의 상담량을 예측하고, 필요한 상담원 수를 계산해 근무 일정을 짜고 관리하는 일입니다.",
     "formula": null,
     "examples": [
      "블프 시즌 상담량 예측이 나와서 WFM 기준으로 추가 인력 12명 요청드려요.",
      "점심 시간대 응답 지연이 커서 WFM에서 휴게 시간을 분산했어요."
     ],
     "sources": [
      {
       "title": "Forecasting & agent scheduling in Connect Customer",
       "url": "https://docs.aws.amazon.com/connect/latest/adminguide/forecasting-capacity-planning-scheduling.html",
       "kind": "official",
       "checked_at": "2026-10-15"
      },
      {
       "title": "Workforce Management in Call Centers: WFM Explained",
       "url": "https://www.nice.com/glossary/what-is-contact-center-workforce-management-wfm",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "AHT",
     "note": "필요 인원 계산의 핵심 입력값입니다."
    },
    {
     "term": "SLA",
     "note": "목표 응답 시간을 지키도록 인력을 배치합니다."
    }
   ],
   "confusable": [
    {
     "term": "WFO",
     "difference": "WFM은 예측·스케줄링 중심이고, WFO는 품질 관리·성과 관리까지 포함한 더 넓은 개념입니다."
    }
   ]
  },
  {
   "id": "health_score",
   "term": "고객 건강 점수",
   "original": "Customer Health Score",
   "korean": "고객 건강 점수",
   "aliases": [
    "헬스 스코어",
    "고객 헬스스코어",
    "Health Score",
    "고객 건강도"
   ],
   "senses": [
    {
     "industries": [
      "platform"
     ],
     "roles": [
      "cx"
     ],
     "level": "심화",
     "importance": 3,
     "definition": "제품 사용량, 문의 이력, 설문 결과 등 여러 신호를 묶어 고객사가 계약을 유지·확대할지, 떠날지를 가늠하는 예측 점수입니다. 회사마다 반영 항목과 가중치가 다릅니다.",
     "formula": null,
     "examples": [
      "헬스 스코어가 빨간불로 바뀐 고객사는 이번 주에 CSM이 먼저 연락해 주세요.",
      "최근 장애 문의가 많았던 고객사는 헬스 스코어 가중치를 다시 봐야겠어요."
     ],
     "sources": [
      {
       "title": "Create a health score in the customer success workspace – HubSpot Knowledge Base",
       "url": "https://knowledge.hubspot.com/help-desk/customize-a-health-score-in-the-customer-success-workspace",
       "kind": "official",
       "checked_at": "2026-10-15"
      },
      {
       "title": "Customer Health Score Explained: Metrics, Models & Tools",
       "url": "https://www.gainsight.com/blog/customer-health-scores/",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "리텐션",
     "note": "건강 점수는 고객 유지 가능성을 미리 보려는 지표입니다."
    },
    {
     "term": "NPS",
     "note": "설문 응답이 건강 점수의 입력값으로 자주 쓰입니다."
    }
   ],
   "confusable": [
    {
     "term": "CSAT",
     "difference": "CSAT는 한 번의 경험 만족도이고, 건강 점수는 여러 신호를 묶은 계정 단위 예측 점수입니다."
    }
   ]
  },
  {
   "id": "slo",
   "term": "SLO",
   "original": "Service Level Objective",
   "korean": "서비스 수준 목표",
   "aliases": [
    "에스엘오",
    "서비스수준목표",
    "서비스 목표 수준",
    "SLO 목표"
   ],
   "senses": [
    {
     "industries": [
      "platform"
     ],
     "roles": [
      "cx",
      "pm"
     ],
     "level": "심화",
     "importance": 3,
     "definition": "서비스가 얼마나 잘 동작해야 하는지 숫자로 정해 둔 내부 목표입니다. 응답 시간, 오류율, 가용성 같은 측정 지표(SLI)에 목표 값이나 범위를 붙여 정합니다.",
     "formula": null,
     "examples": [
      "이번 분기 SLO는 결제 API 성공률 99.9%로 잡았어요.",
      "상담 문의가 몰린 시간대에 응답 지연이 SLO를 넘었는지 먼저 확인해 주세요."
     ],
     "sources": [
      {
       "title": "Google SRE Book - Chapter 4: Service Level Objectives",
       "url": "https://sre.google/sre-book/service-level-objectives/",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "가용성",
     "note": "SLO를 정할 때 가장 흔히 쓰는 측정 지표입니다."
    },
    {
     "term": "에러 버짓",
     "note": "SLO를 기준으로 허용 가능한 실패 양을 계산합니다."
    },
    {
     "term": "장애",
     "note": "장애가 나면 SLO를 얼마나 깎아 먹었는지로 영향을 가늠합니다."
    }
   ],
   "confusable": [
    {
     "term": "SLA",
     "difference": "SLA는 고객과 맺은 약속이라 어기면 보상 등 결과가 따르고, SLO는 내부 목표 값입니다."
    }
   ]
  },
  {
   "id": "error_budget",
   "term": "에러 버짓",
   "original": "Error Budget",
   "korean": "오류 예산",
   "aliases": [
    "에러버짓",
    "오류예산",
    "error budget",
    "장애 허용량"
   ],
   "senses": [
    {
     "industries": [
      "platform"
     ],
     "roles": [
      "cx",
      "pm"
     ],
     "level": "심화",
     "importance": 3,
     "definition": "SLO를 지키면서도 허용되는 실패의 양입니다. 예산이 남아 있으면 새 기능 배포를 이어 가고, 다 쓰면 안정화 작업을 먼저 하는 기준으로 씁니다.",
     "formula": "에러 버짓 = 1 - SLO (예: SLO 99.9%면 에러 버짓 0.1%)",
     "examples": [
      "이번 달 에러 버짓을 벌써 80% 썼으니 큰 배포는 다음 주로 미루죠.",
      "어제 장애로 에러 버짓이 바닥나서 안정화 작업부터 하기로 했어요."
     ],
     "sources": [
      {
       "title": "Google SRE Workbook - Error Budget Policy for Service Reliability",
       "url": "https://sre.google/workbook/error-budget-policy/",
       "kind": "official",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "SLO",
     "note": "에러 버짓은 SLO에서 바로 계산됩니다."
    },
    {
     "term": "포스트모템",
     "note": "에러 버짓을 크게 쓴 장애는 포스트모템으로 원인을 정리합니다."
    },
    {
     "term": "장애",
     "note": "장애 시간과 실패 요청이 에러 버짓을 소진시킵니다."
    }
   ],
   "confusable": [
    {
     "term": "SLA",
     "difference": "SLA는 고객과의 계약상 약속이고, 에러 버짓은 내부 SLO를 기준으로 남은 실패 허용량입니다."
    },
    {
     "term": "가용성",
     "difference": "가용성은 실제로 서비스가 정상 동작한 비율이고, 에러 버짓은 목표 대비 허용된 실패 몫입니다."
    }
   ]
  },
  {
   "id": "safety_stock",
   "term": "안전 재고",
   "original": "Safety Stock",
   "korean": "안전재고",
   "aliases": [
    "안전재고",
    "세이프티 스톡",
    "버퍼 재고",
    "safety stock",
    "완충 재고"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce"
     ],
     "roles": [
      "cx",
      "pm"
     ],
     "level": "심화",
     "importance": 3,
     "definition": "수요가 갑자기 늘거나 입고가 늦어져도 품절이 나지 않도록 평소보다 더 쌓아 두는 여분의 재고입니다. 너무 많으면 보관비와 악성 재고 부담이 커져 적정 수준을 계산해 정합니다.",
     "formula": "안전 재고 = (최대 일 판매량 × 최대 리드타임) - (평균 일 판매량 × 평균 리드타임) (여러 계산법 가운데 간단한 방식)",
     "examples": [
      "프로모션 기간에는 인기 상품 안전 재고를 평소보다 늘려 두죠.",
      "품절 문의가 계속 들어오는 상품은 안전 재고 기준을 다시 봐야 할 것 같아요."
     ],
     "sources": [
      {
       "title": "Safety Stock: What It Is and How to Calculate It - Shopify",
       "url": "https://www.shopify.com/blog/safety-stock",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "품절",
     "note": "안전 재고는 품절을 막기 위한 장치입니다."
    },
    {
     "term": "리드타임",
     "note": "입고 리드타임이 길고 들쭉날쭉할수록 안전 재고가 더 필요합니다."
    },
    {
     "term": "재고 회전율",
     "note": "안전 재고를 과하게 잡으면 재고 회전율이 떨어집니다."
    }
   ],
   "confusable": [
    {
     "term": "재고 회전율",
     "difference": "재고 회전율은 재고가 얼마나 빨리 팔리는지 보는 지표이고, 안전 재고는 미리 정해 두는 여분 수량입니다."
    }
   ]
  },
  {
   "id": "reverse_logistics",
   "term": "역물류",
   "original": "Reverse Logistics",
   "korean": "역물류",
   "aliases": [
    "리버스 로지스틱스",
    "반품 물류",
    "회수 물류",
    "reverse logistics",
    "역방향 물류"
   ],
   "senses": [
    {
     "industries": [
      "ecommerce"
     ],
     "roles": [
      "cx"
     ],
     "level": "심화",
     "importance": 3,
     "definition": "고객에게 간 상품이 다시 판매자나 공급자 쪽으로 돌아오는 흐름을 다루는 물류입니다. 반품 회수, 리콜 같은 회수, 포장재 등의 폐기 처리가 포함됩니다.",
     "formula": null,
     "examples": [
      "반품 접수는 늘었는데 역물류 회수가 늦어서 환불 문의가 쌓이고 있어요.",
      "역물류 비용을 줄이려면 회수 상품 검수 기준부터 정리해야 해요."
     ],
     "sources": [
      {
       "title": "역물류 (Reverse Logistics) | 첼로스퀘어",
       "url": "https://www.cello-square.com/kr/blog/view-233.do",
       "kind": "company_guide",
       "checked_at": "2026-10-15"
      }
     ],
     "status": "verified"
    }
   ],
   "related": [
    {
     "term": "반품",
     "note": "역물류에서 가장 큰 비중을 차지하는 흐름입니다."
    },
    {
     "term": "반품률",
     "note": "반품률이 오르면 역물류 물량과 비용이 함께 늘어납니다."
    },
    {
     "term": "풀필먼트",
     "note": "풀필먼트 업체가 반품 회수와 재입고까지 맡는 경우가 많습니다."
    }
   ],
   "confusable": [
    {
     "term": "풀필먼트",
     "difference": "풀필먼트는 주문 상품을 고객에게 보내는 정방향 처리이고, 역물류는 고객에게서 돌아오는 흐름입니다."
    },
    {
     "term": "반품",
     "difference": "반품은 고객이 상품을 돌려보내는 거래 행위이고, 역물류는 그 상품을 실제로 옮기고 처리하는 물류 과정입니다."
    }
   ]
  }
 ]
};
