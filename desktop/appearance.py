"""Validated, reversible workspace appearance. No generated CSS or code execution."""
import re
from difflib import get_close_matches

DEFAULTS = dict(accent='violet', background='black', sidebar='expanded', details=False,
                font_size='medium', font_family='system', density='comfortable', corners='round',
                orb_size='medium', orb_color='multicolor', orb_speed='calm', orb_visible=True,
                motion='playful', suggestions=False, message_style='plain', composer='comfortable',
                chat_width='focused', status=True, sidebar_color='default', composer_color='default')
CHOICES = dict(accent=('violet','mint','blue','rose','amber','ice'),
 background=('black','graphite','midnight'), sidebar=('expanded','compact','hidden'),
 font_size=('small','medium','large','extra large'), font_family=('system','rounded','mono'),
 density=('compact','comfortable','roomy'), corners=('round','soft','square'),
 orb_size=('small','medium','large'),orb_color=('multicolor','accent'),orb_speed=('calm','balanced','lively'),
 motion=('off','subtle','playful'),message_style=('plain','bubbles'),composer=('compact','comfortable'),
 chat_width=('focused','wide'),sidebar_color=('default','black','graphite','midnight'),
 composer_color=('default','black','graphite','midnight'))
PRESETS = dict(focus=dict(details=False,suggestions=False,sidebar='compact',motion='subtle'),
 studio=dict(details=True,suggestions=True,sidebar='expanded',motion='subtle',chat_width='wide'),
 playful=dict(accent='rose',motion='playful',orb_speed='lively',corners='round'))

def validate(patch):
    if not isinstance(patch,dict) or any(k not in DEFAULTS for k in patch):raise ValueError('Unknown appearance setting.')
    for key,value in patch.items():
        if key in CHOICES:
            if not isinstance(value,str) or value not in CHOICES[key]:raise ValueError('Choose a supported '+key.replace('_',' ')+'.')
        elif type(value) is not bool:raise ValueError('Invalid appearance switch.')
    return patch

def merge(current,patch):
    validate(patch)
    return {**DEFAULTS,**current,**patch}

def _request(text):
    """Only explicit UI requests; leave dictation, app actions and quoted text alone."""
    value=str(text).strip().lower().rstrip('.!?')
    if any(c in value for c in ('"',"'",'`')) or value.startswith(('type ','write ','search ','remember ')):return None
    value=re.sub(r'^(?:(?:hey|okay|ok)[ ,]+)?bob[, ]+','',value)
    value=re.sub(r'^(?:please |could you |can you |i want you to |actually[, ]+)+','',value)
    if value in ('reset appearance','reset the appearance','restore default appearance','reset my layout','reset the ui'):return dict(DEFAULTS)
    for name,patch in PRESETS.items():
        if value in (f'use {name} layout',f'switch to {name} layout',f'use the {name} layout'):return dict(patch)
    subjects={'accent':'accent','accent color':'accent','theme color':'accent','background':'background',
      'background color':'background','sidebar':'sidebar','navigation':'sidebar','text':'font_size','text size':'font_size',
      'font size':'font_size','font':'font_family','font family':'font_family','spacing':'density','density':'density',
      'corners':'corners','orb':'orb_size','orb size':'orb_size','orb color':'orb_color','orb speed':'orb_speed',
      'animations':'motion','animation':'motion','motion':'motion','messages':'message_style','message style':'message_style',
      'composer':'composer','input box':'composer','chat width':'chat_width','sidebar color':'sidebar_color',
      'composer color':'composer_color'}
    aliases={'purple':'violet','pink':'rose','green':'mint','silver':'ice','colorful':'multicolor','colourful':'multicolor',
      'colour':'color','minimal':'subtle','fun':'playful','smooth':'subtle','slow':'calm','fast':'lively',
      'bigger':'large','larger':'large','smaller':'small','rounded':'round','monospace':'mono',
      'normal':'medium','default':'medium','spacious':'roomy','bubble':'bubbles','on':'playful'}
    value=value.replace('colour','color')
    if value in ('make the ui simpler','make the interface simpler','declutter the ui','simplify the layout'):return dict(PRESETS['focus'])
    toggles={'orb':'orb_visible','the orb':'orb_visible','details':'details','details panel':'details','the details panel':'details',
      'suggestions':'suggestions','starter cards':'suggestions','status':'status','status labels':'status'}
    match=re.fullmatch(r'(show|hide|enable|disable|turn on|turn off) (.+)',value)
    if match:
        on=match[1] in ('show','enable','turn on');target=match[2]
        if target in toggles:return {toggles[target]:on}
        if target in ('sidebar','the sidebar','navigation'):return {'sidebar':'expanded' if on else 'hidden'}
        if target in ('animations','motion'):return {'motion':'playful' if on else 'off'}
    match=re.fullmatch(r'(?:set|change|make) (?:my |the )?(.+?)(?: to| into)? (extra large|[a-z]+)',value)
    if not match:return None
    subject=subjects.get(match[1]);raw=match[2]
    if not subject:return None
    raw=aliases.get(raw,raw)
    if subject in ('orb_color','orb_size') and raw in CHOICES['accent']:return {'accent':raw,'orb_color':'accent'}
    if subject=='font_size' and raw=='round':subject='font_family';raw='rounded'
    options=CHOICES.get(subject,())
    if raw not in options:
        near=get_close_matches(raw,options,n=2,cutoff=.82)
        if len(near)!=1:raise ValueError('For '+match[1]+', choose '+', '.join(options)+'.')
        raw=near[0]
    return {subject:raw}


