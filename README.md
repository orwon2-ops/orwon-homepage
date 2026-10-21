# 오르원 홈페이지

orwon.kr 에 올라가는 오르원 회사 홈페이지입니다.

## 폴더

- `site/` 실제로 배포되는 사이트입니다. `index.html` 한 장과 `assets`(영상, 사진, 로고)로 되어 있습니다.
- `src/` 사이트를 고칠 때 쓰는 원본입니다. `body.html`(본문), `style.css`(디자인), `app.js`(움직임과 폼), `build.py`(셋을 합쳐 `index.html`을 만드는 스크립트), `press-extend.py`(기사 사진 배경을 옆으로 넓히는 스크립트).

## 배포

- Vercel 프로젝트의 Root Directory를 `site`로 두면, 이 저장소의 main에 올린 내용이 자동으로 배포됩니다.
- 도메인 orwon.kr 은 가비아 DNS 관리에서 Vercel이 알려 주는 A 레코드와 CNAME 값으로 연결합니다. 메일(MX) 레코드는 건드리지 않습니다.

## 제품 제안 폼

- `site/index.html`의 폼은 Web3Forms로 보내고, 제출 내용은 kim@orwon.kr 로 옵니다. 키는 `src/build.py`의 `FORM_KEY`이며 원래 페이지에 공개되는 값입니다.
