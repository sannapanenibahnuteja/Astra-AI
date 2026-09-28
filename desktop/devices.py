"""Device commands with explicit targets and verified read-back."""
import re
import time
from desktop.windows import com_thread

DEVICE_ACTIONS={'brightness','brightness_up','brightness_down','brightness_status','volume','volume_up','volume_down','audio_status','mute','unmute'}
WORDS={'zero':0,'one':1,'two':2,'three':3,'four':4,'five':5,'six':6,'seven':7,'eight':8,'nine':9,'ten':10,'eleven':11,'twelve':12,'thirteen':13,'fourteen':14,'fifteen':15,'sixteen':16,'seventeen':17,'eighteen':18,'nineteen':19,'twenty':20,'thirty':30,'forty':40,'fifty':50,'sixty':60,'seventy':70,'eighty':80,'ninety':90,'hundred':100}
def number_words(text):
 def replace(match):
  words=match.group().replace('-',' ').split();total=0
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
 if action not in DEVICE_ACTIONS:raise ValueError('Unsupported device command.')
 if action in {'brightness','volume','brightness_up','brightness_down','volume_up','volume_down'}:
  target=target or '10'
  if not isinstance(target,str) or not target.isdigit() or not 0<=int(target)<=100:raise ValueError('Choose a percentage between 0 and 100.')
 if not isinstance(display,str) or (display not in {'all','both','internal','external'} and not (display.isdigit() and 1<=int(display)<=16)):
  raise ValueError('Choose both displays, the laptop screen, external displays, or a monitor number.')
 return {'action':action,'target':target,'display':display,'confirm':False}

def brightness(action,target='',selection='all'):
 import screen_brightness_control as sbc
 with com_thread():
  infos=sbc.list_monitors_info()
  selected=[]
  for index,info in enumerate(infos,1):
   internal=info['method'].__name__=='WMI'
   if selection in {'all','both'} or selection==str(index) or selection==('internal' if internal else 'external'):
    selected.append((index,info))
  if not selected:raise ValueError('That display was not found. Say “what is my current brightness” to list connected displays.')
  results=[];errors=[];levels=[]
  for index,info in selected:
   label=f'Monitor {index}' + (' (laptop)' if info['method'].__name__=='WMI' else ' (external)')
   try:
    device=sbc.Display.from_dict(info);before=device.get_brightness();actual=before
    if action!='brightness_status':
     wanted=int(target) if action=='brightness' else max(0,min(100,before+(int(target or '10') if action=='brightness_up' else -int(target or '10'))))
     device.set_brightness(wanted)
     for attempt in range(5):
      time.sleep(.12 if attempt==0 else .2);actual=device.get_brightness()
      if abs(actual-wanted)<=1:break
     if abs(actual-wanted)>1:raise RuntimeError(f'requested {wanted}%, but the display still reports {actual}%')
    results.append(f'{label}: {actual}%.')
    levels.append(actual)
   except Exception as exc:errors.append(f'{label} did not change: {exc}')
  if errors:raise RuntimeError(' '.join(results+errors))
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

def execute(command):
 command=validate(command)
 if command['action'].startswith('brightness'):return brightness(command['action'],command['target'],command['display'])
 with com_thread():return _audio(command['action'],command['target'])
