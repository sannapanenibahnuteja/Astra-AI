"""Opt-in, one-shot Windows location. No IP lookup, polling or persisted fixes."""
import json
import math
import os
import subprocess
import time

CURRENT = '@current_location'


def is_current(value):
    return isinstance(value, str) and value.strip().casefold() in {
        CURRENT, 'current location', 'my current location', 'my location', 'here', 'from here', 'where i am'}


SCRIPT = r"""
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [Text.UTF8Encoding]::new($false)
Add-Type -AssemblyName System.Runtime.WindowsRuntime
[Windows.Devices.Geolocation.Geolocator,Windows.Devices.Geolocation,ContentType=WindowsRuntime] | Out-Null
$asTask = [System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
    $_.Name -eq 'AsTask' -and $_.IsGenericMethod -and $_.GetGenericArguments().Count -eq 1 -and
    $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1'
} | Select-Object -First 1
$locator = [Windows.Devices.Geolocation.Geolocator]::new()
$locator.DesiredAccuracyInMeters = 100
$operation = $locator.GetGeopositionAsync([TimeSpan]::FromSeconds(30), [TimeSpan]::FromSeconds(10))
$task = $asTask.MakeGenericMethod([Windows.Devices.Geolocation.Geoposition]).Invoke($null, @($operation))
if (-not $task.Wait(12000)) { throw 'Location request timed out' }
$coord = $task.Result.Coordinate
$point = $coord.Point.Position
@{ latitude=$point.Latitude; longitude=$point.Longitude; accuracy=$coord.Accuracy;
   timestamp=$coord.Timestamp.ToUnixTimeSeconds(); source='Windows location service' } | ConvertTo-Json -Compress
"""


def validate(value, now=None):
    if not isinstance(value, dict): raise ValueError('Windows returned an invalid location.')
    for key, low, high in [('latitude',-90,90),('longitude',-180,180),('accuracy',0,50000),('timestamp',0,float('inf'))]:
        number=value.get(key)
        if isinstance(number,bool) or not isinstance(number,(int,float)) or not math.isfinite(number) or not low<=number<=high:
            raise ValueError('Windows returned an invalid or excessively coarse location. Enter a starting place instead.')
    age=(now if now is not None else time.time())-value['timestamp']
    if not -30<=age<=120: raise ValueError('Windows returned an old location. Refresh or enter a starting place instead.')
    return {key:value[key] for key in ('latitude','longitude','accuracy','timestamp')} | {'source':'Windows location service'}


def current(settings):
    if settings.get('location_enabled') is not True:
        raise ValueError('Enable Current location in Day planner or Settings first, or enter a starting place.')
    executable=os.path.join(os.environ['SystemRoot'],'System32','WindowsPowerShell','v1.0','powershell.exe')
    try:
        result=subprocess.run([executable,'-NoProfile','-NonInteractive','-Command',SCRIPT],capture_output=True,timeout=18,creationflags=subprocess.CREATE_NO_WINDOW)
        if result.returncode: raise ValueError('Location unavailable. Enable Windows Location services and desktop app access in Privacy & security → Location, or enter a starting place.')
        return validate(json.loads(result.stdout.decode('utf-8-sig')))
    except (subprocess.TimeoutExpired, OSError, json.JSONDecodeError):
        raise ValueError('Windows could not provide a fresh location. Try again or enter a starting place.') from None


def coordinates(value):
    return f"{value['latitude']:.6f},{value['longitude']:.6f}"
