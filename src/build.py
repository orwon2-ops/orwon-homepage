import os, re, base64, subprocess, html, shutil
S='/tmp/claude-0/-home-user/3f27ac15-0e97-50b1-9036-1e65c4005757/scratchpad'
css=open(f'{S}/src/style.css').read()
body=open(f'{S}/src/body.html').read()
js=open(f'{S}/src/app.js').read()
# every clip is cleared for use (kim, 2026-10-21), so the preview and the site both show them from the start

A=[('검증형','알고리즘 점령한 딕션관리기'),('의심템 까보기형','볼펜 무는 거랑 똑같을 줄 알았어요'),('사용 오해형','처음부터 제일 세게 할 필요 없어요'),
   ('자가진단형','발음 자가점검 체크리스트'),('콩트형','3일 만에 되는 법 없냐'),('POV형','면접 가는 길'),('챌린지형','세 번만 빠르게'),('띠화면 설명형','볼펜처럼 물고 읽는 게 아니라고')]
B=[('흥정 상황극','깎아주세요'),('게임 화면형','아이템 획득'),('파파라치형','포착'),('소문 자막형','요즘 신기한 얘기'),
   ('부모 시점형','딸 방문을 열었다가'),('퀴즈형','듣는 사람만 답답한 말버릇'),('종이인형형','똑같이 외웠는데'),('면접 꿀팁형','경험 질문 답변 순서')]
def track(items):
    one=''.join(f'<span class="ad"><i>{html.escape(f)}</i><b>{html.escape(t)}</b></span>' for f,t in items)
    return f'      <div style="display:contents">{one}</div><div style="display:contents" aria-hidden="true">{one}</div>'
import random
names=[f'c{i:02d}' for i in range(1,31)]
order=list(range(len(names))); random.Random(11).shuffle(order)
cases='\n'.join(f'        <div class="ct" data-o="{o}"><video muted loop playsinline preload="none" poster="assets/c/{n}.jpg" data-csrc="assets/c/{n}.mp4"></video></div>' for n,o in zip(names,order))
body=body.replace('{{CASES}}',cases)
anames=[f'a{i:02d}' for i in range(1,25)]
anames[anames.index('a08')]='a25'  # kim (10-21): the a08 clip moved up to the large phone (v/c3), and the clip that was there (c1, as a25) takes its tile
aorder=list(range(len(anames))); random.Random(29).shuffle(aorder)
actors='\n'.join(f'        <div class="ct" data-o="{o}"><video muted loop playsinline preload="none" poster="assets/a/{n}.jpg" data-csrc="assets/a/{n}.mp4"></video></div>' for n,o in zip(anames,aorder))
body=body.replace('{{ACTORS}}',actors)
# press cards: outlet, date, title, link, photo, photo focus (object-position: on phones the photo is cut to a narrow column, so the focus keeps the face in it).
# without a photo (img=None) the thumbnail is the outlet's name on a navy tile; a None date or title leaves a placeholder.
# 한국경제's date is the one in its article address (2026/09/30); kim gave both titles and 경상일보's date (2026-10-21).
# 내외경제TV (title, date and address from kim) replaced the 대학저널 백현정 card (2026-10-21); 대학저널's date is its approval date, and its title's middle dot is written as 과, like the rest of the site.
# the photos are the articles' own, sent by kim (2026-10-21) and cropped to 3:2 in work/press: 정예린 at the KBS N set (kim's pick), 김햇살, 류상화, and the product shot from 대학저널.
# 김햇살 and 류상화 show the upper body like 정예린 (kim, 10-21): their studio portraits are narrower than 3:2, so work/press/extend.py continues the plain backdrop to the sides and leaves the photo itself untouched (*-wide.jpg).
PRESS=[('한국경제','2026.09.30','하이딕션, KBS N 경제캐스터 정예린 아나운서 학술자문위원 위촉','https://www.hankyung.com/article/202609304597O','assets/press/hk.jpg','67% 50%'),
       ('경상일보','2026.07.09','하이딕션, 스피치31데이즈 아카데미와 공식 교육협력 체결','https://www.ksilbo.co.kr/news/articleView.html?idxno=1061686','assets/press/ks-wide.jpg','50% 50%'),
       ('내외경제TV','2026.07.01','하이딕션, 발음 교육 전문성 강화…류상화 아나운서 합류','https://www.nbntv.co.kr/news/articleView.html?idxno=4022735','assets/press/nbn-wide.jpg','51% 50%'),
       ('대학저널','2026.05.13','하이딕션, 이탈리아 국립음악원 출신 발음과 발성 자문위원 위촉','https://dhnews.co.kr/news/view/1065597242752277','assets/press/dh.jpg','55% 50%')]
