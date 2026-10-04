"""Opt-in outbound reminder announcements via the user's Twilio account."""
import base64
import json
import re
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from xml.sax.saxutils import escape


def config(root):
    path=root/'phone-calls.json'
    if not path.exists(): raise ValueError('Set up your calling account in Settings → Phone & reminders first.')
    cfg=json.loads(path.read_text(encoding='utf-8'))
    if cfg.get('enabled') is not True or not re.fullmatch(r'AC[0-9a-fA-F]{32}',cfg.get('account_sid','')) or not cfg.get('auth_token'):
        raise ValueError('Enable phone calls and enter your Twilio account SID and auth token in phone-calls.json.')
    for key in ('from_number','to_number'):
        if not re.fullmatch(r'\+[1-9]\d{7,14}',cfg.get(key,'')): raise ValueError('Use international +country-code phone numbers in phone-calls.json.')
    return cfg


def provider_error(exc):
    if isinstance(exc, HTTPError):
        detail = ''
        try:
            body = exc.read().decode('utf-8', errors='replace')
            payload = json.loads(body)
            detail = payload.get('message') or payload.get('error') or ''
            code = payload.get('code')
            if code:
                detail = f'Twilio error {code}: {detail}' if detail else f'Twilio error {code}'
        except Exception:
            detail = exc.reason or ''
        if detail:
            detail = re.sub(r'AC[0-9a-fA-F]{32}', 'AC...redacted', detail)
            detail = re.sub(r'(?<!\w)\+[1-9]\d{7,14}(?!\w)', '+...redacted', detail)
            return f'Call submission failed ({exc.code}): {detail[:220]}'
        return f'Call submission failed with HTTP {exc.code}. Check Twilio logs before retrying.'
    if isinstance(exc, URLError):
        reason = str(getattr(exc, 'reason', exc))
        return f'Call submission could not reach Twilio: {reason[:220]}'
    return 'Call submission failed or its outcome is uncertain.'


def submit(root,text):
    cfg=config(root)
    twiml='<Response><Say voice="Polly.Joanna-Neural">'+escape("Hi, it's Bob. Here's your reminder: "+text)+'</Say></Response>'
    body=urlencode({'To':cfg['to_number'],'From':cfg['from_number'],'Twiml':twiml,'Timeout':'30','TimeLimit':'90'}).encode()
    auth=base64.b64encode((cfg['account_sid']+':'+cfg['auth_token']).encode()).decode()
    request=Request('https://api.twilio.com/2010-04-01/Accounts/'+cfg['account_sid']+'/Calls.json',data=body,
                    headers={'Authorization':'Basic '+auth,'Content-Type':'application/x-www-form-urlencoded'})
    try:
        with urlopen(request,timeout=20) as response: result=json.load(response)
    except Exception as exc:
        raise RuntimeError(provider_error(exc)+' Check Twilio logs before retrying; Bob will not automatically redial.') from None
    if not re.fullmatch(r'CA[0-9a-fA-F]{32}',result.get('sid','')): raise RuntimeError('Call provider did not return a valid call ID; check its logs before retrying.')
    return result['sid']
