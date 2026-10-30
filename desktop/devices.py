"""Device commands with explicit targets and verified read-back."""
import re
import time
from desktop.windows import com_thread

DEVICE_ACTIONS={'brightness','brightness_up','brightness_down','brightness_status','volume','volume_up','volume_down','audio_status','mute','unmute'}
DISPLAY_ALIASES={'laptop':'internal','built in':'internal','built-in':'internal','external monitor':'external',
                 'left monitor':'left','right monitor':'right','upper':'top','lower':'bottom',
                 'main':'primary','main monitor':'primary','second monitor':'2','first monitor':'1',
                 'that':'previous','that one':'previous','same':'previous','the other':'other'}

def bind_explicit_monitor(command,request):
 """Preserve a single literal monitor number instead of a model's stale choice.

 No action is created. Negations, multiple targets and physical aliases remain
 with the semantic planner; they cannot be corrected by this narrow entity rule.
 """
 if not isinstance(command,dict) or not str(command.get('action','')).startswith('brightness'):return command
 text=number_words(str(request).lower())
 if re.search(r"\b(?:not|don't|never|leave|alone|except|without|laptop|internal|external|primary|main|left|right|upper|lower|top|bottom|other|same)\b",text):return command
 numbers=set(re.findall(r'\b(?:monitor|display|screen)\s+(\d{1,2})\b',text))
 for ordinal,number in (('first','1'),('second','2'),('third','3'),('fourth','4')):
  if re.search(r'\b'+ordinal+r'\s+(?:monitor|display|screen)\b',text):numbers.add(number)
 if len(numbers)==1:
  number=next(iter(numbers))
  if 1<=int(number)<=16:return {**command,'display':number}
 return command
WORDS={'zero':0,'one':1,'two':2,'three':3,'four':4,'five':5,'six':6,'seven':7,'eight':8,'nine':9,'ten':10,'eleven':11,'twelve':12,'thirteen':13,'fourteen':14,'fifteen':15,'sixteen':16,'seventeen':17,'eighteen':18,'nineteen':19,'twenty':20,'thirty':30,'forty':40,'fifty':50,'sixty':60,'seventy':70,'eighty':80,'ninety':90,'hundred':100}
def number_words(text):
 def replace(match):
  words=match.group().lower().replace('-',' ').split();total=0
  for word in words:
   if word=='hundred':total=max(total,1)*100
   else:total+=WORDS[word]
  return str(total)
 group='(?:'+'|'.join(WORDS)+')'
 return re.sub(r'\b'+group+r'(?:[ -]'+group+r')*\b',replace,text,flags=re.I)

def parse_device(text):
 text=number_words(text.lower()).strip().rstrip('.!?')
 # Never treat negated requests or questions about how something works as changes.
 if re.search(r"\b(?:not|don't|never|explain|how|why)\b",text):return None
 kind='brightness' if re.search(r'\b(?:brightness|brighter|dimmer|dim)\b',text) else 'volume' if re.search(r'\b(?:volume|sound|audio|louder|quieter|mute|unmute)\b',text) else None
 if not kind:return None
 display='all'
 match=re.search(r'\b(?:monitor|display|screen)\s*(\d+)\b',text)
 if match:display=match[1];text=text[:match.start()]+text[match.end():]
 elif re.search(r'\b(?:second|2nd)\b',text):display='2'
 elif re.search(r'\b(?:first|1st)\b',text):display='1'
 elif re.search(r'\b(?:laptop|internal|built.in)\b',text):display='internal'
 elif re.search(r'\bexternal\b',text):display='external'
 elif re.search(r'\b(?:left|right|top|bottom|upper|primary|main)\s+(?:hand )?(?:monitor|screen|display)\b',text):
  side=re.search(r'\b(left|right|top|bottom|upper|primary|main)\b',text)[1]
  display=DISPLAY_ALIASES.get(side,side)
 elif re.search(r'\bother\b',text):display='other'
 elif re.search(r'\b(?:that (?:one|1)|same (?:screen|monitor)|that (?:screen|monitor))\b',text):display='previous'
 if re.search(r'\b(?:what|current|read|tell|show|check)\b',text) and not re.search(r'\b(?:set|change|turn|increase|decrease|lower|raise)\b',text):
  return {'action':'brightness_status' if kind=='brightness' else 'audio_status','target':'','display':display}
 if kind=='volume' and re.fullmatch(r'(?:please )?(?:unmute|mute)(?: (?:the |my )?(?:audio|volume|sound))?',text):return {'action':'unmute' if 'unmute' in text else 'mute','target':''}
 change=re.match(r'^(?:set|change|turn|increase|decrease|lower|raise|reduce|make|dim|brighten|brightness|volume)',text)
 if not change:return None
 value=re.search(r'\b(\d{1,3})\s*(?:percent|%)?',text)
 relative=bool(re.search(r'\bby\b',text))
 if value and not relative:return {'action':kind,'target':value[1],'display':display}
 down=bool(re.search(r'\b(?:down|decrease|lower|reduce|quieter|dimmer|dim)\b',text))
 if relative and value:
  return {'action':kind+'_down' if down else kind+'_up','target':value[1],'display':display}
 if re.search(r'\b(?:up|down|increase|decrease|lower|raise|reduce|brighter|dimmer|dim|brighten|louder|quieter)\b',text):
  return {'action':kind+'_down' if down else kind+'_up','target':'10','display':display}
 return None

