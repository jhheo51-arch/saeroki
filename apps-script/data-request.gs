/**
 * 데이터 요청 접수 (슬랙 무료 플랜용, 워크플로 빌더 대신 Google 설문지 + 웹훅)
 *
 * 1. script.google.com 새 프로젝트에 이 파일을 붙여 넣습니다.
 * 2. 프로젝트 설정 > 스크립트 속성에 두 값을 넣습니다.
 *    DATA_WEBHOOK  #data-질문 Incoming Webhook 주소
 *    BOT_TOKEN     새록이 Bot User OAuth Token (xoxb-, chat:write 권한)
 * 3. setup을 한 번 실행하면 설문지와 제출 트리거가 만들어지고 로그에 설문지 링크가 나옵니다.
 * 4. 그 링크를 FORM_URL에 넣고 postGuide를 실행하면 채널에 안내 메시지가 올라갑니다. 고정은 슬랙에서 합니다.
 */

const CHANNEL_ID = 'C0CEEF8HB6G'; // #data-질문
const OWNER_ID = 'U0C1XN7C550'; // DM 받을 담당자
const FORM_URL = 'https://docs.google.com/forms/d/e/1FAIpQLSdBCb4JOtRSNstHrml2KsU5Z-Ja7cPUhaQkFJuVfhQvv094Yw/viewform';
const QUESTIONS = [
  // [제목, 종류, 도움말]
  ['요청자', 'text', '슬랙 표시 이름'],
  ['지표', 'text', '예: 카테고리별 매출'],
  ['기간', 'text', '예: 2026년 10월'],
  ['기한', 'date', '이 날까지 받고 싶어요'],
  ['설명', 'paragraph', '어디에 쓸 자료인지, 원하는 형태(표, 차트) 등'],
];
const EMOJI = { 요청자: '🙋', 지표: '📊', 기간: '🗓️', 기한: '⏰', 설명: '📝' };

function setup() {
  const form = FormApp.create('📥 데이터 요청 접수')
    .setDescription('제출하면 #data-질문 채널에 올라가고 담당자에게 알림이 가요.');
  QUESTIONS.forEach(([title, kind, help]) => {
    const item = kind === 'date' ? form.addDateItem()
      : kind === 'paragraph' ? form.addParagraphTextItem()
      : form.addTextItem();
    item.setTitle(title).setHelpText(help).setRequired(true);
  });
  ScriptApp.newTrigger('onSubmit').forForm(form).onFormSubmit().create();
  Logger.log('설문지 링크: ' + form.getPublishedUrl());
  Logger.log('편집 링크: ' + form.getEditUrl());
}

function postGuide() {
  postJson(PropertiesService.getScriptProperties().getProperty('DATA_WEBHOOK'), {
    text: '📥 데이터 요청 접수: ' + FORM_URL,
    blocks: [
      { type: 'section', text: { type: 'mrkdwn', text:
        '📥 *데이터 요청 접수*\n양식으로 데이터 요청을 받아 data-질문 채널에 올리고 담당자에게 알립니다' } },
      { type: 'section', text: { type: 'mrkdwn', text: `▶️ *<${FORM_URL}|요청서 열기>*` } },
      { type: 'context', elements: [{ type: 'mrkdwn', text:
        '🙋 요청자  📊 지표  🗓️ 기간  ⏰ 기한  📝 설명, 모두 필수예요  |  🔖 채널 상단 북마크에서도 열 수 있어요' }] },
    ],
  });
}

function onSubmit(e) {
  const props = PropertiesService.getScriptProperties();
  const answers = {};
  e.response.getItemResponses().forEach(r => { answers[r.getItem().getTitle()] = r.getResponse(); });

  const lines = QUESTIONS.map(([title]) => `${EMOJI[title]} *${title}*\n${answers[title] || '-'}`);
  postJson(props.getProperty('DATA_WEBHOOK'), {
    text: ['📥 *[요청] 새 데이터 요청이 들어왔습니다*', '', ...lines].join('\n'),
  });
  postJson('https://slack.com/api/chat.postMessage', {
    channel: OWNER_ID,
    text: `🔔 <#${CHANNEL_ID}> 에 새 데이터 요청이 들어왔습니다. 지표: ${answers['지표']} (기한 ${answers['기한']})`,
  }, props.getProperty('BOT_TOKEN'));
}

function postJson(url, payload, token) {
  const headers = token ? { Authorization: 'Bearer ' + token } : {};
  const res = UrlFetchApp.fetch(url, {
    method: 'post', contentType: 'application/json; charset=utf-8',
    headers, payload: JSON.stringify(payload), muteHttpExceptions: true,
  });
  Logger.log(res.getResponseCode() + ' ' + res.getContentText());
}
