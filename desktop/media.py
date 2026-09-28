"""Music/video transport through Windows media sessions, without focus stealing."""
import json
import math
import os
from pathlib import Path
import re
import subprocess
import webbrowser
from urllib.parse import quote_plus
from desktop import files
from desktop.devices import number_words

ACTIONS = {'media_play','media_pause','media_stop','media_next','media_previous','media_seek',
           'media_forward','media_back','media_status','media_sessions','media_shuffle',
           'media_repeat','media_rate','media_open','media_search'}
EXTENSIONS = {'.mp3','.wav','.flac','.m4a','.aac','.ogg','.wma','.mp4','.mkv','.webm','.mov','.avi','.m4v'}

SCRIPT = r'''
$ErrorActionPreference='Stop'
[Console]::InputEncoding=[Text.UTF8Encoding]::new($false)
[Console]::OutputEncoding=[Text.UTF8Encoding]::new($false)
Add-Type -AssemblyName System.Runtime.WindowsRuntime
[Windows.Media.Control.GlobalSystemMediaTransportControlsSessionManager,Windows.Media.Control,ContentType=WindowsRuntime] | Out-Null
$cfg=[Console]::In.ReadToEnd() | ConvertFrom-Json
$asTask=[System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
 $_.Name -eq 'AsTask' -and $_.IsGenericMethod -and $_.GetGenericArguments().Count -eq 1 -and
 $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1'
} | Select-Object -First 1
function Await-Media($op,[Type]$type) {
 $task=$asTask.MakeGenericMethod($type).Invoke($null,@($op))
 if (-not $task.Wait(8000)) {throw 'The media app did not respond in time.'}
 return $task.Result
}
function Read-Session($session) {
 $info=$session.GetPlaybackInfo();$timeline=$session.GetTimelineProperties()
 $props=Await-Media ($session.TryGetMediaPropertiesAsync()) ([Windows.Media.Control.GlobalSystemMediaTransportControlsSessionMediaProperties])
 return @{app=$session.SourceAppUserModelId;title=$props.Title;artist=$props.Artist;
 state=$info.PlaybackStatus.ToString();position=$timeline.Position.TotalSeconds;
 start=$timeline.MinSeekTime.TotalSeconds;end=$timeline.MaxSeekTime.TotalSeconds;
 shuffle=$info.IsShuffleActive;repeat=[string]$info.AutoRepeatMode;rate=$info.PlaybackRate}
}
$manager=Await-Media ([Windows.Media.Control.GlobalSystemMediaTransportControlsSessionManager]::RequestAsync()) ([Windows.Media.Control.GlobalSystemMediaTransportControlsSessionManager])
$sessions=@($manager.GetSessions())
if ($cfg.action -eq 'media_sessions') {
 $rows=@($sessions | ForEach-Object {Read-Session $_})
 ConvertTo-Json -InputObject $rows -Depth 4 -Compress
 exit
}
if ($sessions.Count -eq 0) {throw 'No Windows media session is available. Start music or a video in a supported player first.'}
if ($cfg.window) {
 $exact=@($sessions | Where-Object {$_.SourceAppUserModelId -eq $cfg.window})
 if ($exact.Count) {$sessions=$exact} else {
  $sessions=@($sessions | Where-Object {
   $row=Read-Session $_
   $_.SourceAppUserModelId.IndexOf($cfg.window,[StringComparison]::OrdinalIgnoreCase) -ge 0 -or $row.title -eq $cfg.window
  })
 }
} else {
 $playing=@($sessions | Where-Object {$_.GetPlaybackInfo().PlaybackStatus.ToString() -eq 'Playing'})
 if ($playing.Count) {$sessions=$playing}
 elseif ($cfg.previous) {
  $remembered=@($sessions | Where-Object {$_.SourceAppUserModelId -eq $cfg.previous -and (Read-Session $_).title -eq $cfg.previous_title})
  if ($remembered.Count -eq 1) {$sessions=$remembered}
 }
}
if ($sessions.Count -ne 1) {throw 'The media player is missing or ambiguous. Say list media players, then name the app. Multiple browser tabs from one app may require selecting the tab in that browser.'}
$session=$sessions[0];$before=Read-Session $session
if ($cfg.action -eq 'media_status') {$before | ConvertTo-Json -Compress;exit}
$controls=$session.GetPlaybackInfo().Controls
$support=@{media_play='IsPlayEnabled';media_pause='IsPauseEnabled';media_stop='IsStopEnabled';media_next='IsNextEnabled';media_previous='IsPreviousEnabled';media_seek='IsPlaybackPositionEnabled';media_forward='IsPlaybackPositionEnabled';media_back='IsPlaybackPositionEnabled';media_shuffle='IsShuffleEnabled';media_repeat='IsRepeatEnabled';media_rate='IsPlaybackRateEnabled'}
$desired=@{media_play='Playing';media_pause='Paused';media_stop='Stopped'}[$cfg.action]
if ($desired -and $before.state -eq $desired) {$before | ConvertTo-Json -Compress;exit}
if (-not $controls.($support[$cfg.action])) {throw "This player does not expose $($cfg.action.Replace('media_','')) control to Windows. No fallback keystroke was sent."}
$value=[double]0
switch ($cfg.action) {
 media_play {$operation=$session.TryPlayAsync()}
 media_pause {$operation=$session.TryPauseAsync()}
 media_stop {$operation=$session.TryStopAsync()}
 media_next {$operation=$session.TrySkipNextAsync()}
 media_previous {$operation=$session.TrySkipPreviousAsync()}
 media_shuffle {$operation=$session.TryChangeShuffleActiveAsync($cfg.value -eq 'on')}
 media_repeat {
  [Windows.Media.MediaPlaybackAutoRepeatMode,Windows.Media,ContentType=WindowsRuntime] | Out-Null
  $mode=@{off=[Windows.Media.MediaPlaybackAutoRepeatMode]::None;one=[Windows.Media.MediaPlaybackAutoRepeatMode]::Track;all=[Windows.Media.MediaPlaybackAutoRepeatMode]::List}[$cfg.value]
  $operation=$session.TryChangeAutoRepeatModeAsync($mode)
 }
 media_rate {$operation=$session.TryChangePlaybackRateAsync([double]$cfg.value)}
 default {
  $value=[double]$cfg.value
  if ($cfg.action -eq 'media_forward') {$value=$before.position+$value}
  if ($cfg.action -eq 'media_back') {$value=$before.position-$value}
  if ($before.end -le $before.start) {throw 'This stream exposes no seekable timeline, possibly because it is live.'}
  $value=[Math]::Max($before.start,[Math]::Min($before.end,$value))
  $operation=$session.TryChangePlaybackPositionAsync([long]($value*10000000))
 }
}
if (-not (Await-Media $operation ([bool]))) {throw 'The media player rejected the playback request.'}
for ($i=0;$i -lt 12;$i++) {
 Start-Sleep -Milliseconds 150
 $after=Read-Session $session
 $verified=$false
 switch ($cfg.action) {
  media_play {$verified=$after.state -eq 'Playing'}
  media_pause {$verified=$after.state -eq 'Paused'}
  media_stop {$verified=$after.state -eq 'Stopped'}
  media_next {$verified=$after.title -ne $before.title}
  media_previous {$verified=$after.title -ne $before.title -or ($before.position -gt 3 -and $after.position -lt 3)}
  media_shuffle {$verified=$after.shuffle -eq ($cfg.value -eq 'on')}
  media_repeat {$verified=$after.repeat -eq $mode.ToString()}
  media_rate {$verified=[Math]::Abs([double]$after.rate-[double]$cfg.value) -lt .01}
  default {$verified=[Math]::Abs($after.position-$value) -lt 3}
 }
 if ($verified) {$after | ConvertTo-Json -Compress;exit}
}
throw 'The player accepted the command but did not report the requested change. Check playback; Bob cannot confirm success.'
'''


