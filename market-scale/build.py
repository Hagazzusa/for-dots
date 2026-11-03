"""Original editable SVG illustration; no images, fonts or external assets."""
from pathlib import Path
import subprocess, os, sys
R=Path(__file__).resolve().parent
DRAFT='--draft' in sys.argv
work=R/'work';work.mkdir(exist_ok=True)
env=os.environ.copy();env['INKSCAPE_PROFILE_DIR']=str(work/'inkscape-profile');env['XDG_CACHE_HOME']=str(work/'cache')
lines=[]
for i in range(15):
 y=72+i*25;lines.append(f'<path d="M272 {y}H825" stroke="#354b56" stroke-width="2"/>')
marks=[]
import math
for i in range(19):
 a=math.radians(210+i*15);r1=49 if i%3 else 44;r2=54
 marks.append(f'<path d="M{509+r1*math.cos(a):.2f} {455+r1*math.sin(a):.2f}L{509+r2*math.cos(a):.2f} {455+r2*math.sin(a):.2f}"/>')
svg='''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="700" viewBox="0 0 900 700">
<title>저울을 덮어 둔 밤</title><desc>가상의 시장길. 닫힌 셔터 앞 작은 저울의 빈 접시에 접어 둔 천 한 장이 놓여 있다. 사람과 버스는 그리지 않았다.</desc>
<defs>
 <linearGradient id="night" x2="0" y2="1"><stop stop-color="#263e4e"/><stop offset="1" stop-color="#395362"/></linearGradient>
 <linearGradient id="cloth" x2="1" y2="1"><stop stop-color="#e2dcc7"/><stop offset="1" stop-color="#c0c4b4"/></linearGradient>
</defs>
<rect width="900" height="700" fill="#203642"/>
<!-- The composition is drawn colour, not a lighting simulation. -->
<path d="M0 0H252V437L0 521Z" fill="#2c485a"/>
<path d="M252 0H900V469L252 437Z" fill="#52636a"/>
<rect x="274" y="41" width="554" height="394" rx="3" fill="url(#night)"/>
SHUTTER_LINES
<path d="M254 0H274V445H254Z" fill="#a69d85"/>
<path d="M828 0H850V460H828Z" fill="#b3a487"/>
<path d="M850 0H900V466H850Z" fill="#344a53"/>
<rect x="868" y="92" width="32" height="218" fill="#d9ad73"/>
<path d="M868 92H877V310H868Z" fill="#8b765b"/>
<path d="M0 521L252 437L900 469V700H0Z" fill="#314953"/>
<g fill="none" stroke="#55707a" stroke-width="2" opacity=".45">
 <path d="M0 603L368 468M23 700L485 461M402 700L638 459M729 700L793 466"/>
 <path d="M0 589L900 573M0 667L900 640"/>
</g>
<!-- Market counter, cropped so this is a corner rather than a whole street. -->
<path d="M169 455L716 398L830 540L250 617Z" fill="#a88e74"/>
<path d="M250 617L830 540V700H250Z" fill="#7c6d60"/>
<path d="M169 455L250 617V700H169Z" fill="#655e56"/>
<path d="M169 455L716 398L830 540L250 617Z" fill="none" stroke="#c4aa8a" stroke-width="6" stroke-linejoin="round"/>
<path d="M260 620L830 546" stroke="#564f49" stroke-width="7"/>
<!-- A restrained cut-paper shadow anchors the scale. -->
<path d="M389 510L636 484L719 534L432 571Z" fill="#6c6a60" opacity=".65"/>
<path d="M388 518Q385 500 401 494L586 478Q604 477 612 493L626 523Q627 534 611 538L415 558Q401 560 396 550Z" fill="#294a4d"/>
<path d="M409 511L593 495L607 520L421 540Z" fill="#65827c"/>
<!-- Enamel body and a quiet unnumbered dial. -->
<path d="M403 407Q404 378 433 374L568 363Q590 361 599 389L617 490Q618 505 597 510L421 529Q402 530 400 509Z" fill="#648d86"/>
<path d="M571 366Q590 364 599 389L617 490Q618 505 597 510L581 511Z" fill="#416c68"/>
<path d="M418 407Q420 391 438 388L565 378" fill="none" stroke="#91aaa0" stroke-width="5" stroke-linecap="round"/>
<ellipse cx="509" cy="455" rx="65" ry="64" fill="#294f52"/>
<ellipse cx="509" cy="455" rx="59" ry="58" fill="#e5d9bc"/>
<g fill="none" stroke="#637269" stroke-width="2" stroke-linecap="round">DIAL_MARKS</g>
<path d="M509 455L509 410" stroke="#8b6150" stroke-width="3.5" stroke-linecap="round"/>
<circle cx="509" cy="455" r="5" fill="#65776c"/>
<path d="M477 482Q509 490 541 482" stroke="#c5c6ad" stroke-width="2" fill="none"/>
<!-- A shallow, empty weighing pan remains visible at right. -->
<path d="M489 370L487 339L534 336L537 366Z" fill="#426866"/>
<ellipse cx="505" cy="328" rx="154" ry="27" fill="#90a8a0"/>
<path d="M351 328Q505 373 659 328L646 345Q506 388 366 345Z" fill="#527975"/>
<ellipse cx="505" cy="324" rx="154" ry="24" fill="#b1c0b2"/>
<path d="M365 324Q504 355 645 324" fill="none" stroke="#d0d3be" stroke-width="3"/>
<!-- One cloth with rounded folds and a soft unsupported edge. -->
<path d="M358 306C395 305 436 289 476 295C511 298 551 307 570 317C554 327 532 332 518 336C493 342 480 345 468 346C458 370 456 395 446 411C425 423 402 423 386 416C377 393 373 373 371 354C369 334 361 320 358 306Z" fill="#879c91" opacity=".4"/>
<path d="M354 299C391 297 431 283 474 289C508 292 548 300 567 310C551 320 531 326 515 330C492 336 478 337 464 340C455 362 453 389 442 404C424 416 402 417 383 409C374 389 371 369 367 350C365 330 357 314 354 299Z" fill="url(#cloth)"/>
<path d="M354 299C378 302 399 309 418 316C437 325 451 331 464 340C455 362 453 389 442 404C424 416 402 417 383 409C374 389 371 369 367 350C365 330 357 314 354 299Z" fill="#c1c5b4"/>
<path d="M418 316C437 301 453 287 474 289C508 292 548 300 567 310C550 320 532 325 515 330C482 325 451 320 418 316Z" fill="#e3dfcc"/>
<path d="M418 316C438 324 452 331 464 340C458 354 451 370 450 383" fill="none" stroke="#a0ad9d" stroke-width="2.5" stroke-linecap="round"/>
<path d="M374 357C378 375 381 387 389 398C405 404 422 400 436 395" fill="none" stroke="#668a85" stroke-width="3.5" stroke-linecap="round"/>
<path d="M361 310C365 326 370 337 372 350M397 339C397 359 401 378 407 389" fill="none" stroke="#d8dac8" stroke-width="2" stroke-linecap="round"/>
<!-- A little wear, not text, a logo, a price or a hidden message. -->
<path d="M709 426L736 423M289 579L320 574" stroke="#d3b897" stroke-width="3" stroke-linecap="round" opacity=".65"/>
</svg>'''.replace('SHUTTER_LINES','\n'.join(lines)).replace('DIAL_MARKS','\n'.join(marks))
(R/'market_scale.svg').write_text(svg)
subprocess.run(['inkscape',str(R/'market_scale.svg'),'--export-type=png','--export-filename='+str(R/('market_scale_draft.png' if DRAFT else 'market_scale_final.png')),'--export-width='+('900' if DRAFT else '1800')],check=True,env=env)
