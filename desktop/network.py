"""Windows radios and saved Wi-Fi connections, with native state verification."""
import ctypes as ct
import json
from ctypes import wintypes as wt
import os
import subprocess
import time


RADIO_SCRIPT = r"""
$ErrorActionPreference = 'Stop'
[Console]::InputEncoding = [Text.UTF8Encoding]::new($false)
[Console]::OutputEncoding = [Text.UTF8Encoding]::new($false)
Add-Type -AssemblyName System.Runtime.WindowsRuntime
[Windows.Devices.Radios.Radio,Windows.System.Devices,ContentType=WindowsRuntime] | Out-Null
$cfg = [Console]::In.ReadToEnd() | ConvertFrom-Json
$asTask = [System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
    $_.Name -eq 'AsTask' -and $_.IsGenericMethod -and $_.GetGenericArguments().Count -eq 1 -and
    $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1'
} | Select-Object -First 1
function Await-Radio($operation, [Type]$resultType) {
    $task = $asTask.MakeGenericMethod($resultType).Invoke($null, @($operation))
    if (-not $task.Wait(10000)) { throw 'Windows radio request timed out.' }
    return $task.Result
}
$kind = if ($cfg.kind -eq 'bluetooth') { 'Bluetooth' } else { 'WiFi' }
$all = Await-Radio ([Windows.Devices.Radios.Radio]::GetRadiosAsync()) ([System.Collections.Generic.IReadOnlyList[Windows.Devices.Radios.Radio]])
$radios = @($all | Where-Object { $_.Kind.ToString() -eq $kind })
if ($radios.Count -eq 0) { throw "Windows exposes no $kind radio on this PC." }
if ($cfg.state) {
    $access = Await-Radio ([Windows.Devices.Radios.Radio]::RequestAccessAsync()) ([Windows.Devices.Radios.RadioAccessStatus])
    if ($access.ToString() -ne 'Allowed') { throw "Windows denied access to $kind. Check device policy and Windows Settings." }
    $desired = if ($cfg.state -eq 'on') { [Windows.Devices.Radios.RadioState]::On } else { [Windows.Devices.Radios.RadioState]::Off }
    foreach ($radio in $radios) {
        if ($radio.State -ne $desired) {
            $result = Await-Radio ($radio.SetStateAsync($desired)) ([Windows.Devices.Radios.RadioAccessStatus])
            if ($result.ToString() -ne 'Allowed') { throw "Windows blocked changing $($radio.Name). Some radios may already have changed." }
        }
        for ($i=0; $i -lt 20 -and $radio.State -ne $desired; $i++) { Start-Sleep -Milliseconds 100 }
        if ($radio.State -ne $desired) { throw "$($radio.Name) did not reach $($cfg.state). Check its hardware switch or airplane mode." }
    }
}
$rows = @($radios | ForEach-Object { "$($_.Name) is $($_.State.ToString().ToLowerInvariant())" })
(($rows -join '; ') + '.') | ConvertTo-Json -Compress
"""


def radio(kind, state=None):
    # Windows Runtime lives in a short-lived OS helper: importing PyWinRT into
    # Whisper's process can crash ONNX Runtime during DLL initialization.
    if kind not in ('bluetooth','wifi') or state not in (None,'on','off'):
        raise ValueError('Choose Bluetooth or Wi-Fi and on/off.')
    powershell = os.path.join(os.environ['SystemRoot'], 'System32', 'WindowsPowerShell', 'v1.0', 'powershell.exe')
    result = subprocess.run([powershell,'-NoProfile','-NonInteractive','-Command',RADIO_SCRIPT],
                            input=json.dumps({'kind':kind,'state':state}).encode('utf-8'),
                            capture_output=True, timeout=35, creationflags=subprocess.CREATE_NO_WINDOW)
    if result.returncode:
        detail = result.stderr.decode('utf-8',errors='replace').strip().splitlines()
        raise RuntimeError(detail[0][:350] if detail else 'Windows could not access the radio.')
    try: return json.loads(result.stdout.decode('utf-8-sig'))
    except ValueError as exc: raise RuntimeError('Windows returned an unreadable radio status; no success was confirmed.') from exc


class GUID(ct.Structure):
    _fields_ = [('data1', wt.DWORD), ('data2', wt.WORD), ('data3', wt.WORD), ('data4', ct.c_ubyte * 8)]


class Interface(ct.Structure):
    _fields_ = [('guid', GUID), ('description', wt.WCHAR * 256), ('state', wt.DWORD)]


class Profile(ct.Structure):
    _fields_ = [('name', wt.WCHAR * 256), ('flags', wt.DWORD)]


class Connection(ct.Structure):
    # Only the fixed leading fields of WLAN_CONNECTION_ATTRIBUTES are needed.
    _fields_ = [('state', wt.DWORD), ('mode', wt.DWORD), ('profile', wt.WCHAR * 256)]