OUT='<svg width="14" height="14" viewBox="0 0 16 16" aria-hidden="true"><path d="M5.5 3.5h7v7M12.5 3.5l-9 9" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'
def press_card(src,date,title,url,img,pos=None):
    focus=f' style="object-position:{pos}"' if pos else ''
    thumb=(f'<span class="press-thumb has-img" aria-hidden="true"><img src="{img}" alt="" loading="lazy"{focus}></span>' if img else
           f'<span class="press-thumb" aria-hidden="true"><span class="rings"></span><b>{src}</b></span>')
    d=f'<span class="press-date">{date}</span>' if date else '<span class="press-date"><span class="ph">[날짜]</span></span>'
    t=html.escape(title) if title else '<span class="ph">[기사 제목]</span>'
    return (f'      <li><a class="press-card" href="{url}" target="_blank" rel="noopener">{thumb}'
            f'<span class="press-body"><span class="press-src">{src}{d}</span><span class="press-t">{t}</span><span class="press-go">기사 보기{OUT}</span></span></a></li>')
body=body.replace('{{PRESS}}','    <ul class="press-list">\n'+'\n'.join(press_card(*p) for p in PRESS)+'\n    </ul>')
# shared bits: arrow icon, and the closing band each tab ends with (next="..." adds a link to the following tab)
ARROW='<svg class="ex-go" width="22" height="22" viewBox="0 0 22 22" aria-hidden="true"><path d="M4.5 11h12.5M12 5.5l5.5 5.5-5.5 5.5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
def cta(m):  # {{CTA|h=headline|sub=line under it|next=tab|label=tab name|cls=extra class}}
    a=dict(re.findall(r'\|(\w+)=([^|]*)',m.group(1)))
    sub=f'\n        <p class="cta-sub">{a["sub"]}</p>' if 'sub' in a else ''
    nxt=(f'\n    <a class="next" href="#{a["next"]}"><small>다음</small><b>{a["label"]}</b>{ARROW.replace("ex-go","next-go")}</a>' if 'next' in a else '')
    return (f'<section class="cta{(" "+a["cls"]) if "cls" in a else ""}">\n  <div class="wrap">\n    <div class="cta-card">\n      <span class="rings" aria-hidden="true"></span>\n'
            f'      <div class="cta-txt">\n        <h2 class="cta-h">{a["h"]}</h2>{sub}\n      </div>\n'
            '      <a class="btn btn-lg btn-primary" href="#contact">제품 제안하기</a>\n'
            f'    </div>{nxt}\n  </div>\n</section>')
body=re.sub(r'\{\{CTA((?:\|[^}]*)?)\}\}',cta,body).replace('{{ARROW}}',ARROW)
# the letter's signature: a temporary drawing from an OFL handwriting font until the CEO's own is scanned (SIGN=b picks the other draft); v10 drops the tail stroke, which made 화 read as 환
sp=f'{S}/work/v10/sign/sign-{os.environ.get("SIGN","a")}.svg'
if os.path.exists(sp):
    sv=open(sp).read().strip()
    sv=re.sub(r'<\?xml[^>]*>\s*','',sv)
    sv=re.sub(r'fill="#[0-9a-fA-F]{3,6}"','fill="currentColor"',sv)
    sv=re.sub(r'stroke="#[0-9a-fA-F]{3,6}"','stroke="currentColor"',sv)
    sv=re.sub(r'\s(width|height)="[^"]*"','',sv,count=2) if re.match(r'<svg[^>]*\s(width|height)=',sv) else sv
    sv=sv.replace('<svg ','<svg class="sign-img" ',1)
else:
    sv='<p class="sign-img sign-ph">서명</p>'
body=body.replace('{{SIGN}}','        '+sv)
assert '{{' not in body.replace('{{TRACK_A}}','').replace('{{TRACK_B}}',''), 'unfilled template'
body=body.replace('{{TRACK_A}}',track(A)).replace('{{TRACK_B}}',track(B))
pre="<script>document.documentElement.classList.add('js')</script>"

