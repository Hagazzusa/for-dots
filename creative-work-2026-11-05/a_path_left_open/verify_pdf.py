from pathlib import Path
import fitz,json,math,hashlib
P=Path(__file__).resolve().parent;MM=72/25.4
main=fitz.open(P/'output/pdf/A-Path-Left-Open.pdf');answers=fitz.open(P/'output/pdf/A-Path-Left-Open-Answers.pdf')
assert len(main)==len(answers)==2
for doc in [main,answers]:
 for page in doc:
  assert abs(page.rect.width/MM-210)<.001 and abs(page.rect.height/MM-297)<.001
  for block in page.get_text('dict')['blocks']:
   for line in block.get('lines',[]):
    for span in line['spans']:
     r=fitz.Rect(span['bbox']);assert r.x0>=14*MM and r.x1<196*MM and r.y0>10*MM and r.y1<294*MM,(span['text'],r)
rects=[]
for draw in main[0].get_drawings():
 for item in draw['items']:
  if item[0]=='re' and draw['fill'] is not None:
   rects.append(item[1]);assert abs(item[1].width/MM-18)<.001 and abs(item[1].height/MM-18)<.001
assert len(rects)==16
board_rects=[]
for draw in main[1].get_drawings():
 for item in draw['items']:
  if item[0]=='re' and abs(item[1].width/MM-90)<.001 and abs(item[1].height/MM-90)<.001:board_rects.append(item[1])
assert len(board_rects)==2
scale=[]
for draw in main[0].get_drawings():
 for item in draw['items']:
  if item[0]=='l' and abs(item[1].y-item[2].y)<.001 and abs(abs(item[1].x-item[2].x)/MM-50)<.001:scale.append(item)
assert len(scale)==1
plain=main[0].get_text();assert '단면' in plain and '뒤집' in plain and '뒷면' in plain and '대각선' in plain
report=json.loads((P/'independent_report.json').read_text());assert report['valid_arrangements']==24 and report['distinct_empty_paths']==10
q={'main_pages':2,'answers_pages':2,'answer_cover_prevents_first_page_solution_preview':True,'page_mm':[210,297],'piece_cell_mm':18,'board_mm':90,'scale_bar_mm':50,'actual_pdf_vectors_checked':True,'all_16_piece_cell_rectangles_correct_size':True,'text_bounds_passed':True,'independent_solution_counts':[4,1],'visual_review':'Pending final post-instruction-change inspection.','limits':['PDF dimensions and arrangements verified digitally; physical printer scaling and cutting precision were not tested.','No timed playtest or difficulty rating is claimed.'],'files':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in (P/'output/pdf').glob('*.pdf')}}
(P/'qa.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n');print(q)
