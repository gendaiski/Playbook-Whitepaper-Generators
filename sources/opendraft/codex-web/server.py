"""Local browser companion to the original OpenDraft CLI. No replacement engine."""
import argparse,base64,json,mimetypes,os,re,secrets,shutil,subprocess,sys,threading,time,uuid
from pathlib import Path
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from urllib.parse import urlparse,unquote
import cloud_access
ROOT=Path(__file__).resolve().parents[1]
DATA=Path(os.environ.get('OPENDRAFT_WORKSPACE',ROOT/'codex-web'/'workspace')).resolve()
DATA.mkdir(parents=True,exist_ok=True)
LOCK=threading.Lock();PROCESSES={};CANCELLED=set();TOKEN=secrets.token_urlsafe(32)
KEYS={'gemini':'GOOGLE_API_KEY','claude':'ANTHROPIC_API_KEY','openai':'OPENAI_API_KEY'}
SETTINGS=DATA/'settings.local.json'

def config():
 try:return json.loads(SETTINGS.read_text())
 except FileNotFoundError:return {'AI_PROVIDER':os.environ.get('AI_PROVIDER','gemini')}

def env():
 e=os.environ.copy();e.update(config());e['PYTHONUNBUFFERED']='1';e['PATH']=str(Path(sys.executable).parent)+os.pathsep+e.get('PATH','');return e

def key_ready(provider):
 e=env();return bool(e.get(KEYS[provider]) or (provider=='gemini' and e.get('GEMINI_API_KEY')))

def safe_file(rel):
 p=(DATA/rel).resolve()
 if not p.is_relative_to(DATA) or p.is_symlink() or not p.is_file() or any(x.startswith('.') for x in Path(rel).parts) or p.name=='settings.local.json':raise ValueError('File unavailable')
 parts=Path(rel).parts
 if not (parts[0]=='uploads' or (len(parts)>3 and parts[0]=='jobs' and parts[2]=='output')):raise ValueError('File unavailable')
 return p

def status():
 c=config();return {'version':'1.8.1','remote':cloud_access.enabled(),'provider':c.get('AI_PROVIDER','gemini'),'keys':{p:key_ready(p) for p in KEYS},'audio_key':bool(env().get('ELEVENLABS_API_KEY')),'original_interface':'Terminal CLI','companion':'Browser control panel','python':sys.version.split()[0]}

def redact(s):
 for k,v in env().items():
  if ('API_KEY' in k or 'TOKEN' in k) and v:
   s=s.replace(v,'[redacted]')
   if len(v)>12:s=s.replace(v[:8]+'...'+v[-4:],'[redacted]')
 return re.sub(r'\x1b\[[0-9;?]*[A-Za-z]','',s)

def read_job(jid):
 if not re.fullmatch('[a-f0-9]{32}',jid):raise ValueError('Unknown job')
 p=DATA/'jobs'/jid;d=json.loads((p/'job.json').read_text());log=p/'run.log'
 d['log']=redact(log.read_text(errors='replace')[-100000:]) if log.exists() else ''
 d['files']=[{'name':str(f.relative_to(p/'output')),'path':str(f.relative_to(DATA)),'bytes':f.stat().st_size} for f in sorted((p/'output').rglob('*')) if f.is_file()]
 return d

def save_job(p,d):
 tmp=p/'job.tmp';tmp.write_text(json.dumps(d,indent=2));tmp.replace(p/'job.json')

