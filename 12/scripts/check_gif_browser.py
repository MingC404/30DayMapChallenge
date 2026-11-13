"""Verify actual GIF playback in an isolated headless Chromium browser, offline."""
import argparse,base64,hashlib,io,json,subprocess,tempfile,time,urllib.request
from pathlib import Path
import numpy as np
from PIL import Image
import websocket

ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--gif',required=True)
    parser.add_argument('--report',required=True)
    args=parser.parse_args()
    gif_path=(ROOT/args.gif).resolve(); report_path=(ROOT/args.report).resolve()
    assert gif_path.is_relative_to(ROOT.resolve()) and report_path.is_relative_to(ROOT.resolve())
    browsers=[Path('C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'),
              Path('C:/Program Files/Google/Chrome/Application/chrome.exe')]
    exe=next(p for p in browsers if p.is_file())
    cache=ROOT/'data/cache'
    with tempfile.TemporaryDirectory(prefix='gif_browser_',dir=cache) as profile:
        assert Path(profile).resolve().is_relative_to(cache.resolve())
        proc=subprocess.Popen([str(exe),'--headless=new','--disable-gpu','--no-first-run','--no-sandbox',
            '--disable-extensions','--disable-background-networking',
            '--no-default-browser-check','--remote-debugging-port=0','--remote-allow-origins=*',
            '--user-data-dir='+profile,'about:blank'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW)
        ws=None
        try:
            portfile=Path(profile)/'DevToolsActivePort'
            for _ in range(100):
                if portfile.exists(): break
                time.sleep(.2)
            port=int(portfile.read_text().splitlines()[0]); time.sleep(1)
            tabs=json.load(urllib.request.urlopen(f'http://127.0.0.1:{port}/json'))
            tab=next(t for t in tabs if t['type']=='page')
            ws=websocket.create_connection(tab['webSocketDebuggerUrl'],timeout=15)
            counter=0
            def call(method,params=None):
                nonlocal counter
                counter+=1; ident=counter
                ws.send(json.dumps({'id':ident,'method':method,'params':params or {}}))
                while True:
                    answer=json.loads(ws.recv())
                    if answer.get('id')==ident:
                        if 'error' in answer: raise RuntimeError(answer['error'])
                        return answer.get('result',{})
            call('Page.enable')
            call('Emulation.setDeviceMetricsOverride',{'width':960,'height':920,'deviceScaleFactor':1,'mobile':False})
            call('Page.navigate',{'url':gif_path.as_uri()})
            time.sleep(1)
            status=call('Runtime.evaluate',{'expression':
                'JSON.stringify({complete:document.images[0]?.complete,width:document.images[0]?.naturalWidth,height:document.images[0]?.naturalHeight})',
                'returnByValue':True})
            info=json.loads(status['result']['value']); assert info['complete'] and info['width']>0
            captures=[]
            for delay in (0,1.6,1.6):
                if delay: time.sleep(delay)
                png=base64.b64decode(call('Page.captureScreenshot',{'format':'png','captureBeyondViewport':False})['data'])
                captures.append(np.asarray(Image.open(io.BytesIO(png)).convert('RGB')))
            diffs=[int(np.any(a!=b,axis=2).sum()) for a,b in zip(captures[:-1],captures[1:])]
            assert min(diffs)>1000,'Browser did not display changing GIF frames'
            report={'browser':str(exe),'image':info,'browser_screenshot_changed_pixels':diffs,
                    'playback_verified':True,'network_used':False,'screenshots_saved':False,
                    'gif_sha256':hashlib.sha256(gif_path.read_bytes()).hexdigest()}
            report_path.write_text(json.dumps(report,indent=2)+'\n')
            print(json.dumps(report,indent=2))
            call('Browser.close')
        finally:
            if ws: ws.close()
            try: proc.wait(timeout=8)
            except subprocess.TimeoutExpired:
                proc.kill(); proc.wait()
            time.sleep(.5)

if __name__=='__main__': main()
