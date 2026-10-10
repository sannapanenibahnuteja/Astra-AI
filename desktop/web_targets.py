"""Known web services and explicit addresses; never invent a brand's domain."""
import re

SERVICES = {
    'youtube':'https://www.youtube.com', 'google':'https://www.google.com',
    'github':'https://github.com', 'spotify':'https://open.spotify.com',
    'netflix':'https://www.netflix.com', 'whatsapp':'https://web.whatsapp.com',
    'telegram':'https://web.telegram.org', 'discord':'https://discord.com/app',
    'gmail':'https://mail.google.com', 'outlook':'https://outlook.live.com',
    'instagram':'https://www.instagram.com', 'facebook':'https://www.facebook.com',
    'x':'https://x.com', 'reddit':'https://www.reddit.com',
    'amazon':'https://www.amazon.in', 'prime video':'https://www.primevideo.com',
    'chatgpt':'https://chatgpt.com', 'notion':'https://www.notion.so',
    'canva':'https://www.canva.com', 'figma':'https://www.figma.com',
    'google docs':'https://docs.google.com', 'google drive':'https://drive.google.com',
    'google maps':'https://maps.google.com', 'google calendar':'https://calendar.google.com',
    'microsoft teams':'https://teams.microsoft.com', 'zoom':'https://app.zoom.us',
    'slack':'https://app.slack.com', 'youtube music':'https://music.youtube.com',
}
ALIASES={'you tube':'youtube','you-tube':'youtube','yt':'youtube','spot ify':'spotify',
         'what sapp':'whatsapp','whats app':'whatsapp','twitter':'x','g mail':'gmail',
         'google mail':'gmail','chat gpt':'chatgpt','teams':'microsoft teams','primevideo':'prime video',
         'you tube music':'youtube music'}


def resolve(target):
    """Return canonical service/address and whether a web version was explicit."""
    target=target.strip()
    explicit=bool(re.search(r'\b(?:website|web site|web app|web version|online|in (?:the )?browser)\b',target,re.I))
    target=re.sub(r'^(?:the |a )','',target,flags=re.I)
    target=re.sub(r'^(?:website|web site|web app|web version)(?: for| of)?\s+','',target,flags=re.I)
    # Resolve spoken brand aliases before removing suffixes such as 'app'.
    target=ALIASES.get(target.casefold(),target)
    target=re.sub(r'\s+(?:website|web site|web app|web version|app|application|online|in (?:the )?browser)$','',target,flags=re.I)
    key=ALIASES.get(target.casefold(),target.casefold())
    if key in SERVICES: return key,SERVICES[key],explicit
    if re.fullmatch(r'https?://\S+',target,re.I): return target,target,True
    if re.fullmatch(r'(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z]{2,63}(?:/[^\s]*)?',target,re.I):
        return target,'https://'+target,True
    return key,None,explicit