def command(request,out):
 mode=request.get('mode','generate');cli=[sys.executable,'-m','opendraft.cli'];c=config();provider=c.get('AI_PROVIDER','gemini')
 if mode in ['generate','resume','revise','tldr','digest']:
  needed='gemini' if mode in ['revise','tldr','digest'] else provider
  if not key_ready(needed):raise ValueError(f'Configure a {needed} API key in Settings first. No AI task was started.')
 if mode=='generate':
  topic=str(request.get('topic','')).strip()
  if not topic or len(topic)>4000 or topic.startswith('-'):raise ValueError('Enter a research topic (up to 4000 characters).')
  level=request.get('level','research_paper');style=request.get('style','apa')
  if level not in ['research_paper','bachelor','master','phd'] or style not in ['apa','ieee','chicago','mla','nalt']:raise ValueError('Invalid level or citation style')
  args=cli+[topic,'--level',level,'--style',style,'--lang',str(request.get('lang','en')),'--output',str(out)]
  for k in ['author','institution','department','advisor','blurb']:
   if request.get(k):args+=['--'+k,str(request[k])]
  for s in request.get('sources',[]):args+=['--source',str(s)]
  for f in request.get('context_files',[]):args+=['--context-file',str(safe_file(f))]
  if request.get('expose'):args+=['--expose']
  return args
 if mode in ['tldr','digest','revise','export']:
  f=safe_file(str(request.get('file','')))
  if mode=='tldr':return cli+['tldr',str(f),'--output',str(out/'summary.md')]
  if mode=='digest':
   args=cli+['digest',str(f),'--output',str(out),'--voice',request.get('voice','rachel')]
   if not request.get('audio'):args+=['--no-audio']
   elif not env().get('ELEVENLABS_API_KEY'):raise ValueError('Audio requires an ElevenLabs key; choose script-only otherwise.')
   return args
  if mode=='revise':
   instructions=str(request.get('instructions','')).strip()
   if not instructions:raise ValueError('Enter revision instructions')
   target=out/f.name;shutil.copy2(f,target)
   return cli+['revise',str(target),instructions]
  if f.suffix.lower() not in ['.md','.txt']:raise ValueError('Export accepts Markdown or text')
  target=out/'draft.md';shutil.copy2(f,target)
  return [sys.executable,str(ROOT/'codex-web'/'export.py'),str(target),str(out)]
 if mode=='resume':
  f=safe_file(str(request.get('file','')))
  if f.name!='checkpoint.json':raise ValueError('Choose checkpoint.json from an earlier job')
  # Preserve sibling state and resume a copy, retaining the old run.
  shutil.copytree(f.parent,out,dirs_exist_ok=True)
  return cli+[str(request.get('topic') or 'Resume saved draft'),'--resume',str(out/'checkpoint.json'),'--output',str(out)]
 if mode=='data':
  provider=request.get('data_provider','list')
  if provider not in ['list','search','worldbank','eurostat','owid']:raise ValueError('Invalid data provider')
  args=cli+['data',provider]
  if request.get('query'):args.append(str(request['query']))
  args+=['--output',str(out)]
  if request.get('countries'):args+=['--countries',str(request['countries'])]
  return args
 if mode=='verify':return cli+['verify']
 if mode=='help':return cli+['--help']
 if mode=='sample':
  sample=ROOT/'examples'/'Why_Academic_Thesis_AI_Saves_The_World.pdf'
  shutil.copy2(sample,out/sample.name)
  (out/'README.txt').write_text('This is the original upstream sample PDF, not a new AI-generated result.\n')
  return [sys.executable,'-c',"print('Original upstream sample copied. No model called.')"]
 raise ValueError('Unknown action')

def launch(req):
 with LOCK:
  if any(p.poll() is None for p in PROCESSES.values()):raise ValueError('A task is running. Wait or cancel it before starting another.')
  jid=uuid.uuid4().hex;p=DATA/'jobs'/jid;out=p/'output';out.mkdir(parents=True)
  try:args=command(req,out)
  except Exception:shutil.rmtree(p);raise
  d={'id':jid,'mode':req.get('mode','generate'),'topic':str(req.get('topic',''))[:200],'status':'running','started':time.time(),'exit_code':None}
  log=open(p/'run.log','w');proc=subprocess.Popen(args,cwd=ROOT/'engine',env=env(),stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=(os.name!='nt'))
  PROCESSES[jid]=proc;save_job(p,d)
 def finish():
  rc=proc.wait();log.close()
  with LOCK:
   d['status']='cancelled' if jid in CANCELLED else ('completed' if rc==0 else 'failed');d['exit_code']=rc;d['finished']=time.time();save_job(p,d)
 threading.Thread(target=finish,daemon=True).start()
 return {'id':jid}

