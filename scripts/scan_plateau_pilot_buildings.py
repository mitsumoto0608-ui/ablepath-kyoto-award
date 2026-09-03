import xml.etree.ElementTree as ET, json, math, sys, glob, os, hashlib
NS={'bldg':'http://www.opengis.net/citygml/building/2.0','gml':'http://www.opengis.net/gml','uro':'https://www.geospatial.jp/iur/uro/3.2','core':'http://www.opengis.net/citygml/2.0'}
BUF=30.0
edges=json.load(open(sys.argv[1]))
files=sys.argv[2:]
def proj(lat0):
    kx=111320*math.cos(math.radians(lat0)); ky=110574
    return lambda lon,lat: ((lon)*kx,(lat)*ky)
def seg_dist(px,py,ax,ay,bx,by):
    dx,dy=bx-ax,by-ay; L2=dx*dx+dy*dy
    t=0 if L2==0 else max(0,min(1,((px-ax)*dx+(py-ay)*dy)/L2))
    cx,cy=ax+t*dx,ay+t*dy
    return math.hypot(px-cx,py-cy),t,(cx,cy),(dx,dy)
bl={}  # buildings by file
envs={}
for f in files:
    tree=ET.parse(f); root=tree.getroot()
    env=root.find('gml:boundedBy/gml:Envelope',NS)
    lo=env.find('gml:lowerCorner',NS).text.split(); hi=env.find('gml:upperCorner',NS).text.split()
    envs[os.path.basename(f)]={'srs':env.get('srsName'),'lat':[float(lo[0]),float(hi[0])],'lon':[float(lo[1]),float(hi[1])]}
    blds=[]
    for b in root.iter('{%s}Building'%NS['bldg']):
        gid=b.get('{%s}id'%NS['gml'])
        bid=None
        for e in b.iter('{%s}buildingID'%NS['uro']): bid=e.text; break
        mh=b.find('bldg:measuredHeight',NS)
        lods=[k for k in ('lod0RoofEdge','lod0FootPrint','lod1Solid','lod2Solid','lod2MultiSurface','lod3Solid') if b.find('bldg:'+k,NS) is not None]
        # footprint vertices: prefer lod0RoofEdge/FootPrint, else lod1Solid all posList
        src=None
        for k in ('lod0RoofEdge','lod0FootPrint','lod1Solid'):
            el=b.find('bldg:'+k,NS)
            if el is not None: src=(k,el); break
        pts=[]
        if src:
            for pl in src[1].iter('{%s}posList'%NS['gml']):
                v=list(map(float,pl.text.split()))
                for i in range(0,len(v)-2,3): pts.append((v[i+1],v[i]))  # (lon,lat)
        usage=b.find('bldg:usage',NS); storeys=b.find('bldg:storeysAboveGround',NS)
        def one(tag):
            for e in b.iter('{%s}%s'%(NS['uro'],tag)): return e.text
            return None
        def many(tag): return sorted({e.text for e in b.iter('{%s}%s'%(NS['uro'],tag)) if e.text})
        hq={'lod1HeightType':one('lod1HeightType'),'geometrySrcDescLod1':one('geometrySrcDescLod1'),'thematicSrcDesc':many('thematicSrcDesc'),'surveyYear':one('surveyYear')}
        hv=None if mh is None else float(mh.text)
        hstat='MISSING' if mh is None else ('INVALID_SENTINEL' if hv<=0 else ('OFFICIAL_ATTRIBUTE_UNIFORM_FALLBACK_3M' if hq['lod1HeightType']=='0' else ('OFFICIAL_ATTRIBUTE_STOREY_ESTIMATE' if hq['lod1HeightType']=='9' else 'OFFICIAL_ATTRIBUTE_PRESENT')))
        blds.append({'gml_id':gid,'uro_buildingID':bid,'measuredHeight':None if mh is None else mh.text,'height_uom':None if mh is None else mh.get('uom'),'lods':lods,'fp_source':src[0] if src else None,'pts':pts,'usage':None if usage is None else usage.text,'hq':hq,'height_status':hstat,'storeys':None if storeys is None else storeys.text,'file':os.path.basename(f)})
    bl[os.path.basename(f)]=blds
