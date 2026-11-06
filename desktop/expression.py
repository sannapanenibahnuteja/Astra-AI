"""Bounded delivery cues; expressive synthesis is not subjective emotion."""
import re
from xml.sax.saxutils import escape

STYLES={'neutral':(0,0),'warm':(-3,2),'calm':(-8,-4),'bright':(6,6),'serious':(-3,-4)}


def choose(request,preferred='auto',enabled=True):
    if not enabled:return 'neutral'
    if preferred in STYLES:return preferred
    text=str(request).lower()
    if re.search(r'\b(stressed|overwhelmed|anxious|worried|sad|calm|comfort|frustrated)\b',text):return 'calm'
    if re.search(r'\b(celebrate|excited|great news|congratulat|happy|funny|joke)\b',text):return 'bright'
    if re.search(r'\b(serious|urgent|emergency|precise)\b',text):return 'serious'
    return 'warm'


def prosody(text,style):
    rate,pitch=STYLES.get(style,STYLES['neutral'])
    if style=='neutral':return ''
    return f'<prosody rate="{rate:+d}%" pitch="{pitch:+d}%">{escape(str(text))}</prosody>'
