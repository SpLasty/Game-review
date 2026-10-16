# Analyzes the collected reviews and developer announcements.

import csv
from collections import Counter, defaultdict
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import re
import statistics
import argparse

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / 'data' / 'raw' / 'steam_30_games'
OUT = ROOT / 'data' / 'processed' / 'steam_30_games'
MIN_WORDS = 10
PATTERNS = {
    'update': r'\b(?:patch(?:es|ed)?|updates?|nerf\w*|buff\w*|rebalanc\w*)\b',
    'stability': r'\b(?:crash\w*|freez\w*|stutter\w*|fps|lag\w*|performance|disconnect\w*)\b',
    'balance': r'\b(?:nerf\w*|buff\w*|balanc\w*|overpowered|underpowered)\b',
    'monetization': r'\b(?:warbonds?|microtransactions?|monetiz\w*|pay\s*to\s*win|p2w|super\s+credits)\b',
    'cheating': r'\b(?:cheat\w*|hackers?|anti[- ]?cheat)\b',
    'bugs': r'\b(?:bugs?|buggy|glitches?|glitchy)\b',
}

VERIFIED = {'1844751498220713', '1844115010503588', '1841579228677702', '1840944183785447',
            '1846018067931597', '1845383656394875', '1845383656387875', '1840310314341287',
            '1844751498231307', '1844751498218925'}
STOP = set('the a an of to in is it and or for with on at as be this that are was were i you we they my your our their have has had but so not no do does did game games play played playing good great really just very can its if all from me like get been more much when even would dont im one will some about also after new now steam fun'.split())

def iso(ts): return datetime.fromtimestamp(ts, timezone.utc).isoformat()
def tokens(text): return [x for x in re.findall(r'[a-z][a-z0-9_-]{2,}',text.lower()) if x not in STOP]
def write_csv(name, rows):
    if not rows: return
    with (OUT / name).open('w',encoding='utf-8-sig',newline='') as f:
        w = csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