out={'files':envs,'building_counts':{k:len(v) for k,v in bl.items()},'edges':[]}
allb=[b for v in bl.values() for b in v]
for eid,e in edges.items():
    cs=e['coords']; lat0=sum(c[1] for c in cs)/len(cs); P=proj(lat0)
    segs=[(P(*cs[i]),P(*cs[i+1])) for i in range(len(cs)-1)]
    L=sum(math.hypot(b[0]-a[0],b[1]-a[1]) for a,b in segs)
    # coverage: buffer bbox within union of envelopes?
    xs=[c[0] for c in cs]; ys=[c[1] for c in cs]; dlon=BUF/(111320*math.cos(math.radians(lat0))); dlat=BUF/110574
    bb=(min(xs)-dlon,max(xs)+dlon,min(ys)-dlat,max(ys)+dlat)
    covered=any(en['lon'][0]<=bb[0] and en['lon'][1]>=bb[1] and en['lat'][0]<=bb[2] and en['lat'][1]>=bb[3] for en in envs.values())
    # union check (2 meshes adjacent) simplistic: every corner inside some envelope
    corners=[(bb[0],bb[2]),(bb[0],bb[3]),(bb[1],bb[2]),(bb[1],bb[3])]
    corner_ok=all(any(en['lon'][0]<=x<=en['lon'][1] and en['lat'][0]<=y<=en['lat'][1] for en in envs.values()) for x,y in corners)
    left=[];right=[]
    for b in allb:
        if not b['pts']: continue
        best=None
        for (lon,lat) in b['pts']:
            px,py=P(lon,lat)
            for (a,c) in segs:
                d,t,(cx,cy),(dx,dy)=seg_dist(px,py,a[0],a[1],c[0],c[1])
                if best is None or d<best[0]: best=(d,dx*(py-cy)-dy*(px-cx))
        if best and best[0]<=BUF:
            rec={'gml_id':b['gml_id'],'uro_buildingID':b['uro_buildingID'],'measuredHeight':b['measuredHeight'],'height_uom':b['height_uom'],'lods':b['lods'],'fp_source':b['fp_source'],'fp_vertex_count':len(b['pts']),'usage_code':b['usage'],'height_status':b['height_status'],'height_provenance':b['hq'],'storeys':b['storeys'],'mesh_file':b['file'],'min_footprint_vertex_to_edge_m_NOT_SETBACK':round(best[0],2)}
            (left if best[1]>0 else right).append(rec)
    left.sort(key=lambda r:r['min_footprint_vertex_to_edge_m_NOT_SETBACK']); right.sort(key=lambda r:r['min_footprint_vertex_to_edge_m_NOT_SETBACK'])
    out['edges'].append({'edge_id':eid,'city_id':e['city'],'edge_length_m_approx':round(L,1),'search_buffer_m':BUF,'buffer_bbox_within_single_mesh':covered,'buffer_bbox_corners_within_loaded_meshes':corner_ok,'left_candidates':left,'right_candidates':right})
json.dump(out,open(os.path.join(os.path.dirname(sys.argv[1]),'scan_out.json'),'w'),ensure_ascii=False,indent=1)
print(json.dumps({'files':envs,'counts':out['building_counts']},ensure_ascii=False))
for e in out['edges']:
    hs=[r['measuredHeight'] for r in e['left_candidates']+e['right_candidates']]
    print(e['edge_id'][:60],'L',e['edge_length_m_approx'],'cov1',e['buffer_bbox_within_single_mesh'],'corners',e['buffer_bbox_corners_within_loaded_meshes'],'left',len(e['left_candidates']),'right',len(e['right_candidates']),'height_missing',sum(1 for h in hs if h is None),'ids_missing',sum(1 for r in e['left_candidates']+e['right_candidates'] if not r['uro_buildingID']))
