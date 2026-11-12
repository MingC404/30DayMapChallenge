"""Retain official location links; never silently fix or jitter them."""
from prepare_data import D,write
import csv,re,html,json,collections,math
records=list(csv.DictReader((D/'water_records.csv').open(encoding='utf-8-sig')))
s=(D/'raw/official_statistics.html').read_text(encoding='utf-8-sig')
links={html.unescape(n):(lon,lat,html.unescape(url)) for url,lat,lon,n in re.findall(r'href="([^"]*q=([\d.]+),([\d.]+)[^"]*)"[^>]*>(.*?)</a>',s)}
gx={269,*range(287,297),305,306,308,310,312,313,315,317,321,323,324,326,327,328,329,330,331,332}
hk={280,282,283,284,285,337}
unresolved={
280:'官方链接纬度22.700702疑似落在深圳，与香港元朗新田蕃田不符；香港食环署确认地名属元朗新田，暂不采用坐标。',
307:'連縣为历史县名，清水的具体调查聚落尚未确认；官方链接似上级行政中心，暂不猜测。',
309:'布田具体历史聚落及今名未确认；官方链接疑为连山县城，待原调查文献核查。',
317:'樟村具体历史聚落未确认；官方链接疑为武宣县城，暂不猜测。',
326:'唐僚具体聚落及今名未确认；官方链接疑为北流城区，暂不猜测。'}
parent_only={278:'高明區',284:'香港特別行政區',300:'開平市',304:'恩平市',305:'臨桂區',308:'平樂縣',310:'宜州區',313:'賀州市信都一帶',315:'百色市',318:'封開縣',320:'郁南縣',321:'賓陽縣',323:'貴港市',324:'南寧市',328:'扶綏縣',329:'崇左市',333:'中山市',334:'珠海市',335:'東莞市',338:'曼谷都會區'}
modern={267:'廣州市從化區',268:'廣州市花都區',270:'廣州市增城區',271:'佛山市三水區',273:'肇慶市高要區',275:'廣州市番禺區',276:'雲浮市雲城區',277:'佛山市南海區',279:'佛山市順德區',297:'江門市鶴山市',298:'江門市蓬江區',299:'江門市新會區',301:'珠海市斗門區',302:'江門市台山市',303:'珠海市斗門區',307:'清遠市連州市（歷史連縣）',309:'清遠市連山壯族瑤族自治縣',317:'來賓市武宣縣',326:'玉林市北流市',327:'南寧市橫州市（歷史橫縣）',336:'深圳市寶安區'}
out=[]
for r in records:
 i=int(r['site_id']);name=r['site_original'];lon,lat,url=links[name]
 region='廣西壯族自治區' if i in gx else '香港特別行政區' if i in hk else '澳門特別行政區' if i==286 else '泰國' if i==338 else '廣東省'
 clean=re.sub(r'\((?:圍頭話|蜑家話|土話|土拐話|百姓話|平話|賓陽話|四排話|廣府話)\)','',name)
 normalized=region+'／'+clean
 if i in modern:normalized=region+'／'+modern[i]+'／'+('、'.join(re.findall(r'\((.*?)\)',clean)) or clean)
 confidence='中：官方链接，仅作城镇级近似，未经调查地址核对'
 precision='城镇或市县中心近似；误差范围未量化'
 notes='来源未声明坐标基准；按经纬度绘制，六位小数不代表调查定位精度。'
 if i in parent_only:
  precision='上级市县/区域中心近似，不代表括号内聚落';confidence='低：只支持区域位置';notes+='采用为'+parent_only[i]+'区域代表点，具体乡镇位置待核。'
 if i in unresolved:confidence='待核查：不绘制';precision='未定位';notes+=unresolved[i]
 if i==280:notes+=' 地名核对：https://www.fehd.gov.hk/tc_chi/map/toilet/toilet_pt.html?mapID=929&type=toilet'
 out.append(dict(site_id=r['site_id'],site_original=name,place_normalized=normalized,longitude='' if i in unresolved else round(float(lon),3),latitude='' if i in unresolved else round(float(lat),3),coordinate_source='小學堂粵語／收錄現況／调查点地图链接',source_url='https://xiaoxue.iis.sinica.edu.tw/yueyu/Statistics/Statistics',source_map_url=url,source_longitude=lon,source_latitude=lat,coordinate_basis='原页面未声明；按地理经纬度暂绘',precision=precision,confidence=confidence,ambiguity='是：调查聚落/链接位置待核' if i in unresolved else '未发现明显同名歧义；具体调查地址未核',region=region,map_status='pending' if i in unresolved else 'approximate',notes=notes))
write('site_coordinates.csv',out)
write('coordinate_review_queue.csv',[r for r in out if r['map_status']=='pending' or r['confidence'].startswith('低')])
joined=[r|{('coordinate_notes' if k=='notes' else k):v for k,v in c.items() if k not in r or k=='notes'} for r,c in zip(records,out)]
write('water_geocoded.csv',joined)
features=[dict(type='Feature',geometry=dict(type='Point',coordinates=[r['longitude'],r['latitude']]) if r['longitude']!='' else None,properties=r) for r in joined]
(D/'water_points.geojson').write_text(json.dumps(dict(type='FeatureCollection',features=features),ensure_ascii=False,indent=2),encoding='utf-8')
groups=collections.defaultdict(list)
for r in joined:
 if r['longitude']!='':groups[(r['longitude'],r['latitude'])].append(r)
write('coincident_points.csv',[dict(longitude=k[0],latitude=k[1],site_count=len(v),sites='；'.join(r['site_original'] for r in v),initials='；'.join(r['initial'] for r in v),reason='沿用官方上级中心近似坐标；不表示同一调查位置') for k,v in groups.items() if len(v)>1])
print('coordinates',len(out),'mapped',sum(r['longitude']!='' for r in out),'pending',len(unresolved))