def validate(command):
 action=command['action'];target=command.get('target','');display=command.get('display','all')
 if isinstance(display,str):display=DISPLAY_ALIASES.get(display.lower().strip(),display.lower().strip())
 if action not in DEVICE_ACTIONS:raise ValueError('Unsupported device command.')
 if action in {'brightness','volume','brightness_up','brightness_down','volume_up','volume_down'}:
  target=target or '10'
  if not isinstance(target,str) or not target.isdigit() or not 0<=int(target)<=100:raise ValueError('Choose a percentage between 0 and 100.')
 if not isinstance(display,str) or (display not in {'all','both','internal','external','left','right','top','bottom','primary','secondary','previous','other'} and not (display.isdigit() and 1<=int(display)<=16)):
  raise ValueError('Choose both displays, the laptop screen, external displays, or a monitor number.')
 return {'action':action,'target':target,'display':display,'confirm':False}

def display_layout():
 """Bob's monitor numbering plus Windows interface UID, without EDID guessing."""
 import win32api
 from desktop.windows import monitor_inventory
 result=[]
 for number,monitor in enumerate(monitor_inventory(),1):
  uids=[]
  for adapter in range(5):
   try:identity=win32api.EnumDisplayDevices(monitor['Device'],adapter,1).DeviceID
   except Exception:continue
   uid=re.search(r'UID(\d+)',identity,re.I)
   if uid:uids.append(uid[1])
  result.append({'number':number,'device':monitor['Device'],'rect':monitor['Monitor'],
                 'primary':bool(monitor['Flags']&1),'uids':uids})
 return result


def map_display_controls(infos,layout):
 """Never substitute another display when an individual identity is unknown."""
 rows=[];used=set()
 for monitor in layout:
  matches=[(i,info) for i,info in enumerate(infos) if info.get('uid') is not None and str(info['uid']) in monitor['uids']]
  row={**monitor,'info':None}
  if len(matches)==1 and matches[0][0] not in used:
   index,info=matches[0];used.add(index);row['info']=info
  rows.append(row)
 for index,info in enumerate(infos):
  if index not in used:rows.append({'number':None,'device':'','rect':None,'primary':False,'uids':[],'info':info})
 return rows


def select_displays(rows,selection,context=None):
 controls=[r for r in rows if r['info'] is not None]
 if selection in {'all','both'}:return controls
 if selection in {'internal','external'}:
  return [r for r in controls if (r['info']['method'].__name__=='WMI')==(selection=='internal')]
 if selection in {'previous','other'}:
  prior=(context or {}).get('last_brightness_display',{})
  if not prior.get('uid') or not 0<=time.time()-prior.get('at',0)<300:
   raise ValueError('Which monitor do you mean? Name the laptop, external screen, or a monitor number first.')
  previous=[r for r in controls if str(r['info'].get('uid'))==prior['uid'] and r['device']==prior.get('device')]
  if len(previous)!=1:raise ValueError('The previously selected screen changed or disconnected. Name the monitor again.')
  if selection=='previous':return previous
  others=[r for r in controls if r is not previous[0]]
  if len(others)!=1:raise ValueError('Which other monitor? There is more than one possible screen.')
  return others
 connected=[r for r in rows if r['number'] is not None]
 if selection.isdigit():chosen=[r for r in connected if r['number']==int(selection)]
 elif selection in {'primary','secondary'}:chosen=[r for r in connected if r['primary']==(selection=='primary')]
 else:
  axis=0 if selection in {'left','right'} else 1
  positions=[((r['rect'][axis]+r['rect'][axis+2])/2,r) for r in connected if r['rect']]
  if len(positions)<2:raise ValueError('Name the laptop or external monitor; a spatial choice needs at least two mapped screens.')
  edge=(min if selection in {'left','top'} else max)(p[0] for p in positions)
  chosen=[r for p,r in positions if abs(p-edge)<1]
 if len(chosen)!=1:raise ValueError('Which monitor? Say “list monitors” and choose its number, or name the laptop/external screen.')
 if chosen[0]['info'] is None:raise ValueError('That screen has no verified brightness control. Check its connection and enable DDC/CI in its own menu; Bob will not change another screen.')
 return chosen