def parse(text):
    text = text.strip()
    lower = text.lower()
    exact = {'play':'media_play','play music':'media_play','play some music':'media_play','resume':'media_play',
             'resume playback':'media_play','pause':'media_pause','pause it':'media_pause','pause the music':'media_pause',
             'pause the video':'media_pause','stop the music':'media_stop','stop playback':'media_stop',
             'stop the video':'media_stop','next track':'media_next','next song':'media_next','skip this song':'media_next',
             'previous track':'media_previous','previous song':'media_previous','what is playing':'media_status',
             "what's playing":'media_status','now playing':'media_status','list media players':'media_sessions',
             'show media players':'media_sessions','restart the song':'media_seek','restart the video':'media_seek'}
    if lower in exact:
        return {'action':exact[lower],'target':'','value':'0' if exact[lower]=='media_seek' else '', 'library_fallback':lower in ('play music','play some music')}
    match=re.fullmatch(r'(pause|resume|stop|play) (?:the |my )?(?:current )?(?:video|music|song|playback)',lower)
    if match:return {'action':{'pause':'media_pause','resume':'media_play','stop':'media_stop','play':'media_play'}[match[1]],'target':''}
    match = re.fullmatch(r'(pause|resume|stop|play|next track|previous track)(?: (?:music|video|playback))? (?:in|on) (.+)', text,re.I)
    if match:
        return {'action':{'pause':'media_pause','resume':'media_play','stop':'media_stop','play':'media_play','next track':'media_next','previous track':'media_previous'}[match[1].lower()],'target':'','window':match[2]}
    match = re.fullmatch(r'(?:seek to|skip to|go to|fast forward|skip forward|rewind|go back)(?: (?:by|to))? (.+?)(?: (?:in|on) (.+))?',text,re.I)
    if match:
        value = number_words(match[1].lower())
        timestamp = re.fullmatch(r'(\d+):(\d{2})(?::(\d{2}))?',value)
        if timestamp:
            parts=[int(p) for p in timestamp.groups() if p is not None]
            if any(p>=60 for p in parts[1:]): raise ValueError('Use minutes:seconds or hours:minutes:seconds.')
            seconds=sum(n*60**i for i,n in enumerate(reversed(parts)))
        else:
            quantity=re.fullmatch(r'(\d+(?:\.\d+)?)\s*(seconds?|minutes?|hours?)?',value)
            if not quantity:return None
            seconds=float(quantity[1]) * (3600 if (quantity[2] or '').startswith('hour') else 60 if (quantity[2] or '').startswith('minute') else 1)
        action='media_forward' if lower.startswith(('fast forward','skip forward')) else 'media_back' if lower.startswith(('rewind','go back')) else 'media_seek'
        return {'action':action,'target':'','value':str(seconds),'window':match[2] or ''}
    match=re.fullmatch(r'(?:turn )?shuffle (on|off)(?: (?:in|on) (.+))?',text,re.I)
    if match:return {'action':'media_shuffle','target':'','value':match[1].lower(),'window':match[2] or ''}
    match=re.fullmatch(r'repeat (one|all|off)(?: (?:in|on) (.+))?',text,re.I)
    if match:return {'action':'media_repeat','target':'','value':match[1].lower(),'window':match[2] or ''}
    match=re.fullmatch(r'(?:set )?(?:playback |video )?speed(?: to)? (\d+(?:\.\d+)?)(?:x| times)?(?: (?:in|on) (.+))?',text,re.I)
    if match:return {'action':'media_rate','target':'','value':match[1],'window':match[2] or ''}
    match=re.fullmatch(r'(?:search for|find) (?:music|song|video) (.+?)(?: on (youtube|spotify))?',text,re.I)
    if match:return {'action':'media_search','target':match[1],'window':match[2] or 'youtube'}
    match=re.fullmatch(r'play (?:file |song |music file |video file )?(.+)',text,re.I)
    if match:
        if match[1].lower() in ('it','it again','the video','the music'):return {'action':'media_play','target':''}
        return {'action':'media_open','target':match[1]}
    return None


