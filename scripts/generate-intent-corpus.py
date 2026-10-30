"""Build reproducible labeled conversational examples; this does not train weights."""
import json
from pathlib import Path


def corpus():
    selectors={'laptop screen':'internal','external monitor':'external','second monitor':'2',
               'first monitor':'1','upper screen':'top','primary screen':'primary'}
    templates=["Could you put my {screen} at {level} percent?",
        "I'd like the brightness on the {screen} to be {level}, please.",
        "The {screen} is too bright. Set it to {level} percent.",
        "Can you get the {screen} brightness to {level}?",
        "Please leave the other displays alone and set the {screen} to {level} percent.",
        "Actually, make the {screen} {level} percent bright.",
        "For the {screen}, I want {level} percent brightness.",
        "Change only my {screen} brightness to {level}."]
    for screen,display in selectors.items():
        for level in range(5,100,5):
            for template in templates:
                yield {'text':template.format(screen=screen,level=level),'actions':[{'action':'brightness','target':str(level),'display':display}]}
        for direction,action in [('down','brightness_down'),('up','brightness_up')]:
            for delta in (5,10,15,20):
                for text in (f'Could you turn the {screen} {direction} by {delta} percent?',
                             f'Change the {screen} brightness {direction} by {delta}, please.'):
                    yield {'text':text,'actions':[{'action':action,'target':str(delta),'display':display}]}
    for text in ("Don't change the external brightness; explain what DDC/CI means.",
                 'Tell me how brightness controls work. Do not change anything.',
                 'What does dimmer mean?', 'Can Bob adjust individual monitors?'):
        yield {'text':text,'actions':[]}


if __name__=='__main__':
    root=Path(__file__).resolve().parents[1]
    path=root/'tests/fixtures/natural-brightness-intents.jsonl'
    path.parent.mkdir(parents=True,exist_ok=True)
    rows=list(corpus())
    path.write_text(''.join(json.dumps(row)+'\n' for row in rows),encoding='utf-8')
    print(f'{len(rows)} labeled evaluation examples: {path}')
