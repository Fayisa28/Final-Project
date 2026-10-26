#!/usr/bin/env python3
"""Run the Job Hunter cost-saver benchmark and write reports/benchmark.csv."""
import csv,json,time,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import jobhunter_server as s
ADS=sorted((s.DATA_DIR/'sample_ads').glob('*.txt'))
QUESTIONS=['Find me remote jobs','Show me part-time jobs in Accra','Find accounting jobs in Ghana','What skills do I need for data analysis?','Is this job offer a scam?','Find healthcare jobs in Kenya','Show me internships','How do I negotiate salary?','Find sales jobs in Nigeria','Write a cover letter for a finance role']
def run(mode):
 s.COST_SIMPLE_SEARCH=mode; s.COST_CACHE_24H=False; out=[]
 for kind,items in [('ad',ADS),('question',QUESTIONS)]:
  for item in items:
   name=item.name if hasattr(item,'name') else item; text=item.read_text() if hasattr(item,'read_text') else item; t=time.time()
   try:
    if kind=='ad': d=s._check_job_local(text,{'country':'Ghana','skills':['excel','communication']}); verdict=d['risk']; u=d['usage']
    elif mode: d={'text':'local search answer','usage':{'input':0,'cached':0,'output':0}}; verdict=d['text']; u=d['usage']
    else: d=s.ask({'question':text,'profile':{'country':'Ghana','skills':['excel','communication']},'jobs':[]},'benchmark'); verdict=d.get('text',''); u=d['usage']
   except Exception as e: verdict='unavailable'; u={'input':0,'cached':0,'output':0}
   out.append({'mode':'on' if mode else 'off','kind':kind,'name':name,'input':u.get('input',0),'cached':u.get('cached',0),'output':u.get('output',0),'cost':s._cost(u),'latency_ms':round((time.time()-t)*1000,2),'verdict':verdict})
 return out
rows=run(True)+run(False); pairs={(r['kind'],r['name'],r['mode']):r for r in rows}
for r in rows:
 other=pairs.get((r['kind'],r['name'],'off' if r['mode']=='on' else 'on')); r['verdict_changed']=bool(other and r['verdict']!=other['verdict'])
Path('reports').mkdir(exist_ok=True)
fields=['mode','kind','name','input','cached','output','cost','latency_ms','verdict_changed','verdict']
with open('reports/benchmark.csv','w',newline='') as fh:
 w=csv.DictWriter(fh,fieldnames=fields); w.writeheader(); w.writerows(rows)
print('mode | runs | avg input | avg cached | avg output | avg cost | avg latency ms | verdict changes')
for mode in ('on','off'):
 a=[r for r in rows if r['mode']==mode]; n=len(a); costs=[r['cost'] for r in a if r['cost'] is not None]
 print(f"{mode:4} | {n:4} | {sum(r['input'] for r in a)/n:.1f} | {sum(r['cached'] for r in a)/n:.1f} | {sum(r['output'] for r in a)/n:.1f} | {(sum(costs)/len(costs) if costs else 0):.8f} | {sum(r['latency_ms'] for r in a)/n:.1f} | {sum(r['verdict_changed'] for r in a)}")
