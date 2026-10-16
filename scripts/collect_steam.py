# Downloads Steam reviews and announcements and resumes interrupted runs.

import argparse
from contextlib import AbstractContextManager
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import hashlib
import html
import json
import os
from pathlib import Path
import random
import re
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
GAMES={553850:'HELLDIVERS 2',730:'Counter-Strike 2',275850:"No Man's Sky",548430:'Deep Rock Galactic',108600:'Project Zomboid'}
FILTER_VERSION='unicode_word_runs_v1'
def utc():return datetime.now(timezone.utc).isoformat()
def game_folder_name(game,appid):
    slug=re.sub(r'[^A-Za-z0-9]+','_',game).strip('_')
    return f'{slug}_{appid}'
def word_count(text):return len(re.findall(r'\b\w+\b',text,re.UNICODE))
def eligible(row,minimum):return row.get('language')=='english' and word_count(row.get('review',''))>=minimum
def read_json(path,default):return json.loads(path.read_text(encoding='utf-8')) if path.exists() else default

def dump(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_name(path.name+f'.{os.getpid()}.tmp')
    try:
        with tmp.open('w',encoding='utf-8') as f:
            json.dump(value,f,ensure_ascii=False,indent=2);f.flush();os.fsync(f.fileno())
        os.replace(tmp,path)
    finally:tmp.unlink(missing_ok=True)

def load_reviews(path):

    if not path.exists():return []
    rows=[]
    with path.open('r+b') as f:
        while True:
            offset=f.tell();line=f.readline()
            if not line:break
            try:row=json.loads(line.decode('utf-8'))
            except (json.JSONDecodeError,UnicodeDecodeError):
                if f.read(1):raise ValueError(f'Corrupt interior row at byte {offset} in {path}')
                f.truncate(offset);f.flush();os.fsync(f.fileno());print('Recovered interrupted final row',flush=True);break
            rows.append(row)
            if not line.endswith(b'\n'):
                f.seek(0,2);f.write(b'\n');f.flush();os.fsync(f.fileno())
    if len({str(r['recommendationid']) for r in rows})!=len(rows):raise ValueError(f'Duplicate saved IDs in {path}')
    return rows

def append_rows(path,rows):
    with path.open('a',encoding='utf-8') as f:
        for row in rows:f.write(json.dumps(row,ensure_ascii=False)+'\n')
        f.flush();os.fsync(f.fileno())

def export_subsets(folder,rows,minimum):
    for name,kind in [('reviews_eligible.jsonl','eligible'),('reviews_short.jsonl','short'),('reviews_excluded_language.jsonl','language')]:
        target=folder/name;tmp=target.with_name(target.name+f'.{os.getpid()}.tmp')
        try:
            with tmp.open('w',encoding='utf-8') as f:
                for row in rows:
                    keep=eligible(row,minimum) if kind=='eligible' else row.get('language')=='english' and not eligible(row,minimum) if kind=='short' else row.get('language')!='english'
                    if keep:f.write(json.dumps({**row,'word_count':word_count(row['review']),'text_eligible':eligible(row,minimum)},ensure_ascii=False)+'\n')
                f.flush();os.fsync(f.fileno())
            os.replace(tmp,target)
        finally:tmp.unlink(missing_ok=True)
    dump(folder/'filter_summary.json',{'min_words':minimum,'word_count_method':FILTER_VERSION,'raw_reviews':len(rows),
         'eligible_reviews':sum(eligible(r,minimum) for r in rows),'short_reviews':sum(r.get('language')=='english' and not eligible(r,minimum) for r in rows),
         'excluded_language_reviews':sum(r.get('language')!='english' for r in rows),
         'meaning':'Text-length subset, not validity or supported attribution. All rows retained in reviews.jsonl.','updated_utc':utc()})

def clean_text(text):
    text=re.sub(r'\[/?(?:list|olist|h[1-6]|p|quote|b|i|u|strike|table|tr|td|th)[^\]]*\]','\n',text,flags=re.I)
    text=re.sub(r'\[\*\]','\n- ',text);text=re.sub(r'\[(img|previewyoutube)[^\]]*\].*?\[/\1\]','',text,flags=re.I|re.S)
    text=re.sub(r'\[/?[^\]]+\]','',text);text=re.sub(r'<[^>]+>',' ',text)
    return re.sub(r'\n[ \t]*\n+','\n\n',html.unescape(text)).strip()

def retry_after_seconds(value,now):
    if not value:return None
    try:return max(0,float(value))
    except ValueError:
        try:return max(0,parsedate_to_datetime(value).timestamp()-now)
        except (ValueError,TypeError,OverflowError):return None

class Client:
    def __init__(self,state_path,interval=3,initial_wait=60,maximum_wait=900,max_rate_retries=0,opener=None,clock=None,sleeper=None):
        self.path=Path(state_path);self.state=read_json(self.path,{})
        self.calls=0;self.last=-float('inf');self.interval=interval;self.initial_wait=initial_wait
        self.maximum_wait=maximum_wait;self.max_rate_retries=max_rate_retries
        self.opener=opener or urllib.request.urlopen;self.clock=clock or time.time;self.sleeper=sleeper or time.sleep
    def wait_until(self,deadline,reason):
        while deadline>self.clock():
            remaining=deadline-self.clock();print(f'{reason}: {remaining:.0f}s remaining; resumes at {datetime.fromtimestamp(deadline,timezone.utc).isoformat()}',flush=True)
            self.sleeper(min(30,remaining))
    def get(self,base,params):
        url=base+'?'+urllib.parse.urlencode(params);host=urllib.parse.urlparse(base).netloc;transient=0;rate_retries=0
        while True:
            bucket=self.state.get(host,{})
            self.wait_until(bucket.get('blocked_until',0),f'Cooldown for {host}')
            self.sleeper(max(0,self.interval-(self.clock()-self.last)));self.last=self.clock();self.calls+=1
            try:
                req=urllib.request.Request(url,headers={'User-Agent':'ENSF621-public-research/2.0'})
                with self.opener(req,timeout=35) as response:payload=json.load(response)
                if host in self.state:self.state.pop(host);dump(self.path,self.state)
                return payload,url
            except urllib.error.HTTPError as exc:
                if exc.code==429:
                    rate_retries+=1;streak=bucket.get('streak',0)+1;delay=retry_after_seconds(exc.headers.get('Retry-After'),self.clock())
                    if delay is None:
                        delay=min(self.maximum_wait,self.initial_wait*2**min(streak-1,20));delay=min(self.maximum_wait,delay+random.uniform(0,min(5,delay*.1)))
                    delay=max(self.interval,1,delay)
                    self.state[host]={'blocked_until':self.clock()+delay,'streak':streak,'status':429,'saved_utc':utc()};dump(self.path,self.state)
                    print(f'HTTP 429 on {host}; saved cooldown; retrying SAME page in {delay:.0f}s.',flush=True)
                    if self.max_rate_retries and rate_retries>=self.max_rate_retries:raise
                    continue
                if exc.code not in {408,425,500,502,503,504}:raise
                transient+=1
                if transient>=5:raise
                self.wait_until(self.clock()+min(60,2**transient),f'HTTP {exc.code} retry')
            except (urllib.error.URLError,TimeoutError,json.JSONDecodeError) as exc:
                transient+=1
                if transient>=5:raise
                self.wait_until(self.clock()+min(60,2**transient),f'{type(exc).__name__} retry')

class SnapshotLock(AbstractContextManager):
    def __init__(self,path):self.path=path;self.handle=None
    def __enter__(self):
        self.handle=self.path.open('a+b');self.handle.seek(0)
        if self.path.stat().st_size==0:self.handle.write(b'0');self.handle.flush();self.handle.seek(0)
        try:
            if os.name=='nt':
                import msvcrt
                msvcrt.locking(self.handle.fileno(),msvcrt.LK_NBLCK,1)
            else:
                import fcntl
                fcntl.flock(self.handle.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
        except OSError:
            self.handle.close();raise RuntimeError('Another collector is using this snapshot. Stop it or wait for completion.')
        return self
    def __exit__(self,*args):
        self.handle.seek(0)
        if os.name=='nt':
            import msvcrt
            msvcrt.locking(self.handle.fileno(),msvcrt.LK_UNLCK,1)
        self.handle.close()

def collect_game(client,folder,appid,game,salt,args):
    folder.mkdir(exist_ok=True);path=folder/'reviews.jsonl';rows=load_reviews(path)
    seen={str(r['recommendationid']) for r in rows};state=read_json(folder/'review_state.json',{'cursor':'*'})
    saved_api=state.get('review_api','legacy' if rows else 'modern');api=saved_api if args.review_api=='auto' else args.review_api
    if rows and api!=saved_api:raise ValueError('Cannot change API for a saved cursor. Use --review-api auto or a new snapshot.')
    count=sum(eligible(r,args.min_words) for r in rows);cursor=state['cursor'];exhausted=state.get('exhausted',False)
    print(f'{game}: resumed {len(rows):,} raw / {count:,} >= {args.min_words} words; target {args.reviews_per_game:,}',flush=True)
    def checkpoint():
        state.update(cursor=cursor,rows=len(rows),eligible_rows=count,min_words=args.min_words,review_api=api,exhausted=exhausted,updated_utc=utc(),word_count_method=FILTER_VERSION)
        dump(folder/'review_state.json',state)
    try:
        while count<args.reviews_per_game and len(rows)<args.max_raw_per_game and not exhausted:
            size=min(100,args.max_raw_per_game-len(rows))
            if api=='modern':
                request={'appid':appid,'filter':1,'languages':['english'],'purchase_type':1,'review_type':0,'num_per_page':size,'cursor':cursor,'filter_offtopic_activity':False}
                payload,url=client.get('https://api.steampowered.com/IUserReviewsService/GetAppReviews/v1/',{'input_json':json.dumps(request)})
                payload=payload.get('response',{})
                if 'reviews' not in payload:raise ValueError('Missing reviews in API response')
            else:
                payload,url=client.get(f'https://store.steampowered.com/appreviews/{appid}',{'json':1,'language':'english','filter':'recent','num_per_page':size,'purchase_type':'all','cursor':cursor,'filter_offtopic_activity':0})
                if payload.get('success')!=1:raise ValueError('Review endpoint failure')
            state['query_summary']=state.get('query_summary') or payload.get('query_summary');batch=payload.get('reviews',[]);fresh=[]
            for original in batch:
                key=str(original['recommendationid'])
                if key in seen:continue
                r=dict(original);author=r.get('author',{})
                r['author']={k:v for k,v in author.items() if k in {'num_games_owned','num_reviews','playtime_forever','playtime_last_two_weeks','playtime_at_review','deck_playtime_at_review','last_played'}}
                r['author']['author_hash']=hashlib.sha256(salt+str(author.get('steamid','')).encode()).hexdigest()
                r.update(appid=appid,game=game,source_url=url.split('?')[0],fetched_utc=utc());fresh.append(r);seen.add(key)


            append_rows(path,fresh);rows.extend(fresh);count+=sum(eligible(r,args.min_words) for r in fresh)
            next_cursor=payload.get('cursor',cursor);exhausted=not batch
            if batch and next_cursor==cursor:raise RuntimeError('Nonempty review page did not advance; rows saved, cursor unchanged.')
            cursor=next_cursor;state['last_request_url']=url;checkpoint()
            print(f'{game}: {len(rows):,} raw / {count:,} eligible',flush=True)
        checkpoint()
    finally:export_subsets(folder,rows,args.min_words)
    news=read_json(folder/'news.json',[]);ns=read_json(folder/'news_state.json',{})
    enddate=ns.get('next_enddate',min((n['date'] for n in news),default=0)-1)
    while len(news)<args.news_per_game and not ns.get('done',False):
        params={'appid':appid,'count':min(100,args.news_per_game-len(news)),'maxlength':0,'feeds':'steam_community_announcements'}
        if enddate>0:params['enddate']=enddate
        payload,url=client.get('https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/',params)
        batch=payload.get('appnews',{}).get('newsitems',[]);ids={n['gid'] for n in news}
        for original in batch:
            if original['gid'] in ids or original['date']<args.cutoff:continue
            n=dict(original);n.update(appid=appid,game=game,text=clean_text(n.get('contents','')),fetched_utc=utc());news.append(n);ids.add(n['gid'])
        dump(folder/'news.json',news)
        ns['done']=not batch or min((n['date'] for n in batch),default=args.cutoff-1)<args.cutoff
        if batch:
            next_enddate=min(n['date'] for n in batch)-1
            if enddate>0 and next_enddate>=enddate:raise RuntimeError('News pagination did not advance')
            enddate=next_enddate
        ns.update(next_enddate=enddate,updated_utc=utc());dump(folder/'news_state.json',ns)
    if not (folder/'steamspy.json').exists():
        try:
            meta,url=client.get('https://steamspy.com/api.php',{'request':'appdetails','appid':appid});dump(folder/'steamspy.json',{'source_url':url,'fetched_utc':utc(),'data':meta})
        except Exception as exc:print(f'{game}: optional SteamSpy metadata unavailable: {exc}',flush=True)
    status='target_met' if count>=args.reviews_per_game else 'source_exhausted' if exhausted else 'raw_cap_reached'
    return {'appid':appid,'game':game,'raw_reviews':len(rows),'eligible_reviews':count,
            'short_reviews':sum(r.get('language')=='english' and not eligible(r,args.min_words) for r in rows),
            'excluded_language_reviews':sum(r.get('language')!='english' for r in rows),
            'announcements':len(news),'status':status,'review_api':api}

def collect(args):
    out=ROOT/'data'/args.snapshot;out.mkdir(parents=True,exist_ok=True)
    with SnapshotLock(out/'.collector.lock'):
        secret=ROOT/'.local'/'author_salt';secret.parent.mkdir(exist_ok=True)
        if not secret.exists():
            if any(out.glob('*/reviews.jsonl')):raise RuntimeError('Saved reviews exist but author salt is missing. Restore .local/author_salt before resuming.')
            secret.write_bytes(os.urandom(32))
        client=Client(out/'http_state.json',args.request_interval,args.rate_limit_wait,args.max_rate_limit_wait,args.max_rate_limit_retries)
        previous=read_json(out/'manifest.json',{})
        manifest={'snapshot':args.snapshot,'created_utc':previous.get('created_utc',previous.get('started_utc',utc())),
                  'run_started_utc':utc(),'min_words':args.min_words,'eligible_target_per_game':args.reviews_per_game,'max_raw_per_game':args.max_raw_per_game,
                  'news_target_per_game':args.news_per_game,'news_since':args.news_since,'request_interval_seconds':args.request_interval,'word_count_method':FILTER_VERSION,
                  'sampling':'Newest English reviews; all purchase types; off-topic activity included. All raw rows retained.',
                  'filter':'Text-length subset, not validity or attribution. Word counts before stop-word removal.',
                  'privacy':'Salted author hashes; profile names, avatars and URLs removed before persistence.','games':[],'failures':[],'status':'running'}
        dump(out/'manifest.json',manifest)
        catalog=read_json(out/'game_catalog.json',{})
        catalog.update({str(k):v for k,v in args.games.items() if not args.appids or k in args.appids})
        dump(out/'game_catalog.json',catalog)
        try:
            for appid,game in args.games.items():
                if args.appids and appid not in args.appids:continue
                try:manifest['games'].append(collect_game(client,out/game_folder_name(game,appid),appid,game,secret.read_bytes(),args))
                except Exception as exc:
                    manifest['failures'].append({'appid':appid,'game':game,'error':str(exc)});print(f'{game}: saved partial progress; {exc}',flush=True)
                dump(out/'manifest.json',manifest)
            manifest['status']='completed_with_failures' if manifest['failures'] else 'completed'
        except KeyboardInterrupt:
            manifest['status']='interrupted';print('Interrupted. Saved pages and cooldowns resume on rerun.',flush=True)
        finally:
            manifest.update(run_finished_utc=utc(),requests_this_run=client.calls);dump(out/'manifest.json',manifest);append_rows(out/'collection_runs.jsonl',[manifest])
        print(json.dumps(manifest,ensure_ascii=False,indent=2),flush=True)
        return 130 if manifest['status']=='interrupted' else 1 if manifest['failures'] else 0

def parse_args(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot',default='raw/steam_30_games')
    parser.add_argument('--review-api',choices=['auto','modern','legacy'],default='auto')
    parser.add_argument('--reviews-per-game',type=int,default=1000,help='Target number meeting --min-words; all raw rows retained')
    parser.add_argument('--min-words',type=int,default=10,help='Text-subset minimum before stop-word removal')
    parser.add_argument('--max-raw-per-game',type=int,default=10000,help='Bound pagination if eligible target cannot be reached')
    parser.add_argument('--news-per-game',type=int,default=300)
    parser.add_argument('--news-since',default='2024-10-09')
    parser.add_argument('--games-file',type=Path,default=ROOT/'data/games.json',help='JSON object mapping Steam app IDs to game names, for a larger game scope')
    parser.add_argument('--appids',nargs='+',type=int,help='Restrict this run to IDs in the selected game mapping')
    parser.add_argument('--request-interval',type=float,default=3)
    parser.add_argument('--rate-limit-wait',type=float,default=60,help='Fallback initial wait if Retry-After missing')
    parser.add_argument('--max-rate-limit-wait',type=float,default=900,help='Fallback cap; server Retry-After always honored')
    parser.add_argument('--max-rate-limit-retries',type=int,default=0,help='0 retries 429 indefinitely; nonzero stops safely after this many 429s')
    args=parser.parse_args(argv)
    if min(args.min_words,args.reviews_per_game,args.max_raw_per_game,args.news_per_game,args.rate_limit_wait,args.max_rate_limit_wait)<=0 or args.request_interval<0 or args.max_rate_limit_retries<0:parser.error('Targets/waits positive; interval and retry count nonnegative')
    if not args.snapshot or any(not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]*',part) or part in {'.','..'} for part in args.snapshot.split('/')):
        parser.error('Snapshot must be a safe relative path without directory traversal')
    args.games=dict(GAMES)
    if args.games_file:
        try:
            supplied=json.loads(args.games_file.read_text(encoding='utf-8'))
            if not isinstance(supplied,dict) or not supplied:raise ValueError('Expected a nonempty JSON object')
            args.games={int(key):name for key,name in supplied.items()}
            if any(key<=0 or not isinstance(name,str) or not name.strip() for key,name in args.games.items()):raise ValueError('App IDs must be positive and names nonempty strings')
        except (OSError,ValueError,TypeError) as exc:parser.error(f'Invalid --games-file: {exc}')
    if args.appids and set(args.appids)-set(args.games):parser.error('--appids must occur in the selected game mapping')
    args.cutoff=int(datetime.strptime(args.news_since,'%Y-%m-%d').replace(tzinfo=timezone.utc).timestamp())
    return args

if __name__=='__main__':raise SystemExit(collect(parse_args()))
