# Corrected reusable fixture. Requires the empty scratch composition and injected Resolve objects.
# build-native.py preserves the failed absolute-handle baseline.
from pathlib import Path
import json
# Run through the editor's supported scripting context after setting these inputs.
# OUTPUT_DIR must be a NEW folder; EXPECTED_PROJECT must equal the selected scratch project.
assert isinstance(EXPECTED_PROJECT, str) and EXPECTED_PROJECT
assert project.GetName() == EXPECTED_PROJECT, 'Selected project changed; stop.'
out=Path(OUTPUT_DIR).expanduser().resolve()
out.mkdir(parents=True, exist_ok=False)
assert not project.IsRenderingInProgress()
t=project.GetCurrentTimeline(); item=t.GetItemListInTrack('video',1)[0]; c=item.GetFusionCompByIndex(1)
assert len(c.GetToolList())==1, 'Exercise is already built; preserve it.'
c.Lock(); c.StartUndo('Course mask and parent motion exercise')
nodes={}; edges=[]
def add(role,kind):
    tool=c.AddTool(kind,False,len(nodes)*2,0,False,False)
    assert tool and tool.ID==kind
    tool.SetData('training_role',role); nodes[role]=tool
    return tool
def setv(tool,name,value):
    assert name in {v.ID for v in tool.GetInputList().values()}, (tool.ID,name)
    tool.SetInput(name,value,0)
def connect(role,name,upstream):
    assert nodes[role].ConnectInput(name,nodes[upstream])
    edges.append([upstream,role,name])
def bg(role,rgba):
    tool=add(role,'Background')
    for k,v in zip(['TopLeftRed','TopLeftGreen','TopLeftBlue','TopLeftAlpha'],rgba): setv(tool,k,v)
    return tool
def animate(tool,name,keys):
    assert tool.AddModifier(name,'BezierSpline')
    inp={v.ID:v for v in tool.GetInputList().values()}[name]
    spline=inp.GetConnectedOutput().GetTool()
    spline.SetKeyFrames(keys,True)
    return {'node':tool.Name,'input':name,'keys':spline.GetKeyFrames(),'values':{str(f):tool.GetInput(name,f) for f in [0,9,18,24,40,60,90,119,149]}}
try:
    bg('canvas',(0.025,0.035,0.045,1))
    mask=add('card_mask','RectangleMask'); setv(mask,'Width',.68); setv(mask,'Height',.42); setv(mask,'CornerRadius',.06)
    bg('card',(15/255,88/255,61/255,1)); connect('card','EffectMask','card_mask')
    sm=add('stripe_shape','RectangleMask'); setv(sm,'Width',1.10); setv(sm,'Height',.05)
    bg('stripe',(.9,.95,.93,1)); connect('stripe','EffectMask','stripe_shape')
    stripe=add('stripe_motion','Transform'); connect('stripe_motion','Input','stripe')
    add('clipped_detail','Merge'); connect('clipped_detail','Background','card'); connect('clipped_detail','Foreground','stripe_motion'); connect('clipped_detail','EffectMask','card_mask')
    parent=add('card_parent','Transform'); connect('card_parent','Input','clipped_detail')
    add('card_on_canvas','Merge'); connect('card_on_canvas','Background','canvas'); connect('card_on_canvas','Foreground','card_parent')
    fgmask=add('foreground_shape','EllipseMask'); setv(fgmask,'Width',.20); setv(fgmask,'Height',.12); setv(fgmask,'Center',{1:.27,2:.46})
    bg('foreground',(.9,.35,.1,1)); connect('foreground','EffectMask','foreground_shape')
    add('composite','Merge'); connect('composite','Background','card_on_canvas'); connect('composite','Foreground','foreground')
    mo=next(v for v in c.GetToolList().values() if v.ID=='MediaOut'); assert mo.ConnectInput('Input',nodes['composite'])
    motion=[]
    motion.append(animate(parent,'Size',{0: {1: 0.72, 'RH': {1: 6, 2: 0.0}}, 18: {1: 1.06, 'LH': {1: -6, 2: 0.0}, 'RH': {1: 2, 2: 0.0}}, 24: {1: 1, 'LH': {1: -2, 2: 0}, 'RH': {1: 30, 2: 0}}, 119: {1: 1, 'LH': {1: -30, 2: 0}, 'RH': {1: 10, 2: 0}}, 149: {1: 0.72, 'LH': {1: -10, 2: 0.0}}}))
    motion.append(animate(stripe,'Angle',{0: {1: 0, 'RH': {1: 8, 2: 0}}, 24: {1: 0, 'LH': {1: -8, 2: 0}, 'RH': {1: 10, 2: 0}}, 54: {1: 90, 'LH': {1: -10, 2: 0}, 'RH': {1: 21, 2: 0}}, 149: {1: 90, 'LH': {1: -19, 2: 0}}}))
finally:
    c.EndUndo(True); c.Unlock()
assert item.ExportFusionComp(str(out/'occlusion.comp'),1)
assert resolve.GetProjectManager().SaveProject()
receipt={'project':project.GetName(),'timeline':t.GetName(),'duration':item.GetDuration(),'range':[item.GetStart(),item.GetEnd()],'nodes':{k:{'name':v.Name,'id':v.ID} for k,v in nodes.items()},'edges':edges,'motion':motion,'composition_exported':True}
(out/'native-build-corrected.json').write_text(json.dumps(receipt,indent=2))
result={'built':True,'node_count':len(nodes),'duration':item.GetDuration(),'render_started':False,'parent_values':motion[0]['values']}