def validate(command):
    result={k:command.get(k,'') for k in ('action','target','value','window')}
    if result['action'] not in ACTIONS or any(not isinstance(v,str) or len(v)>2048 or '\x00' in v for v in result.values()):
        raise ValueError('Invalid media command.')
    action=result['action']
    if action in ('media_seek','media_forward','media_back','media_rate'):
        try: value=float(result['value'])
        except ValueError as exc:raise ValueError('Give a numeric playback position or rate.') from exc
        minimum,maximum=(.25,4) if action=='media_rate' else (0,604800)
        if not math.isfinite(value) or not minimum<=value<=maximum:raise ValueError('Playback value is outside the supported range.')
    if action=='media_shuffle' and result['value'] not in ('on','off'):raise ValueError('Shuffle must be on or off.')
    if action=='media_repeat' and result['value'] not in ('one','all','off'):raise ValueError('Repeat must be one, all or off.')
    if action in ('media_open','media_search') and not result['target'].strip():raise ValueError('Name the music or video.')
    result['confirm']=False
    result['library_fallback']=command.get('library_fallback') is True
    return result


def native(command, context):
    executable=os.path.join(os.environ['SystemRoot'],'System32','WindowsPowerShell','v1.0','powershell.exe')
    payload={**command,'previous':context.get('last_media_app',''),'previous_title':context.get('last_media_title','')}
    result=subprocess.run([executable,'-NoProfile','-NonInteractive','-Command',SCRIPT],
                          input=json.dumps(payload).encode('utf-8'),capture_output=True,timeout=40,
                          creationflags=subprocess.CREATE_NO_WINDOW)
    if result.returncode:
        lines=result.stderr.decode('utf-8',errors='replace').strip().splitlines()
        raise RuntimeError(lines[0][:450] if lines else 'Windows media control failed.')
    return json.loads(result.stdout.decode('utf-8-sig'))


