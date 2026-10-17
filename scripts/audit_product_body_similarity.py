"""Read-only visible product-content similarity audit (not an SEO penalty score).

Measures 3-word shingle Jaccard after masking numbers. The whole <main>
includes repeated product modules; report its scores separately from the
first buyer paragraph. The comparison is within the same locale/category.
"""
import json, re, statistics, sys
from collections import defaultdict
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from site_renderer import SERIES
from sku_unique_openings import COPY
from sku_unique_openings_phase2 import COPY as PHASE2_COPY
LANGS=('en','es','pt','ru','tr')
FIRST=re.compile(r'<h1\b[^>]*>.*?</h1>\s*<p\b[^>]*class="[^"]*copy-muted[^"]*"[^>]*>(.*?)</p>',re.S|re.I)
MAIN=re.compile(r'<main\b[^>]*>(.*?)</main>',re.S|re.I)
WORDS=re.compile(r'[^\W_]+',re.U)
class Visible(HTMLParser):
 def __init__(self):
  super().__init__(convert_charrefs=True);self.skip=0;self.text=[]
 def handle_starttag(self,tag,attrs):
  if tag in ('nav','table','button','script','style','form','svg'):self.skip+=1
 def handle_endtag(self,tag):
  if tag in ('nav','table','button','script','style','form','svg'):self.skip=max(0,self.skip-1)
 def handle_data(self,data):
  if not self.skip and data.strip():self.text.append(data.strip())
def visible(source):
 x=Visible();x.feed(source);return ' '.join(x.text)
def intro(source):
 m=FIRST.search(source);return visible(m.group(1)) if m else ''
def grams(s):
 x=WORDS.findall(re.sub(r'\d+(?:[.,]\d+)*',' NUM ',s.casefold()))
 return set(tuple(x[i:i+3]) for i in range(max(0,len(x)-2)))
def score(a,b):
 return round(len(a&b)/len(a|b),4) if a and b else 0.0
def median_or_none(values):
 values=list(values)
 return round(statistics.median(values),3) if values else None
def audit():
 pages={}
 for row in SERIES.values():
  for lang in LANGS:
   path=ROOT/'dist'/('' if lang=='en' else lang)/'products'/row['slug']/'index.html'
   if not path.is_file():raise RuntimeError('Missing rendered page: '+str(path))
   html=path.read_text(encoding='utf8');m=MAIN.search(html)
   if not m:raise RuntimeError('Missing main: '+str(path))
   body=m.group(1);lead=intro(body)
   pages[(lang,row['slug'])]=dict(category=row['category'],pilot=row['slug'] in COPY or row['slug'] in PHASE2_COPY,
    intro=lead,lead_grams=grams(lead),main_grams=grams(visible(body)))
 groups=defaultdict(list)
 for (lang,slug),entry in pages.items():groups[(lang,entry['category'])].append((slug,entry))
 results=[]
 for (lang,category),rows in sorted(groups.items()):
  for sku,row in rows:
   neighbours=[(score(row['main_grams'],r['main_grams']),score(row['lead_grams'],r['lead_grams']),other)
               for other,r in rows if other!=sku]
   closest=max(neighbours,default=(0,0,''))
   results.append(dict(locale=lang,category=category,sku=sku,pilot=row['pilot'],
    nearest_sku=closest[2],nearest_main=closest[0],nearest_intro=closest[1],
    intro_words=len(WORDS.findall(row['intro']))))
 summary=[]
 for lang in LANGS:
  for pilot in (True,False):
   sub=[r for r in results if r['locale']==lang and r['pilot']==pilot]
   summary.append(dict(locale=lang,cohort='edited' if pilot else 'remaining',
    count=len(sub),median_nearest_main=median_or_none(r['nearest_main'] for r in sub),
    median_nearest_intro=median_or_none(r['nearest_intro'] for r in sub)))
 return dict(method='Visible main and first post-H1 paragraph; Jaccard 3-word shingles, digits masked; nearest same-category within same locale; diagnostic not Google score',
  models=len(SERIES),pages=len(pages),pilots=len(COPY)+len(PHASE2_COPY),summary=summary,rows=results)
if __name__=='__main__':
 result=audit()
 dest=ROOT/'_local_ops'/'product-body-similarity-2026-10-14.json'
 dest.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
 print('PRODUCT_BODY_AUDIT',result['models'],result['pages'])
 for row in result['summary']:print(row)
 print('REPORT',dest)