# font subset for the artifact (inline data URI)
frag_wo_font=f"<title>오르원 홈페이지 초안</title>\n{css}{body}{js}"
chars=set(frag_wo_font)|set(chr(c) for c in range(32,127))|set('○©—–“”‘’…×')
open(f'{S}/work/chars.txt','w').write(''.join(sorted(chars)))
subprocess.run(['pyftsubset',f'{S}/work/package/dist/public/variable/PretendardVariable.ttf',f'--text-file={S}/work/chars.txt',
  '--flavor=woff2','--layout-features=*',f'--output-file={S}/work/pv-subset.woff2'],check=True)
b64=base64.b64encode(open(f'{S}/work/pv-subset.woff2','rb').read()).decode()
face=('@font-face{font-family:"Pretendard Variable";font-weight:45 920;font-style:normal;font-display:swap;'
      f'src:url(data:font/woff2;base64,{b64}) format("woff2")}}')

artifact=(f'<title>오르원 홈페이지 초안</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n'
          f'<style>{face}</style>\n<style>\n{css}</style>\n{pre}\n{body}\n<script>\n{js}</script>\n')
open(f'{S}/build/artifact.html','w').write(artifact)

desc='오르원은 광고 대행사가 아니라 좋은 제품을 찾아 직접 파는 회사입니다. 광고비나 대행료 없이, 제조사, 수입사, 유통사의 제품을 브랜드로 키워 판매합니다.'
# the site keeps only what is decided: no review panel, no earlier home, no draft-only styles or script
sbody=re.sub(r'<!--(draft|was)-->.*?<!--/\1-->\n*','',body,flags=re.S)
sbody=re.sub(r'<span class="was">.*?</span>','',sbody)
sbody=re.sub(r'<span class="now">(.*?)</span>',r'\1',sbody).replace(' now"','"')
scss=re.sub(r'/\*draft\*/.*?/\*/draft\*/\n?','',css,flags=re.S)
sjs=re.sub(r'  /\*draft\*/.*?/\*/draft\*/\n','',js,flags=re.S)
assert 'class="was' not in sbody and 'pick' not in sbody and '.pick' not in scss and '.pick' not in sjs
site=f'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>오르원 ORWON</title>
<meta name="description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:title" content="오르원 ORWON | 시간이 지나도, 찾는 이름이 되도록">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="/assets/og.png">
<meta property="og:locale" content="ko_KR">
<meta name="theme-color" content="#0e1a2b">
<link rel="icon" type="image/png" href="/assets/favicon.png">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">
<style>
{scss}</style>
{pre}
</head>
<body>
{sbody}
<script>
{sjs}</script>
</body>
</html>
'''
# the site's form really sends: the Web3Forms access key kim made for kim@orwon.kr (2026-10-21). The key is public by design, it only routes submissions to that inbox.
# the preview has no key, so there the form only shows its done screen and keeps the note that nothing is sent.
FORM_KEY='feb8ea5b-2593-457c-8afa-ccf7979fd580'
for a,b in [('<form id="propose" novalidate>',f'<form id="propose" novalidate data-key="{FORM_KEY}">'),
            ('\n        <p class="f-note">미리보기 화면이라 실제로 보내지지는 않습니다.</p>','')]:
    assert site.count(a)==1,a
    site=site.replace(a,b)
# the site folder is everything a host needs and nothing else: the page plus each file it points to (clips, posters, logos, icons, link preview)
open(f'{S}/build/site/index.html','w').write(site)
need=set(re.findall(r'(?:src|href|poster|data-src|data-csrc|content)="/?(assets/[^"#?]+)"',site))|set(re.findall(r'url\((assets/[^)]+)\)',site))
miss=[n for n in need if not os.path.isfile(f'{S}/build/{n}')]
assert not miss, f'missing assets: {miss}'
shutil.rmtree(f'{S}/build/site/assets',ignore_errors=True)
for n in need:
    os.makedirs(os.path.dirname(f'{S}/build/site/{n}'),exist_ok=True); shutil.copy(f'{S}/build/{n}',f'{S}/build/site/{n}')
site_kb=sum(os.path.getsize(f'{S}/build/site/{n}') for n in need)//1024
print('font subset KB',os.path.getsize(f'{S}/work/pv-subset.woff2')//1024,'| glyph chars',len(chars),'| artifact KB',len(artifact.encode())//1024,'| site KB',len(site.encode())//1024,'| site files',len(need)+1,'| assets KB',site_kb)
# local preview wrapper for the screenshot tests
open(f'{S}/build/preview.html','w').write('<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"></head><body>\n'+artifact+'\n</body></html>')
