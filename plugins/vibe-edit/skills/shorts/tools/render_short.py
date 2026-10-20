#!/usr/bin/env python3
"""Render one reviewed short from a customer project directory.
Usage: render_short.py PROJECT SHORT_ID [--no-ink]
Requires content-map.json, shorts/layouts.json and shorts/caption-plan.json.
Creates a new working-output subfolder; refuses an existing final output.
Preserves source speech without an enhancement chain; AAC extraction is a re-encode.
"""
import json, sys, subprocess, pathlib
if len(sys.argv)<3: raise SystemExit(__doc__)
B=pathlib.Path(sys.argv[1]).expanduser().resolve(); M=pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0,str(M.parent/'edit/tools'))
from video_render_check import check_render
sid=sys.argv[2]; NO_INK='--no-ink' in sys.argv; FORCE='--force-overlay' in sys.argv
L=json.load(open(B/'shorts/layouts.json')); S=L['shorts'][sid]; cm={c['id']:c for c in json.load(open(B/'content-map.json'))['clips']}[sid]
cap=json.load(open(B/'shorts/caption-plan.json'))[sid]; SRC=str((B/cm['source']).resolve()); FPS=float(L.get('fps',30))
work=B/'shorts'/sid; work.mkdir(parents=True,exist_ok=False); out=(B/cm['output']).resolve(); out.parent.mkdir(parents=True,exist_ok=True)
if out.exists(): raise SystemExit('Output exists; choose a new project/output path')
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=r_frame_rate','-of','json',SRC])); n,d=map(int,probe['streams'][0]['r_frame_rate'].split('/')); assert abs(n/d-FPS)<1e-6, 'Layout FPS must match source FPS' 
start_f=cm['start_frame']; total=cm['end_frame']-start_f; dur=total/FPS

# ---- video filter graph: one input, per-segment trim + layout, concat
parts=[]; labels=[]
for i,seg in enumerate(S['segments']):
    a,b_,name=seg[0],seg[1],seg[2]; mode=seg[3] if len(seg)>3 else None; lay=L[name]; n=b_-a
    if mode in ('hold_first','hold_last'):
        src_a=b_ if mode=='hold_first' else a-1  # hold the next segment's first frame, or the previous segment's last frame (screen-share transitions)
        trim=f"[0:v]trim=start_frame={src_a}:end_frame={src_a+1},setpts=PTS-STARTPTS,loop=loop={n-1}:size=1:start=0,setpts=N/{FPS}/TB"
    else:
        trim=f"[0:v]trim=start_frame={a}:end_frame={b_},setpts=PTS-STARTPTS"
    if lay['type']=='full':
        x,y,w,h=lay['crop']; parts.append(f"{trim},crop={w}:{h}:{x}:{y},scale=2160:3840:flags=lanczos,setsar=1[v{i}]")
    elif lay['type']=='desktop_inset_v2':
        d=lay['desktop']; c=lay['inset']; dx,dy,dw,dh=d['crop']; cx,cy,cw,ch=c['crop']
        dH=round(dh*2160/dw); iw=round(cw*c['scale']); ih=round(ch*c['scale']); ix=(2160-iw)//2
        parts.append(f"{trim},split=3[s{i}a][s{i}b][s{i}c];"
            f"[s{i}a]crop={cw}:{ch}:{cx}:{cy},scale=2160:3840:flags=bicubic,hflip,gblur=sigma=46,eq=brightness=-0.18:saturation=0.85,setsar=1[bg{i}];"
            f"[s{i}b]crop={dw}:{dh}:{dx}:{dy},scale=2160:{dH}:flags=lanczos,setsar=1[dk{i}];"
            f"[s{i}c]crop={cw}:{ch}:{cx}:{cy},scale={iw}:{ih}:flags=lanczos,setsar=1[in{i}];"
            f"[bg{i}][dk{i}]overlay=0:{d['y']}[m{i}];[m{i}][in{i}]overlay={ix}:{c['y']}[v{i}]")
    else:
        t=lay['top']; bt=lay['bottom']; tx,ty,tw,th=t['crop']; bx,by,bw,bh=bt['crop']
        parts.append(f"{trim},split=2[s{i}a][s{i}b];[s{i}a]crop={tw}:{th}:{tx}:{ty},scale=2160:{t['h']}:flags=lanczos,setsar=1[t{i}];[s{i}b]crop={bw}:{bh}:{bx}:{by},scale=2160:{bt['h']}:flags=lanczos,setsar=1[b{i}];[t{i}][b{i}]vstack[v{i}]")
    labels.append(f"[v{i}]")
