import json,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from desktop.runtime import Runtime
from desktop import devices
from unittest.mock import patch
r=Runtime('.cache/routine-device-test');id=r.new_conversation()
with devices.com_thread():
 import screen_brightness_control as sbc
 screens=[sbc.Display.from_dict(i) for i in sbc.list_monitors_info()]
 levels=[d.get_brightness() for d in screens]
 from pycaw.pycaw import AudioUtilities
 speaker=AudioUtilities.GetSpeakers();volume=speaker.EndpointVolume
 old_volume=round(volume.GetMasterVolumeLevelScalar()*100);old_mute=volume.GetMute()
 try:
  parts=[f'set monitor {i+1} brightness to {max(5,old-5)}' for i,old in enumerate(levels)]
  parts.append(f'set volume of {max(0,old_volume-5)}%')
  with patch('desktop.runtime.ChatConnection',side_effect=AssertionError('Fast path must not call Ollama')):
   start=time.monotonic();job=r.start_chat(id,' and '.join(parts),True)
   while not (result:=r.poll_chat(job))['done']:time.sleep(.03)
   assert not result['error'],result
   assert id not in r._pending
   print(json.dumps({'seconds':round(time.monotonic()-start,2),**result}))
 finally:
  for screen,old in zip(screens,levels):screen.set_brightness(old)
  volume.SetMasterVolumeLevelScalar(old_volume/100,None);volume.SetMute(old_mute,None)
 del volume,speaker