def request(text):
    value=str(text).strip()
    parts=re.split(r'\s+(?:and then|and|then)\s+',value,flags=re.I)
    if len(parts)>1:
        changes=[_request(part) for part in parts]
        if not all(change is not None for change in changes):return None
        result={}
        for change in changes:result.update(change)
        return result
    return _request(value)


UI_WORDS=r'\b(?:ui|interface|layout|accent|theme|orb|sidebar|animations|appearance|composer|text size|font|spacing|corners|background)\b'

def semantic_candidate(text,history=()):
    value=str(text).lower().strip()
    correction=bool(re.match(r'^(?:actually|no[, ]+i meant|instead)\b',value))
    value=re.sub(r'^(?:actually[, ]+|no[, ]+i meant |instead[, ]+)+','',value)
    if not correction and not re.match(r'^(?:please |could you |can you )?(?:give|make|change|set|hide|show|use|switch|simplify|i want)\b',value):return False
    if re.search(r'\b(?:open|launch|delete|type|write|send|remind|schedule|call|volume|brightness|file|window|app|play)\b',value):return False
    if re.search(UI_WORDS,value):return True
    return bool((correction or re.search(r'\b(?:it|that)\b',value)) and any(re.search(UI_WORDS,row.get('content',''),re.I) for row in history[-3:] if row.get('role')=='user'))

def model_payload(current,text,history,settings):
    import json
    props={key:{'type':'string','enum':list(values)} for key,values in CHOICES.items()}
    props.update({key:{'type':'boolean'} for key in DEFAULTS if key not in CHOICES})
    schema={'type':'object','properties':{'patch':{'type':'object','properties':props,'additionalProperties':False},'question':{'type':'string'}},'required':['patch','question'],'additionalProperties':False}
    recent=[row for row in history[:-1] if re.search(UI_WORDS,row.get('content',''),re.I)][-2:]
    return {'model':settings['model'],'stream':True,'think':False,'keep_alive':settings['keep_alive'],
       'options':{'num_ctx':2048,'num_predict':256,'temperature':0},'format':schema,
       'messages':[{'role':'system','content':'Map only the requested Bob UI changes to a JSON patch. Preserve unrelated preferences. Use the schema enum values. Interpret clear color/style synonyms and follow-up corrections from context. No task execution, CSS, shell or code. If genuinely ambiguous or unsupported, return an empty patch and the smallest useful question. Otherwise question must be empty. Current appearance (data): '+json.dumps(current)},
         *[{'role':row['role'],'content':row['content'][:600]} for row in recent],{'role':'user','content':text}]}