graph=";".join(parts)+";"+"".join(labels)+f"concat=n={len(labels)}:v=1:a=0,setpts=N/{FPS}/TB,format=yuv420p[base]"

# ---- overlay props: cues carry the measured safe caption bottom (4K px) for the layout active at cue start
def layout_at(t):
    f=start_f+int(t*FPS)
    for seg in S['segments']:
        if seg[0]<=f<seg[1]: return seg[2]
    return S['segments'][-1][2]
cues=[]
for q in cap['cues']:
    a,b_=q['start'],min(q['end'],dur)
    if b_<=a: continue
    cues.append({'start':round(a,3),'end':round(b_,3),'text':q['text'],'y':S['caption_y'][layout_at(a)]})
h0,h1=S['hook']
if S.get('hook_until_layout_change',True):
    from hook_rule import hook_end_seconds   # Payton, Oct 9: whole short, or until the first screen share, never returning
    h1=hook_end_seconds(S,start_f,dur,FPS)
hook={'text':cm['hook'],'start':h0,'end':round(h1,2),'top':S.get('hook_top_px',440)}
ink=S.get('ink'); ink_props={k:v for k,v in ink.items() if k!='layout'} if (ink and not NO_INK) else None
props={'fps':FPS,'frames':total,'hook':hook,'cues':cues,'ink':ink_props}
props_text=json.dumps(props,indent=1); (work/'overlay-props.json').write_text(props_text)

# ---- overlay render (Remotion, ProRes 4444 with alpha, full duration); reused when props are unchanged
ov_file=work/'overlay.mov'; prev=work/'overlay-props.prev.json'
if FORCE or not ov_file.exists() or not prev.exists() or prev.read_text()!=props_text:
    r=subprocess.run(['./node_modules/.bin/remotion','render','src/videos/short-overlay/index.tsx','Short-overlay',str(ov_file),
        '--props='+str(work/'overlay-props.json'),'--codec=prores','--prores-profile=4444','--image-format=png','--pixel-format=yuva444p10le',
        '--concurrency=4','--timeout=120000','--muted','--log=error'],cwd=str(M/'flow'),capture_output=True,text=True)
    assert r.returncode==0, r.stderr[-1500:]
    prev.write_text(props_text)

# ---- audio segment from the approved master (no re-processing)
aud=work/f'audio-{start_f}-{cm["end_frame"]}.m4a'  # keyed on the exact frame range so a changed boundary never reuses a stale cut
if not aud.exists(): subprocess.run(['ffmpeg','-v','error','-nostdin','-n','-ss',f'{start_f/FPS:.9f}','-i',SRC,'-t',f'{dur:.9f}','-vn','-c:a','aac','-b:a','320k','-ar','48000','-map_metadata','-1',str(aud)],check=True)

# ---- final encode: base graph -> overlay -> libx264
chain=f"{graph};[base][1:v]overlay=0:0:eof_action=pass:format=auto[vout]"
cmd=['ffmpeg','-hide_banner','-nostdin','-n','-i',SRC,'-i',str(ov_file),'-i',str(aud),'-filter_complex',chain,'-map','[vout]','-map','2:a:0',
     '-frames:v',str(total),'-r',str(FPS),'-fps_mode','cfr','-c:v','libx264','-preset','medium','-crf','17','-maxrate','60M','-bufsize','120M','-profile:v','high','-level','5.2',
     '-pix_fmt','yuv420p','-g','60','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv','-c:a','copy','-movflags','+faststart',str(out)]
(work/'ffmpeg-command.json').write_text(json.dumps(cmd,indent=1))
with (work/'ffmpeg.log').open('w') as fh: subprocess.run(cmd,stdout=fh,stderr=fh,check=True)
rec=check_render(out,width=2160,height=3840,fps=FPS,frames=total,audio='present',audio_reference=aud)
rec.update(recipe='portrait-layout-and-overlay',short=sid,perceptual_listening=False,visual_review='pending',ink=bool(ink_props),
           overlay='Remotion Short-overlay: hook card, phrase captions, one Gentlemen note; no libass')
(work/'technical.json').write_text(json.dumps(rec,indent=1)); assert rec['ok'],rec['errors']
print(sid,'ok',out.stat().st_size,'bytes',total,'frames')