def brightness(action,target='',selection='all',context=None):
 import screen_brightness_control as sbc
 with com_thread():
  infos=sbc.list_monitors_info()
  try:layout=display_layout()
  except Exception:layout=[]
  rows=map_display_controls(infos,layout)
  selected=select_displays(rows,selection,context)
  if not selected:raise ValueError('That display was not found. Say “what is my current brightness” to list connected displays.')
  results=[];errors=[];levels=[]
  for fallback,row in enumerate(selected,1):
   info=row['info'];index=row['number'] or fallback
   label=(f'Monitor {index}' if row['number'] is not None else f'Unmapped brightness device {fallback}') + (' (laptop)' if info['method'].__name__=='WMI' else ' (external)')
   try:
    device=sbc.Display.from_dict(info);before=device.get_brightness();actual=before
    if action!='brightness_status':
     wanted=int(target) if action=='brightness' else max(0,min(100,before+(int(target or '10') if action=='brightness_up' else -int(target or '10'))))
     device.set_brightness(wanted)
     for attempt in range(5):
      time.sleep(.12 if attempt==0 else .2);actual=device.get_brightness()
      if abs(actual-wanted)<=1 and (wanted==before or actual!=before):break
     if abs(actual-wanted)>1 or (wanted!=before and actual==before):raise RuntimeError(f'requested {wanted}%, but the display still reports {actual}%')
    results.append(f'{label}: {actual}%.')
    levels.append(actual)
   except Exception as exc:errors.append(f'{label} did not change: {exc}')
  if errors:raise RuntimeError(' '.join(results+errors))
  if context is not None and len(selected)==1 and selected[0]['info'].get('uid') is not None and selected[0]['device']:
   context['last_brightness_display']={'uid':str(selected[0]['info']['uid']),'device':selected[0]['device'],'at':time.time()}
  if len(levels)==2 and len(set(levels))==1 and action!='brightness_status':
   return f'Both screens are at {levels[0]}%.'
  return ' '.join(results)

def _audio(action,target):
 from pycaw.pycaw import AudioUtilities
 device=AudioUtilities.GetSpeakers();endpoint=device.EndpointVolume
 old=endpoint.GetMasterVolumeLevelScalar();muted=bool(endpoint.GetMute())
 if action in {'mute','unmute'}:
  endpoint.SetMute(action=='mute',None)
  if bool(endpoint.GetMute())!=(action=='mute'):raise RuntimeError('Windows did not apply the mute change.')
 elif action!='audio_status':
  level=int(target)/100 if action=='volume' else max(0,min(1,old+(int(target or '10')/100 if action=='volume_up' else -int(target or '10')/100)))
  endpoint.SetMasterVolumeLevelScalar(level,None)
  if level>0:endpoint.SetMute(False,None)
  if abs(endpoint.GetMasterVolumeLevelScalar()-level)>.015:raise RuntimeError('Windows did not apply the volume change.')
 actual=round(endpoint.GetMasterVolumeLevelScalar()*100);muted=bool(endpoint.GetMute());name=device.FriendlyName
 summary = 'Muted' if muted else f'Volume is {actual}%'
 return summary + (f' on {name}.' if action=='audio_status' else '.')

def execute(command,context=None):
 command=validate(command)
 if command['action'].startswith('brightness'):return brightness(command['action'],command['target'],command['display'],context)
 with com_thread():return _audio(command['action'],command['target'])
