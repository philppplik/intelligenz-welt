import json,os,re,time
from common import *
os.makedirs('../data',exist_ok=True)
# AI news
ai=[]
for u,s in [('https://the-decoder.de/feed/','THE DECODER'),('https://www.theverge.com/rss/ai-artificial-intelligence/index.xml','The Verge AI'),('https://techcrunch.com/category/artificial-intelligence/feed/','TechCrunch AI'),('https://huggingface.co/blog/feed.xml','Hugging Face Blog'),('https://hnrss.org/newest?q=LLM&points=50','Hacker News'),('https://www.heise.de/rss/heise-atom.xml','heise online')]:
    items=feed(u,s,15)
    if s=='heise online': items=[i for i in items if re.search(r'\bKI\b|AI|Claude|GPT|OpenAI|Gemini|LLM|Nvidia',i['title'])]
    ai+=items
json.dump(merge_archive('../data/ai_archive.json',ai),open('../data/ai_archive.json','w'),ensure_ascii=False)
# models trending
b=get('https://huggingface.co/api/models?sort=trendingScore&limit=20')
models=[]
if b:
    for m in json.loads(b):
        models.append(dict(id=m['id'],likes=m.get('likes',0),dl=m.get('downloads',0),tag=m.get('pipeline_tag',''),url='https://huggingface.co/'+m['id']))
json.dump(models,open('../data/models.json','w'))

print(len(ai),len(models))