def snapshot():
    """Locale-independent interface/profile inventory; never requests Wi-Fi keys."""
    dll = ct.WinDLL('wlanapi')
    dll.WlanOpenHandle.argtypes = [wt.DWORD, ct.c_void_p, ct.POINTER(wt.DWORD), ct.POINTER(wt.HANDLE)]
    dll.WlanEnumInterfaces.argtypes = [wt.HANDLE, ct.c_void_p, ct.POINTER(ct.c_void_p)]
    dll.WlanGetProfileList.argtypes = [wt.HANDLE, ct.POINTER(GUID), ct.c_void_p, ct.POINTER(ct.c_void_p)]
    dll.WlanQueryInterface.argtypes = [wt.HANDLE, ct.POINTER(GUID), ct.c_int, ct.c_void_p, ct.POINTER(wt.DWORD), ct.POINTER(ct.c_void_p), ct.POINTER(ct.c_int)]
    dll.WlanFreeMemory.argtypes = [ct.c_void_p]
    dll.WlanCloseHandle.argtypes = [wt.HANDLE, ct.c_void_p]
    handle, version = wt.HANDLE(), wt.DWORD()
    code = dll.WlanOpenHandle(2, None, ct.byref(version), ct.byref(handle))
    if code:
        raise RuntimeError(f'Windows Wi-Fi service is unavailable (error {code}).')
    result, memory = [], ct.c_void_p()
    try:
        code = dll.WlanEnumInterfaces(handle, None, ct.byref(memory))
        if code:
            raise RuntimeError(f'Could not enumerate Wi-Fi adapters (error {code}).')
        count = wt.DWORD.from_address(memory.value).value
        entries = (Interface * count).from_address(memory.value + 8)
        for entry in entries:
            profiles, connection = ct.c_void_p(), ct.c_void_p()
            row = {'adapter':entry.description, 'state':int(entry.state), 'profile':'', 'profiles':[]}
            try:
                if dll.WlanGetProfileList(handle, ct.byref(entry.guid), None, ct.byref(profiles)) == 0:
                    n = wt.DWORD.from_address(profiles.value).value
                    row['profiles'] = [p.name for p in (Profile * n).from_address(profiles.value + 8)]
                size, opcode = wt.DWORD(), ct.c_int()
                row['query_error'] = dll.WlanQueryInterface(handle, ct.byref(entry.guid), 7, None, ct.byref(size), ct.byref(connection), ct.byref(opcode))
                if row['query_error'] == 0:
                    row['profile'] = ct.cast(connection, ct.POINTER(Connection)).contents.profile
            finally:
                if profiles.value: dll.WlanFreeMemory(profiles)
                if connection.value: dll.WlanFreeMemory(connection)
            result.append(row)
    finally:
        if memory.value: dll.WlanFreeMemory(memory)
        dll.WlanCloseHandle(handle, None)
    return result


def wifi(action, target='', context=None):
    context = context if context is not None else {}
    rows = snapshot()
    if not rows:
        raise RuntimeError('Windows has no available Wi-Fi adapter.')
    if action == 'wifi_status':
        for row in rows:
            if row['state'] == 1 and row['profile']:
                context['last_wifi'] = row['profile']
        return '\n'.join((f"{r['adapter']}: connected to {r['profile']}." if r['profile'] else f"{r['adapter']}: connected; Windows withheld the network name (error {r.get('query_error', 'unknown')}). Check Windows location permissions or administrator policy.") if r['state'] == 1 else f"{r['adapter']}: not connected." for r in rows)
    if action == 'wifi_profiles':
        return 'Saved Wi-Fi networks: ' + (', '.join(sorted({p for r in rows for p in r['profiles']})) or 'none') + '.'
    if len(rows) != 1:
        raise ValueError('More than one Wi-Fi adapter is present. Choose the connection in Windows Wi-Fi Settings.')
    row = rows[0]
    if row['profile']:
        context['last_wifi'] = row['profile']
    if action == 'wifi_connect':
        if row.get('query_error') == 5:
            raise RuntimeError('Windows denied access to connection verification (error 5). No connection change was attempted. Check location permissions or administrator policy in Windows Settings.')
        target = context.get('last_wifi', '') if target.lower() in ('', 'it', 'that', 'again', 'previous') else target
        matches = [p for p in row['profiles'] if p.strip().casefold() == target.strip().casefold()]
        if len(matches) != 1:
            raise ValueError('Name a saved Wi-Fi network. Say “list saved Wi-Fi networks”. For a new network, enter its password in Windows Wi-Fi Settings first.')
        target = matches[0]
        arguments = ['wlan', 'connect', 'name=' + target]
    else:
        arguments = ['wlan', 'disconnect']
    command = [os.path.join(os.environ['SystemRoot'], 'System32', 'netsh.exe'), *arguments]
    result = subprocess.run(command, capture_output=True, timeout=15, creationflags=subprocess.CREATE_NO_WINDOW)
    if result.returncode:
        raise RuntimeError('Windows rejected the Wi-Fi request: ' + result.stdout.decode(errors='replace')[:250])
    for _ in range(40):
        latest = snapshot()
        if len(latest) == 1:
            actual = latest[0]
            if action == 'wifi_connect' and actual['state'] == 1 and actual['profile'] == target:
                context['last_wifi'] = target
                return f'Connected to {target}.'
            if action == 'wifi_disconnect' and actual['state'] == 4:
                return 'Disconnected from Wi-Fi. Say “reconnect Wi-Fi” to reconnect.'
        time.sleep(.25)
    raise RuntimeError('Windows has not confirmed the requested Wi-Fi connection state. Check Wi-Fi Settings; I cannot claim it succeeded.')
