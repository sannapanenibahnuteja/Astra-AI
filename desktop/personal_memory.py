"""Conservative local extraction of explicit personal statements, never inferred facts."""
import re


def facts(message):
    if len(message)>4000 or re.search(r'\b(?:not|never|if|maybe|might|pretend|example|quote|said|password|pin|secret|credit card)\b',message,re.I):
        return []
    results=[]
    for sentence in re.split(r'[.!?;\n]+',message):
        sentence=sentence.strip()
        patterns=[
            ('preferred name',r"(?:my name is|call me) ([\w -]{1,60})"),
            ('favorite {0}',r"my (?:favorite|favourite) (food|drink|color|colour|music|movie|place|restaurant) is (.{1,200})"),
            ('preference',r"i (?:prefer|like|love) (.{1,200})"),
            ('routine',r"i (?:usually|normally|always) (.{1,200})"),
            ('relationship: {0}',r"([\w -]{1,60}) is my (mother|father|mum|mom|dad|brother|sister|son|daughter|wife|husband|partner|friend|colleague|manager|cousin|roommate)"),
            ('relationship: {1}',r"my (mother|father|mum|mom|dad|brother|sister|son|daughter|wife|husband|partner|friend|colleague|manager|cousin|roommate) is ([\w -]{1,60})"),
        ]
        for key,pattern in patterns:
            match=re.fullmatch(pattern,sentence,re.I)
            if not match: continue
            parts=match.groups()
            if key.startswith('relationship'):
                person=parts[1] if key.endswith('{1}') else parts[0]
                relation=parts[0] if key.endswith('{1}') else parts[1]
                results.append(('relationship: '+person.strip().casefold(),relation.casefold()))
            else:
                results.append((key.format(*parts),parts[-1].strip()))
            break
    return results[:5]


def learn(store, identity, message, speaker, spoken):
    context=store.context(identity)
    profile=context.get('voice_profile')
    if not store.settings().get('conversation_memory',True) or not profile or context.get('unidentified_voice'):
        return []
    if spoken and (speaker.get('state')!='matched' or speaker.get('profile_id')!=profile):
        return []
    saved=[]
    for key,value in facts(message):
        if next((row['value'] for row in store.memories(profile) if row['key']==key),None)==value: continue
        store.remember(key,value,profile); saved.append(key)
    return saved
