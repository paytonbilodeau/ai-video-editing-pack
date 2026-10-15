#!/usr/bin/env python3
"""Make a new disposable synthetic source. Requires installed FFmpeg, no downloads."""
import argparse,json,math,struct,subprocess,wave
from pathlib import Path

def make_fixture(destination):
    d=Path(destination)
    if d.exists():raise FileExistsError('Choose a new fixture directory')
    d.mkdir(parents=True)
    sample_rate=48000;frames=90;fps=30;duration=frames/fps
    # Synthetic tones and one click. There is no recorded human voice.
    samples=[]
    for n in range(int(duration*sample_rate)):
        time=n/sample_rate
        value=.035*math.sin(2*math.pi*440*time)
        if sample_rate <= n < sample_rate+240:value += .3*math.sin(2*math.pi*1800*time)
        samples.append(max(-32767,min(32767,round(value*32767))))
    for name,multiplier in [('source.wav',1.0),('processed-example.wav',.3)]:
        with wave.open(str(d/name),'wb') as w:
            w.setnchannels(2);w.setsampwidth(2);w.setframerate(sample_rate)
            w.writeframes(b''.join(struct.pack('<hh',round(v*multiplier),round(v*multiplier)) for v in samples))
    subprocess.run(['ffmpeg','-v','error','-n','-f','lavfi','-i','testsrc2=size=1280x720:rate=30:duration=3','-i',str(d/'source.wav'),'-map','0:v','-map','1:a','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',str(d/'source.mp4')],check=True)
    (d/'protected-ranges.json').write_text(json.dumps({'fps':30,'frames':90,'ranges':[{'start_frame':30,'end_frame':45}]},indent=2)+'\n')
    (d/'illustrative-word-cues.json').write_text(json.dumps({'words':[{'word':'Synthetic','start':.25,'end':.7},{'word':'test','start':1.0,'end':1.4},{'word':'fixture','start':2.0,'end':2.4}]},indent=2)+'\n')
    (d/'README.md').write_text('# Synthetic technical fixture\n\nThree seconds of generated test pattern, tone and a click at one second. No human voice, filmed demonstration or actual transcription is present. Word cues are deliberately authored overlay-test data. The attenuated WAV is a simulated processing result, not Auphonic output.\n')
    return d
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('new_output_directory');a=p.parse_args();print(make_fixture(a.new_output_directory))
