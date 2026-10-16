"""Render the supplied FigureSpec-style JSON diagrams to editable SVG and PDF.

Local fallback: the installed figure-spec skill has no figure_renderer.py.
Uses only matplotlib; fixed positions and bundled DejaVu Sans keep layout stable.
"""
from pathlib import Path
import json
import math
import textwrap
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = Path(__file__).resolve().parent
plt.rcParams.update({'font.family': 'DejaVu Sans', 'svg.fonttype': 'none',
                     'svg.hashsalt': 'steam-architecture-v1', 'pdf.fonttype': 42})

def render(spec, name):
    nodes = {n['id']: n for n in spec['nodes']}
    assert len(nodes) == len(spec['nodes']), 'duplicate IDs'
    for edge in spec['edges']:
        assert edge['from'] in nodes and edge['to'] in nodes
    for a in nodes.values():
        for b in nodes.values():
            if a['id'] < b['id']:
                assert abs(a['x']-b['x']) >= (a['width']+b['width'])/2 or abs(a['y']-b['y']) >= (a['height']+b['height'])/2, 'overlap'
    w,h=spec['canvas']['width'],spec['canvas']['height']
    fig,ax=plt.subplots(figsize=(w/100,h/100))
    ax.set(xlim=(0,w),ylim=(h,0));ax.axis('off');fig.subplots_adjust(0,0,1,1)
    fitted_text = []
    for label in spec.get('labels',[]):
        caption = '\n'.join(textwrap.wrap(label['text'], width=112))
        item = ax.text(label['x'],label['y'],caption,fontsize=label.get('font_size',12),color='#53677A',ha='center',va='center',weight=label.get('weight','normal'))
        fitted_text.append((item, w-32, 50))
    for n in nodes.values():
        x,y,bw,bh=n['x'],n['y'],n['width'],n['height']
        patch=FancyBboxPatch((x-bw/2,y-bh/2),bw,bh,boxstyle='round,pad=0,rounding_size=9',facecolor=n.get('fill','#EAF3F8'),edgecolor=n.get('stroke','#184A64'),linewidth=1.3)
        ax.add_patch(patch)
        label = '\n'.join('\n'.join(textwrap.wrap(line,width=28,break_long_words=False)) for line in n['label'].split('\n'))
        item = ax.text(x,y,label,fontsize=n.get('font_size',12),ha='center',va='center',color='#122B3C',linespacing=1.35)
        fitted_text.append((item, bw-20, bh-16))
    for e in spec['edges']:
        a,b=nodes[e['from']],nodes[e['to']]
        dx,dy=b['x']-a['x'],b['y']-a['y']
        def boundary(n,s):
            scale=min((n['width']/2)/abs(dx) if dx else math.inf,(n['height']/2)/abs(dy) if dy else math.inf)
            return (n['x']+s*dx*scale,n['y']+s*dy*scale)
        start,end=boundary(a,1),boundary(b,-1)
        ax.add_patch(FancyArrowPatch(start,end,arrowstyle='-|>',mutation_scale=14,linewidth=1.4,color='#44738A',linestyle='--' if e.get('style')=='dashed' else '-',connectionstyle=f"arc3,rad={e.get('curve',0)}",shrinkA=5,shrinkB=5))
        if e.get('label'):
            ax.text((start[0]+end[0])/2+e.get('label_dx',0),(start[1]+end[1])/2+e.get('label_dy',-12),e['label'],fontsize=9,ha='center',color='#53677A',bbox={'facecolor':'white','edgecolor':'none','pad':2})
    # Measure actual font extents rather than assuming a fixed character width.
    for _ in range(8):
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        changed = False
        for item, max_w, max_h in fitted_text:
            bounds = item.get_window_extent(renderer)
            scale = min(max_w/bounds.width, max_h/bounds.height, 1)
            if scale < 0.995:
                item.set_fontsize(item.get_fontsize()*scale*0.985)
                changed = True
        if not changed:
            break
    fig.canvas.draw()
    for item, max_w, max_h in fitted_text:
        bounds = item.get_window_extent(fig.canvas.get_renderer())
        assert bounds.width <= max_w+1 and bounds.height <= max_h+1, 'label overflow'
    out=ROOT/'figures';out.mkdir(exist_ok=True)
    for ext in ['svg','pdf']:
        fig.savefig(out/f'{name}.{ext}',metadata={'Date':None} if ext=='svg' else {'CreationDate':None,'ModDate':None})
    plt.close(fig)

def node(i,label,x,y,fill='#EAF3F8',width=205,height=78):
    return dict(id=i,label=label,x=x,y=y,width=width,height=height,fill=fill)
def edge(a,b,label='',**kw):return dict(**{'from':a,'to':b,'label':label},**kw)