class Handler(BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def reply(self,data,status=200,kind='application/json'):
  b=json.dumps(data).encode() if kind=='application/json' else data
  self.send_response(status);self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(b)));self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.end_headers();self.wfile.write(b)
 def allowed(self):
  return self.headers.get('Host','') in [f'127.0.0.1:{self.server.server_port}',f'localhost:{self.server.server_port}']
 def do_GET(self):
  if not self.allowed():return self.reply({'error':'Local access only'},403)
  path=unquote(urlparse(self.path).path)
  if path=='/health':return self.reply({'ok':True})
  if not cloud_access.authorized(self.headers):
   if path=='/':return self.reply(cloud_access.ENTRY_HTML,kind='text/html; charset=utf-8')
   return self.reply({'error':'Open your personal preview link first.'},403)
  try:
   if path=='/':return self.reply((ROOT/'codex-web/index.html').read_bytes().replace(b'__TOKEN__',TOKEN.encode()),kind='text/html; charset=utf-8')
   if path=='/api/status':return self.reply(status())
   if path=='/api/jobs':
    jobs=[]
    for f in sorted((DATA/'jobs').glob('*/job.json'),key=lambda p:p.stat().st_mtime,reverse=True):
     d=json.loads(f.read_text());jobs.append(d)
    return self.reply(jobs)
   if path.startswith('/api/jobs/'):return self.reply(read_job(path.rsplit('/',1)[1]))
   if path=='/api/files':return self.reply([{'path':str(f.relative_to(DATA)),'name':f.name} for folder in ['uploads','jobs'] for f in (DATA/folder).rglob('*') if f.is_file() and (folder=='uploads' or 'output' in f.relative_to(DATA).parts)])
   if path.startswith('/download/'):
    f=safe_file(path.removeprefix('/download/'));return self.reply(f.read_bytes(),kind=mimetypes.guess_type(f.name)[0] or 'application/octet-stream')
   return self.reply({'error':'Not found'},404)
  except (ValueError,FileNotFoundError):return self.reply({'error':'Not found'},404)
 def do_POST(self):
  if not self.allowed():return self.reply({'error':'Invalid request'},403)
  if urlparse(self.path).path=='/api/unlock':return cloud_access.unlock(self)
  if not cloud_access.authorized(self.headers) or self.headers.get('X-Local-Token')!=TOKEN:return self.reply({'error':'Invalid request'},403)
  try:
   n=int(self.headers.get('Content-Length','0'))
   if n<1 or n>30_000_000:raise ValueError('Request too large or empty')
   req=json.loads(self.rfile.read(n));path=urlparse(self.path).path
   if path=='/api/jobs':return self.reply(launch(req),201)
   if path=='/api/settings':
    provider=req.get('provider','gemini')
    if provider not in KEYS:raise ValueError('Invalid provider')
    with LOCK:
     if any(p.poll() is None for p in PROCESSES.values()):raise ValueError('Wait for the current task before changing settings.')
     c=config();c['AI_PROVIDER']=provider
     for key in [*KEYS.values(),'ELEVENLABS_API_KEY','OPENAI_MODEL','ANTHROPIC_MODEL']:
      if req.get(key):c[key]=str(req[key]).strip()
     fd=os.open(SETTINGS,os.O_WRONLY|os.O_CREAT|os.O_TRUNC,0o600)
     with os.fdopen(fd,'w') as f:json.dump(c,f)
    return self.reply(status())
   if path=='/api/upload':
    name=Path(str(req.get('name','document.md'))).name
    if not re.fullmatch(r'[\w .-]{1,160}',name) or Path(name).suffix.lower() not in ['.md','.txt','.pdf','.docx','.csv','.json']:raise ValueError('Upload PDF, DOCX, Markdown, text, CSV or JSON')
    b=base64.b64decode(req['content'],validate=True)
    if len(b)>20_000_000:raise ValueError('Maximum upload is 20 MB')
    p=DATA/'uploads'/uuid.uuid4().hex/name;p.parent.mkdir(parents=True);p.write_bytes(b)
    return self.reply({'path':str(p.relative_to(DATA))},201)
   if path=='/api/cancel':
    jid=req.get('id');proc=PROCESSES.get(jid)
    if not proc or proc.poll() is not None:raise ValueError('Task is not running')
    import signal
    CANCELLED.add(jid)
    if os.name=='nt':proc.terminate()
    else:os.killpg(proc.pid,signal.SIGTERM)
    return self.reply({'cancelled':jid})
   raise ValueError('Unknown action')
  except (ValueError,KeyError,TypeError,json.JSONDecodeError) as e:return self.reply({'error':str(e)},400)

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=8877);args=parser.parse_args()
 for f in (DATA/'jobs').glob('*/job.json'):
  d=json.loads(f.read_text())
  if d.get('status')=='running':d['status']='interrupted';save_job(f.parent,d)
 print(f'OpenDraft browser companion: http://127.0.0.1:{args.port}',flush=True)
 ThreadingHTTPServer(('127.0.0.1',args.port),Handler).serve_forever()