def local_media(query, context):
    if Path(query.strip('"')).is_absolute() or query.lower() in files.REFERENCES:
        paths=files.sources(query,context)
    else:
        root=files.known_folder('music')
        paths=[];scanned=0
        for directory,folders,names in os.walk(root,followlinks=False):
            folders[:]=[n for n in folders if not (Path(directory)/n).is_symlink() and not (Path(directory)/n).is_junction()]
            for name in names:
                scanned+=1
                if Path(name).suffix.lower() in EXTENSIONS and (query=='*' or query.casefold() in Path(name).stem.casefold()):
                    paths.append(Path(directory)/name)
                if scanned>=5000 or len(paths)>=20:break
            if scanned>=5000 or len(paths)>=20:break
        if query=='*':paths=sorted(paths)[:1]
    if not paths:raise ValueError('No matching local media found in Music. Give a full file path, or say “search for music [title] on YouTube”.')
    if len(paths)!=1:raise ValueError('Several local tracks match. Use the exact name or path: '+ '; '.join(str(p) for p in paths[:6]))
    path=files.path_for(str(paths[0]),context)
    if not path.is_file() or path.suffix.lower() not in EXTENSIONS:raise ValueError('Choose an existing audio or video file.')
    os.startfile(str(path))
    context['last_media_file']=str(path)
    return f'Opened {path.name} in your default media player. Playback depends on the player; say “what is playing” to check.'


def execute(command, context):
    command=validate(command);action=command['action']
    if action=='media_open':return local_media(command['target'],context)
    if action=='media_search':
        service=command['window'].lower() or 'youtube'
        if service not in ('youtube','spotify'):raise ValueError('Choose YouTube or Spotify for media search.')
        url=('https://www.youtube.com/results?search_query=' if service=='youtube' else 'https://open.spotify.com/search/')+quote_plus(command['target'])
        if not webbrowser.open(url):raise RuntimeError('Windows could not open your browser.')
        return f'Opened {service} search results for {command["target"]}. Choose a result to start playback; this search does not autoplay.'
    if command['library_fallback']:
        sessions=native({'action':'media_sessions'},context)
        if not sessions:return local_media('*',context)
    result=native(command,context)
    if action=='media_sessions':
        return 'Available media players:\n'+'\n'.join(f"{r['app']}: {r['title'] or 'untitled'} ({r['state']})" for r in result) if result else 'No Windows media sessions are available. Start a track or video first.'
    context['last_media_app']=result['app']
    context['last_media_title']=result.get('title','')
    title=result.get('title') or 'Untitled media'
    if action=='media_status':
        return f"{title}"+(f" — {result['artist']}" if result.get('artist') else '')+f". {result['state']} in {result['app']}, at {round(result['position'])} seconds."
    if action in ('media_seek','media_forward','media_back'):return f"Playback is at {round(result['position'])} seconds."
    if action=='media_shuffle':return f"Shuffle is {command['value']}."
    if action=='media_repeat':return f"Repeat is {command['value']}."
    if action=='media_rate':return f"Playback speed is {command['value']}×."
    return f"{result['state']}: {title}."