def specifications():
    yield 'system',dict(canvas={'width':1040,'height':630},nodes=[
        node('steam','Steam APIs\nCatalog / reviews / news',125,95),
        node('ingest','Connector + worker\nRate budget / checkpoints',390,95),
        node('raw','Source archive\nSanitized, versioned JSON',650,95),
        node('parse','Normalize + parse\nReview spans / patch claims',910,95),
        node('models','Inference pipeline\nRetrieve / link / polarity / status',910,300),
        node('db','Postgres + pgvector\nEvidence + report snapshots',650,300),
        node('api','FastAPI\nJobs + cached report reads',390,300),
        node('ui','Streamlit\nGame / patch / evidence',125,300),
        node('dvc','DVC snapshots\nOffline training inputs',260,500,'#FFF3DC'),
        node('mlflow','Training + evaluation\nMLflow runs and registry',555,500,'#FFF3DC'),
        node('release','Release manifest\nPinned model bundle',850,500,'#FFF3DC')],edges=[
        edge('steam','ingest'),edge('ingest','raw'),edge('raw','parse'),edge('parse','models'),edge('models','db'),edge('db','api'),edge('api','ui'),edge('api','ingest','enqueue',label_dx=35,label_dy=0),
        edge('dvc','mlflow'),edge('mlflow','release'),edge('release','models','load',style='dashed',label_dx=40,label_dy=0)],labels=[{'x':520,'y':20,'text':'RUNTIME: one codebase, API and durable worker processes','font_size':15,'weight':'bold'},{'x':520,'y':590,'text':'OFFLINE LIFECYCLE: snapshots are cut from the source archive; serving never trains models','font_size':12}])
    yield 'analysis',dict(canvas={'width':1040,'height':615},nodes=[
        node('patch','Patch post\nTitle + headings + branch',140,90,width=230),
        node('claims','Atomic change claims\nExact spans + release scope',450,90,width=230),
        node('window','Eligible review window\nCoverage + edit handling',850,90,width=260),
        node('retrieval','Hybrid retrieval\nBM25 + MiniLM; game filter',140,290,width=230),
        node('link','Link + evidence checks\nSame change? Ambiguous?',450,290,width=230),
        node('polarity','Change-targeted polarity\nPositive / negative / mixed',850,290,width=260),
        node('status','Developer fix status\nProposal ladder + scope',140,510,'#FFF3DC',230),
        node('aggregate','Aggregate unique reviews\nCounts / coverage / uncertainty',450,510,'#FFF3DC',230),
        node('report','Cited patch report\nLiked / disliked / insufficient',850,510,'#FFF3DC',260)],edges=[
        edge('patch','claims'),edge('claims','window','release time'),edge('claims','link'),edge('window','polarity'),edge('retrieval','link'),edge('link','polarity'),edge('patch','retrieval'),edge('retrieval','status'),edge('polarity','aggregate'),edge('status','aggregate'),edge('link','aggregate'),edge('aggregate','report')],labels=[{'x':520,'y':20,'text':'TWO QUESTIONS: what players say, and what developers announce','font_size':15,'weight':'bold'},{'x':520,'y':590,'text':'Retrieval searches eligible review spans for each claim; fix-check mode reverses retrieval to announcement passages.','font_size':11}])
    yield 'lifecycle',dict(canvas={'width':1040,'height':580},nodes=[
        node('snapshot','Approved data snapshot\nDVC + split manifest',130,100,width=225),
        node('train','Reproduce + train\nLocked environment',390,100,width=215),
        node('eval','Evaluate candidate\nQuality + latency gates',650,100,width=215),
        node('registry','MLflow registry\nImmutable model versions',910,100,width=220),
        node('code','Pull request\nTests / schema / security',130,310),
        node('image','Build once\nImage digest + SBOM',390,310),
        node('stage','Staging release\nPinned bundle + smoke tests',650,310),
        node('prod','Production rollout\nHealth checks + rollback',910,310),
        node('monitor','Operations + human labels\nDrift triage; proposed retraining',520,475,'#FFF3DC',390,65)],edges=[
        edge('snapshot','train'),edge('train','eval'),edge('eval','registry'),edge('code','image'),edge('image','stage'),edge('stage','prod'),edge('registry','stage','release manifest',label_dx=40,label_dy=0),edge('prod','monitor',style='dashed')],labels=[{'x':520,'y':20,'text':'CI/CD RELEASES SOFTWARE; TRAINING PROPOSES MODELS','font_size':15,'weight':'bold'},{'x':520,'y':550,'text':'Feedback is reviewed before a new snapshot; drift never promotes a model automatically.'}])

if __name__=='__main__':
    for name,spec in specifications():
        (ROOT/'figures/specs'/f'{name}.json').write_text(json.dumps(spec,indent=2))
        render(spec,name)
        print('Validated and rendered',name)
