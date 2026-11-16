"""Read-only Unity v22 container metadata and installed managed-mod IL inventory.
Not a native decompiler or a runtime profiler. Uses an existing local ILSpy.
"""
from pathlib import Path
import collections, hashlib, json, re, struct, subprocess
from s1lab import HERE, digest, root_checked
ROOT=root_checked(Path(r'B:\Schedule I'))
OUT=HERE/'evidence'
CLASS={1:'GameObject',21:'Material',28:'Texture2D',43:'Mesh',48:'Shader',49:'TextAsset',83:'AudioClip',114:'MonoBehaviour',128:'Font',129:'PlayerSettings',141:'BuildSettings',142:'AssetBundle',150:'PreloadData',187:'Texture2DArray',104:'RenderSettings',47:'QualitySettings',30:'GraphicsSettings'}

def parse(path):
    with path.open('rb') as f:
        h=f.read(48)
        _,_,version,_=struct.unpack('>IIII',h[:16])
        if version!=22: raise ValueError('Only serialized format v22 supported; got '+str(version))
        endian='<' if h[16]==0 else '>'
        metadata,size,offset,_=struct.unpack('>IQQQ',h[20:48])
        if size!=path.stat().st_size: raise ValueError('File-size mismatch')
        if metadata>64*1024*1024: raise ValueError('Metadata safety limit')
        buf=f.read(metadata)
    pos=0
    def read(fmt):
        nonlocal pos
        st=struct.Struct(endian+fmt)
        if pos+st.size>len(buf): raise ValueError('Truncated metadata')
        v=st.unpack_from(buf,pos); pos+=st.size
        return v[0] if len(v)==1 else v
    def skip(n):
        nonlocal pos
        if n<0 or pos+n>len(buf):raise ValueError('Invalid metadata length')
        pos+=n
    end=buf.index(0); unity=buf[:end].decode(); pos=end+1
    platform=read('i'); trees=read('?'); nt=read('i')
    if not 0<=nt<=100000:raise ValueError('Invalid type count')
    types=[]
    for _ in range(nt):
        cls=read('i'); stripped=read('?'); script=read('h')
        if cls==114:skip(16)
        skip(16)
        if trees:
            nodes=read('i'); strings=read('i');skip(nodes*32);skip(strings)
            deps=read('i');skip(deps*4)
        types.append(cls)
    count=read('i')
    if not 0<=count<=10000000:raise ValueError('Invalid object count')
    totals=collections.Counter();sizes=collections.Counter();textures=[]
    for _ in range(count):
        skip((-pos)%4)
        objid=read('q'); start=read('q')+offset; length=read('I'); tid=read('i')
        if not 0<=tid<len(types) or start<offset or start+length>size:raise ValueError('Object bounds invalid')
        cls=types[tid]; name=CLASS.get(cls,'ClassID_'+str(cls));totals[name]+=1;sizes[name]+=length
    return {'file':path.name,'unity':unity,'serialized_version':version,'type_tree_present':trees,
            'objects':count,'class_counts':dict(totals),'serialized_object_bytes':dict(sizes),
            'note':'Serialized bytes are not resident RAM/VRAM. External resS/resource bytes excluded. No texture decoding or shader disassembly.'}

assets=[]
for p in sorted((ROOT/'Schedule I_Data').iterdir()):
    if p.is_file() and (p.suffix=='.assets' or p.name=='globalgamemanagers' or re.fullmatch(r'level\d+',p.name)):
        try:assets.append(parse(p))
        except Exception as e:assets.append({'file':p.name,'error':str(e),'complete':False})
(OUT/'assets.json').write_text(json.dumps(assets,indent=2),encoding='utf-8')
print('CONTAINERS',json.dumps([{k:v for k,v in x.items() if k in ('file','objects','type_tree_present','class_counts','error')} for x in assets]))

exe=Path(r'C:\Users\herob\Documents\notion-code\tools\ilspy\.store\ilspycmd\11.2.0.10050\ilspycmd.win-x64\11.2.0.10050\tools\any\win-x64\ilspycmd.exe')
mods=[]
for p in sorted((ROOT/'Mods').glob('*.dll')):
    try:
        proc=subprocess.run([str(exe),'-il',str(p)],capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=35)
        if proc.returncode:raise ValueError('ILSpy returned nonzero')
        il=proc.stdout
        refs=sorted(set(re.findall(r'\[([A-Za-z][A-Za-z0-9_.-]+)\](?=[A-Za-z_])',il)))
        # Method names indicate possible paths, not proof of executed cost/conflict.
        indicators={k:len(re.findall(re.escape(k),il)) for k in (
            'FindObjectsOfType','FindObjectsByType','GetComponentsInChildren','GC::Collect',
            'AppendAllText','WriteAllText','HarmonyPatch','streamingMipmapsMemoryBudget',
            'OnUpdate','OnGUI','LogDebug','TextureBudgetMB','CanvasScanInterval')}
        mods.append({'file':p.name,'sha256':digest(p),'referenced_assembly_names_in_IL_not_full_manifest':refs,
                     'il_text_occurrences_not_call_counts':indicators})
        if p.stem in ('S1Perf','ScheduleRu'):
            r=subprocess.run([str(exe),str(p)],capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=35)
            if r.returncode==0:(OUT/(p.stem+'.installed.cs')).write_text(r.stdout,encoding='utf-8')
    except Exception as e:mods.append({'file':p.name,'error':str(e)})
(OUT/'mod-analysis.json').write_text(json.dumps(mods,indent=2),encoding='utf-8')
print('MODS',json.dumps(mods))