def wilson(k,n):
    if not n:return [None,None]
    z=1.96;p=k/n;d=1+z*z/n;center=(p+z*z/(2*n))/d;h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return [center-h,center+h]

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    reviews=[]; notes=[]
    for p in sorted(SNAPSHOT.glob('*/reviews.jsonl')):
        for line in p.read_text(encoding='utf-8').splitlines():
            r=json.loads(line);a=r['author'];text=r['review']
            reviews.append(dict(appid=r['appid'],game=r['game'],review_id=r['recommendationid'],review_text=text,language=r.get('language','unknown'),
                created_utc=iso(r['timestamp_created']),updated_utc=iso(r['timestamp_updated']),
                timestamp_created=r['timestamp_created'],timestamp_updated=r['timestamp_updated'],
                recommended=r['voted_up'],unedited=r['timestamp_created']==r['timestamp_updated'],
                playtime_at_review_hours=a.get('playtime_at_review')/60 if a.get('playtime_at_review') is not None else None,
                lifetime_playtime_hours=a.get('playtime_forever')/60 if a.get('playtime_forever') is not None else None,
                primarily_steam_deck=r.get('primarily_steam_deck'),steam_purchase=r.get('steam_purchase'),refunded=r.get('refunded'),
                author_hash=a['author_hash'],word_count=len(re.findall(r'\b\w+\b',text)),
                text_eligible=r.get('language')=='english' and len(re.findall(r'\b\w+\b',text))>=MIN_WORDS,
                **{f'mentions_{name}':bool(re.search(pattern,text,re.I)) for name,pattern in PATTERNS.items()},
                mentions_version=bool(re.search(r'\b\d+\.\d+(?:\.\d+)*\b',text)),source_url=r['source_url']))
    for p in sorted(SNAPSHOT.glob('*/news.json')):
        for n in json.loads(p.read_text(encoding='utf-8')):
            title=n['title'];text=n['text']
            candidate = bool(re.search(r'patch|hotfix|release notes|\d+\.\d+',title,re.I)) or (bool(re.search(r'update',title,re.I)) and bool(re.search(r'\b(?:fixed|increased|decreased|changes|bug fixes)\b',text,re.I)))
            branch = 'unstable' if re.search(r'\bunstable\b',title,re.I) else 'stable' if re.search(r'\bstable\b',title,re.I) else 'unspecified'
            notes.append(dict(appid=n['appid'],game=n['game'],gid=n['gid'],title=title,date_utc=iso(n['date']),timestamp=n['date'],release_branch_hint=branch,
                patch_candidate=candidate,verification_status='manually_verified_patch' if n['gid'] in VERIFIED else 'unverified_candidate' if candidate else 'unverified_other',
                text=text,source_url=n['url'],feed=n['feedname']))
    raw_all=reviews
    excluded_language=[r for r in raw_all if r['language']!='english']
    reviews=[r for r in raw_all if r['language']=='english']
    assert len({(r['appid'],r['review_id']) for r in reviews})==len(reviews), 'Duplicate review IDs'
    assert all(r['timestamp_created']<=r['timestamp_updated'] for r in reviews),'Invalid timestamps'
    write_csv('all_english_reviews.csv',reviews);write_csv('developer_announcements.csv',notes)
    sensitivity=[]
    for appid in [None,*sorted({r['appid'] for r in reviews})]:
        population=[r for r in reviews if appid is None or r['appid']==appid]
        for threshold in [1,5,10,20]:
            kept=[r for r in population if r['word_count']>=threshold]
            sensitivity.append({'game':'All games' if appid is None else population[0]['game'],'minimum_words':threshold,
                'raw_reviews':len(population),'retained':len(kept),'retention_share':len(kept)/len(population),
                'negative_retained':sum(not r['recommended'] for r in kept),
                'negative_share_retained':sum(not r['recommended'] for r in kept)/len(kept) if kept else None,
                'raw_negative_share':sum(not r['recommended'] for r in population)/len(population)})
    change_items=[]
    for n in notes:
        if not n['patch_candidate'] and n['verification_status']!='manually_verified_patch':continue
        context=''; section=''; idx=0; pending_bullet=False
        for raw in n['text'].splitlines():
            line=raw.strip()
            if line in ['-','*']:pending_bullet=True;continue
            if not line or line.startswith('{STEAM_'):continue
            is_bullet=pending_bullet or line.startswith('-');pending_bullet=False
            if not is_bullet and len(line)<100:
                section=line
                if re.search(r'\b(?:AR/|LAS-|G/|Orbital|Trident|One-Two)\b',line):context=line
            if not re.search(r'\b(?:fixed|fixes|added|removed|increased|decreased|reduced|improved|changed|adjusted|no longer)\b',line,re.I):continue
            if len(line)<22:continue
            idx+=1;m=re.search(r'\bfrom\s+([\d.]+)\s+to\s+([\d.]+)',line,re.I)
            change_items.append(dict(appid=n['appid'],game=n['game'],gid=n['gid'],item_id=f"{n['gid']}:{idx}",title=n['title'],date_utc=n['date_utc'],timestamp=n['timestamp'],
                section=section,entity_hint=context,change_text=line.lstrip('- ').strip(),old_value=m.group(1) if m else '',new_value=m.group(2) if m else '',
                extraction='rule_candidate_needs_review',verification_status=n['verification_status'],source_url=n['source_url']))
    summaries=[];cohorts=[];daily=[];examples=[];windows=[]
    for appid in sorted({r['appid'] for r in reviews}):
        rs=[r for r in reviews if r['appid']==appid];ns=[n for n in notes if n['appid']==appid];neg=[r for r in rs if not r['recommended']]
        un=[r for r in rs if r['unedited']];times=[r['timestamp_created'] for r in rs]
        summary=dict(appid=appid,game=rs[0]['game'],reviews=len(rs),negative=len(neg),negative_share=len(neg)/len(rs),
            oldest_utc=iso(min(times)),newest_utc=iso(max(times)),announcements=len(ns),patch_candidates=sum(n['patch_candidate'] for n in ns),
            manually_verified_patches=sum(n['verification_status']=='manually_verified_patch' for n in ns),
            unedited=len(un),edited=len(rs)-len(un),steam_deck=sum(r['primarily_steam_deck'] is True for r in rs),
            short_reviews=sum(r['word_count']<=5 for r in rs),update_mentions=sum(r['mentions_update'] for r in rs),
            negative_update_mentions=sum(r['mentions_update'] for r in neg),negative_stability_mentions=sum(r['mentions_stability'] for r in neg),
            version_mentions=sum(r['mentions_version'] for r in rs))
        summary.update(text_eligible=sum(r['text_eligible'] for r in rs),eligible_unedited=sum(r['text_eligible'] and r['unedited'] for r in rs))
        summaries.append(summary)
        for label,predicate in [('Newcomer (<10h)',lambda r:r['playtime_at_review_hours'] is not None and r['playtime_at_review_hours']<10),
                                ('Veteran (>=100h)',lambda r:r['playtime_at_review_hours'] is not None and r['playtime_at_review_hours']>=100),
                                ('Primarily Steam Deck',lambda r:r['primarily_steam_deck'] is True),
                                ('Not primarily Steam Deck',lambda r:r['primarily_steam_deck'] is False)]:
            group=[r for r in un if predicate(r)];k=sum(not r['recommended'] for r in group);low,high=wilson(k,len(group))
            cohorts.append(dict(appid=appid,game=rs[0]['game'],cohort=label,population='unedited_reviews_only',reviews=len(group),negative=k,negative_share=k/len(group) if group else None,wilson_95_low=low,wilson_95_high=high))
        byday=defaultdict(list)
        for r in rs:byday[r['created_utc'][:10]].append(r)
        for day,group in sorted(byday.items()):
            k=sum(not r['recommended'] for r in group)
            daily.append(dict(appid=appid,game=rs[0]['game'],date_utc=day,reviews=len(group),negative=k,negative_share=k/len(group),partial_boundary_day=day in {iso(min(times))[:10],iso(max(times))[:10]}))
        for n in ns:
            if n['verification_status']!='manually_verified_patch':continue
            t=n['timestamp'];before=[r for r in un if t-7*86400<=r['timestamp_created']<t];after=[r for r in un if t<=r['timestamp_created']<t+7*86400]
            complete=min(times)<=t-7*86400 and max(times)>=t+7*86400
            windows.append(dict(game=rs[0]['game'],gid=n['gid'],title=n['title'],date_utc=n['date_utc'],complete_7day_windows=complete,
                before_n=len(before),before_negative=sum(not r['recommended'] for r in before),before_negative_share=sum(not r['recommended'] for r in before)/len(before) if before else None,
                after_n=len(after),after_negative=sum(not r['recommended'] for r in after),after_negative_share=sum(not r['recommended'] for r in after)/len(after) if after else None,source_url=n['source_url']))
        interesting=sorted([r for r in neg if r['unedited'] and (r['mentions_update'] or r['mentions_stability']) and 6<=r['word_count']<=180],key=lambda r:(not r['mentions_version'],-r['timestamp_created']))
        for r in interesting[:12]:
            prior=[n for n in ns if n['patch_candidate'] and n['timestamp']<=r['timestamp_created'] and r['timestamp_created']-n['timestamp']<=90*86400]
            rt=set(tokens(r['review_text']))
            scored=[]
            for n in prior:
                nt=set(tokens(n['text']));overlap=sorted(rt&nt);score=len(overlap)/math.sqrt(max(1,len(rt)*len(nt)))
                scored.append((score,n,overlap))
            scored.sort(key=lambda x:x[0],reverse=True)
            examples.append({**r,'candidates':[dict(gid=n['gid'],title=n['title'],date_utc=n['date_utc'],word_overlap_score=round(score,4),shared_words=overlap,source_url=n['source_url'],verification_status=n['verification_status']) for score,n,overlap in scored[:3]],
                'attribution_status':'unlabelled; lexical retrieval only'})
    dup=defaultdict(list)
    for c in change_items:dup[(c['appid'],re.sub(r'\W+',' ',c['change_text'].lower()).strip())].append(c)
    repeated=[{'game':group[0]['game'],'change_text':group[0]['change_text'],'posts':[{'gid':x['gid'],'title':x['title'],'date_utc':x['date_utc'],'verification_status':x['verification_status']} for x in group]} for group in dup.values() if len({x['gid'] for x in group})>1 and len(group[0]['change_text'])>40]
    result={'snapshot':SNAPSHOT.name,'total_raw_downloaded':len(raw_all),'excluded_language_reviews':len(excluded_language),'games':summaries,'total_reviews':len(reviews),'total_announcements':len(notes),'total_change_candidates':len(change_items),
        'total_edited':sum(not r['unedited'] for r in reviews),'total_short':sum(r['word_count']<=5 for r in reviews),'total_version_mentions':sum(r['mentions_version'] for r in reviews),
        'minimum_words':MIN_WORDS,'eligible_reviews':sum(r['text_eligible'] for r in reviews),
        'eligible_unedited_reviews':sum(r['text_eligible'] and r['unedited'] for r in reviews),'length_sensitivity':sensitivity,
        'negative_topic_keyword_counts':{name:sum((not r['recommended']) and r[f'mentions_{name}'] for r in reviews) for name in PATTERNS},
        'patch_windows':windows,'repeated_change_wording':repeated,'cohorts':cohorts,
        'limitations':['Convenience sample of newest English reviews, not random or representative. Equal per-game caps cover different time periods.',
                       'Keyword flags overlap and are not validated topic labels. Numeric/version mentions may be playtime or unrelated numbers.',
                       'Only explicitly marked posts were manually inspected. Other patch and change-item candidates need review.',
                       'No supported-link labels, causal claims, model evaluation or unsupported-link rate can be established from this pilot.',
                       'Steam Deck false does not identify desktop hardware. Cohort thresholds are exploratory and arbitrary.',
                       'Overlapping patches and incomplete time windows preclude isolated update effects.']}
    (OUT/'analysis.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:result[k] for k in ['games','total_reviews','total_announcements','total_change_candidates','total_edited','total_short','total_version_mentions','negative_topic_keyword_counts','patch_windows']},ensure_ascii=False,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--min-words',type=int,default=10)
    parser.add_argument('--snapshot',default='raw/steam_30_games')
    parser.add_argument('--output-dir',default='data/processed/steam_30_games')
    args=parser.parse_args()
    if args.min_words<1:parser.error('--min-words must be positive')
    MIN_WORDS=args.min_words;SNAPSHOT=ROOT/'data'/args.snapshot;OUT=ROOT/args.output_dir
    run()
