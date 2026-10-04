"""Persist private mobile pairing with Windows user-bound encryption."""
import json


def save(root, data):
    import win32crypt
    encrypted=win32crypt.CryptProtectData(json.dumps(data).encode(),'Bob mobile pairing',None,None,None,0)
    path=root/'mobile-pairing.dat'
    temporary=root/'mobile-pairing.tmp'
    temporary.write_bytes(encrypted);temporary.replace(path)


def load(root):
    import win32crypt
    path=root/'mobile-pairing.dat'
    if not path.exists(): return None
    _,plaintext=win32crypt.CryptUnprotectData(path.read_bytes(),None,None,None,0)
    return json.loads(plaintext)


def clear(root):
    (root/'mobile-pairing.dat').unlink(missing_ok=True)
