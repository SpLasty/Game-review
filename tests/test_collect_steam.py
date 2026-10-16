"""Fault-injection checks for rate limits and interruption-safe collection."""
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from scripts import collect_steam as c

class FakeTime:
    def __init__(self):self.now=1000;self.sleeps=[]
    def clock(self):return self.now
    def sleep(self,seconds):self.sleeps.append(seconds);self.now+=seconds

def row(key,text='one two three four five six seven eight nine ten'):
    return {'recommendationid':str(key),'review':text,'language':'english','author':{'steamid':'123','personaname':'remove me','profile_url':'remove me','avatar':'remove me'},'timestamp_created':100,'timestamp_updated':100,'voted_up':True}

class QueueClient:
    def __init__(self,pages):self.pages=list(pages);self.cursors=[]
    def get(self,base,params):
        self.cursors.append(params['cursor'])
        return self.pages.pop(0),base

class RecoveryTests(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
    def tearDown(self):self.tmp.cleanup()
    def fixture(self,minimum=10,target=2):
        folder=self.root/'730';folder.mkdir()
        c.dump(folder/'news.json',[]);c.dump(folder/'news_state.json',{'done':True});c.dump(folder/'steamspy.json',{})
        args=c.parse_args(['--review-api','legacy','--min-words',str(minimum),'--reviews-per-game',str(target)])
        return folder,args

    def test_429_honors_header_and_retries_same_url(self):
        clock=FakeTime();calls=[]
        def opener(req,timeout):
            calls.append((req.full_url,clock.now))
            if len(calls)==1:raise HTTPError(req.full_url,429,'limit',{'Retry-After':'75'},None)
            return io.StringIO('{"ok":1}')
        client=c.Client(self.root/'http.json',interval=0,opener=opener,clock=clock.clock,sleeper=clock.sleep)
        result,_=client.get('https://example.com/reviews',{'cursor':'same'})
        self.assertEqual(result,{'ok':1});self.assertEqual(calls[0][0],calls[1][0]);self.assertGreaterEqual(calls[1][1]-calls[0][1],75)
        self.assertTrue(all(s<=30 for s in clock.sleeps));self.assertEqual(c.read_json(self.root/'http.json',None),{})

    def test_restart_respects_persisted_cooldown(self):
        clock=FakeTime();path=self.root/'http.json'
        def limited(req,timeout):raise HTTPError(req.full_url,429,'limit',{'Retry-After':'100'},None)
        client=c.Client(path,interval=0,max_rate_retries=1,opener=limited,clock=clock.clock,sleeper=clock.sleep)
        with self.assertRaises(HTTPError):client.get('https://example.com/reviews',{})
        calls=[]
        def success(req,timeout):calls.append(clock.now);return io.StringIO('{}')
        restarted=c.Client(path,interval=0,opener=success,clock=clock.clock,sleeper=clock.sleep)
        restarted.get('https://example.com/reviews',{});self.assertGreaterEqual(calls[0],1100)

    def test_missing_header_exponential_backoff(self):
        clock=FakeTime();attempts=[]
        def opener(req,timeout):
            attempts.append(clock.now)
            if len(attempts)<3:raise HTTPError(req.full_url,429,'limit',{},None)
            return io.StringIO('{}')
        with patch.object(c.random,'uniform',return_value=0):
            c.Client(self.root/'http.json',interval=0,opener=opener,clock=clock.clock,sleeper=clock.sleep).get('https://example.com/r',{})
        self.assertEqual(attempts,[1000,1060,1180])

    def test_http_date_and_invalid_retry_after(self):
        self.assertEqual(c.retry_after_seconds('Thu, 01 Jan 1970 00:20:00 GMT',1000),200)
        self.assertIsNone(c.retry_after_seconds('bad',1000))

    def test_fatal_403_is_not_retried(self):
        def forbidden(req,timeout):raise HTTPError(req.full_url,403,'forbidden',{},None)
        client=c.Client(self.root/'http.json',opener=forbidden)
        with self.assertRaises(HTTPError):client.get('https://example.com/r',{})
        self.assertEqual(client.calls,1)

    def test_crash_after_row_write_replays_without_duplicates(self):
        folder,args=self.fixture(target=2);path=folder/'reviews.jsonl'
        c.dump(folder/'review_state.json',{'cursor':'*','review_api':'legacy'})
        pages=[{'success':1,'reviews':[row(1)],'cursor':'next'},{'success':1,'reviews':[row(2)],'cursor':'end'}]
        original=c.dump
        def failing(path,value):
            if Path(path).name=='review_state.json':raise OSError('simulated checkpoint failure after append')
            return original(path,value)
        with patch.object(c,'dump',side_effect=failing):
            with self.assertRaises(OSError):c.collect_game(QueueClient(pages),folder,730,'test',b'salt',args)
        self.assertEqual(len(c.load_reviews(path)),1)
        client=QueueClient(pages)
        result=c.collect_game(client,folder,730,'test',b'salt',args)
        self.assertEqual(client.cursors,['*','next']);self.assertEqual(result['eligible_reviews'],2)
        saved=c.load_reviews(path);self.assertEqual([r['recommendationid'] for r in saved],['1','2'])
        self.assertFalse({'steamid','personaname','profile_url','avatar'} & saved[0]['author'].keys())

    def test_rerun_larger_target_continues_saved_cursor(self):
        folder,args=self.fixture(target=1)
        client=QueueClient([{'success':1,'reviews':[row(1)],'cursor':'after-one'}])
        c.collect_game(client,folder,730,'test',b'salt',args)
        args.reviews_per_game=2
        next_client=QueueClient([{'success':1,'reviews':[row(2)],'cursor':'after-two'}])
        c.collect_game(next_client,folder,730,'test',b'salt',args)
        self.assertEqual(next_client.cursors,['after-one'])

    def test_filter_counts_target_while_preserving_short_rows(self):
        folder,args=self.fixture(target=1)
        client=QueueClient([{'success':1,'reviews':[row(1,'Update broke multiplayer')],'cursor':'a'},{'success':1,'reviews':[row(2)],'cursor':'b'}])
        result=c.collect_game(client,folder,730,'test',b'salt',args)
        self.assertEqual((result['raw_reviews'],result['eligible_reviews'],result['short_reviews']),(2,1,1))
        self.assertEqual(len(c.load_reviews(folder/'reviews_short.jsonl')),1)
        args.min_words=1
        result=c.collect_game(QueueClient([]),folder,730,'test',b'salt',args)
        self.assertEqual(result['eligible_reviews'],2)

    def test_truncated_final_record_recovery_and_interior_error(self):
        path=self.root/'reviews.jsonl';path.write_bytes(json.dumps(row(1)).encode()+b'\n{"review":')
        self.assertEqual(len(c.load_reviews(path)),1);self.assertTrue(path.read_bytes().endswith(b'\n'))
        path.write_bytes(b'{bad}\n'+json.dumps(row(2)).encode()+b'\n')
        before=path.read_bytes()
        with self.assertRaises(ValueError):c.load_reviews(path)
        self.assertEqual(before,path.read_bytes())

    def test_empty_page_marks_exhaustion(self):
        folder,args=self.fixture();client=QueueClient([{'success':1,'reviews':[],'cursor':'*'}])
        result=c.collect_game(client,folder,730,'test',b'salt',args)
        self.assertEqual(result['status'],'source_exhausted')
        c.collect_game(QueueClient([]),folder,730,'test',b'salt',args)

    def test_snapshot_lock_blocks_second_writer(self):
        with c.SnapshotLock(self.root/'lock'):
            with self.assertRaises(RuntimeError):
                with c.SnapshotLock(self.root/'lock'):pass

    def test_custom_game_scope_and_subset_validation(self):
        path=self.root/'games.json';c.dump(path,{'999':'Additional game'})
        args=c.parse_args(['--games-file',str(path),'--appids','999'])
        self.assertEqual(args.games,{999:'Additional game'})

    def test_language_mismatch_is_saved_but_not_eligible(self):
        foreign=row(1);foreign['language']='schinese'
        self.assertFalse(c.eligible(foreign,10))
        self.assertTrue(c.eligible(row(2),10))
        c.export_subsets(self.root,[foreign,row(2)],10)
        summary=c.read_json(self.root/'filter_summary.json',{})
        self.assertEqual((summary['raw_reviews'],summary['eligible_reviews'],summary['excluded_language_reviews']),(2,1,1))
        self.assertEqual(len((self.root/'reviews_excluded_language.jsonl').read_text(encoding='utf-8').splitlines()),1)

if __name__=='__main__':unittest.main()
