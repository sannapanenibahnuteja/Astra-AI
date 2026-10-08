"""Named Settings pages and verified accessible controls. No registry guessing."""
import os
import re
import time
from desktop import network, windows

PAGES = {
    'system':'', 'display':'display', 'sound':'sound', 'notifications':'notifications',
    'focus':'quiethours', 'power':'powersleep', 'battery saver':'batterysaver',
    'storage':'storagesense', 'multitasking':'multitasking', 'about':'about',
    'bluetooth':'bluetooth', 'devices':'connecteddevices', 'printers':'printers',
    'mouse':'mousetouchpad', 'touchpad':'devices-touchpad', 'typing':'typing',
    'wifi':'network-wifi', 'airplane mode':'network-airplanemode', 'network':'network-status',
    'ethernet':'network-ethernet', 'vpn':'network-vpn', 'proxy':'network-proxy',
    'mobile hotspot':'network-mobilehotspot', 'background':'personalization-background',
    'colors':'personalization-colors', 'themes':'themes', 'lock screen':'lockscreen',
    'taskbar':'taskbar', 'start menu':'personalization-start', 'fonts':'fonts',
    'apps':'appsfeatures', 'default apps':'defaultapps', 'startup apps':'startupapps',
    'accounts':'yourinfo', 'sign in':'signinoptions', 'other users':'otherusers',
    'date and time':'dateandtime', 'language':'regionlanguage', 'region':'regionformatting',
    'accessibility':'easeofaccess', 'text size':'easeofaccess-display',
    'magnifier':'easeofaccess-magnifier', 'narrator':'easeofaccess-narrator',
    'keyboard':'easeofaccess-keyboard', 'privacy':'privacy', 'microphone':'privacy-microphone',
    'camera':'privacy-webcam', 'location':'privacy-location', 'windows update':'windowsupdate',
    'update history':'windowsupdate-history', 'recovery':'recovery', 'activation':'activation',
    'troubleshoot':'troubleshoot', 'remote desktop':'remotedesktop', 'gaming':'gaming-gamebar',
}
ACTIONS = {'settings_open', 'settings_inspect', 'settings_set', 'settings_status', 'radio_set', 'radio_status',
           'wifi_status', 'wifi_profiles', 'wifi_connect', 'wifi_disconnect'}


def canonical(value):
    value = value.lower().strip().replace('wi-fi', 'wifi').replace('wi fi', 'wifi').replace('aeroplane', 'airplane')
    value = re.sub(r'^(?:the |my )', '', value)
    return {'battery save':'battery saver', 'energy saver':'battery saver', 'bluetooth and devices':'bluetooth',
            'internet':'network', 'personalisation':'themes', 'personalization':'themes', 'updates':'windows update'}.get(value, value)


def parse(text, context):
    text = text.strip()
    lower = canonical(text)
    match = re.fullmatch(r'(?:turn|switch) (?:the )?(bluetooth|wifi|airplane mode|battery saver|energy saver|it)(?: back)? (on|off)', lower)
    if not match:
        reverse = re.fullmatch(r'(?:turn|switch) (on|off) (?:the )?(bluetooth|wifi|airplane mode|battery saver|energy saver|it)', lower)
        if reverse: match = (None, reverse[2], reverse[1])
    if not match:
        enabled = re.fullmatch(r'(enable|disable) (?:the )?(bluetooth|wifi|airplane mode|battery saver|energy saver)', lower)
        if enabled: match = (None, enabled[2], 'on' if enabled[1] == 'enable' else 'off')
    if match:
        target = context.get('last_setting', '') if match[1] == 'it' else canonical(match[1])
        if target not in ('bluetooth', 'wifi', 'airplane mode', 'battery saver'):
            return {'action':'clarify', 'target':'Which setting should I turn ' + match[2] + '?'}
        return {'action':'radio_set' if target in ('bluetooth', 'wifi') else 'settings_set', 'target':target, 'value':match[2], 'page':target}
    match = re.fullmatch(r'(?:open|show|go to) (.+?) settings', lower)
    if match and canonical(match[1]) in PAGES:
        return {'action':'settings_open', 'target':canonical(match[1])}
    match = re.fullmatch(r'set (.+?) to (.+?) in (.+?) settings', text, re.I)
    if match:
        return {'action':'settings_set', 'target':match[1], 'value':match[2], 'page':canonical(match[3])}
    match = re.fullmatch(r'turn (.+?) (on|off) in (.+?) settings', text, re.I)
    if match:
        return {'action':'settings_set', 'target':match[1], 'value':match[2].lower(), 'page':canonical(match[3])}
    match = re.fullmatch(r'(?:inspect|read|show)(?: the)? (?:current )?settings(?: controls| page)?', lower)
    if match:
        return {'action':'settings_inspect', 'target':''}
    match = re.fullmatch(r'(?:is|check|show)(?: the)? (bluetooth|wifi)(?: status| on| off)?', lower)
    if match:
        return {'action':'radio_status', 'target':match[1]}
    match = re.fullmatch(r'(?:is|check|show)(?: the)? (airplane mode|battery saver|energy saver)(?: status| on| off)?', lower)
    if match:
        return {'action':'settings_status', 'target':canonical(match[1])}
    if lower in ('wifi status', 'network status', 'what wifi am i connected to', 'which wifi am i connected to'):
        return {'action':'wifi_status', 'target':''}
    if lower in ('list saved wifi networks', 'show saved wifi networks', 'list wifi networks'):
        return {'action':'wifi_profiles', 'target':''}
    if lower in ('disconnect wifi', 'disconnect from wifi', 'disconnect my laptop from wifi'):
        return {'action':'wifi_disconnect', 'target':''}
    if lower in ('reconnect wifi', 'reconnect to wifi', 'connect wifi'):
        return {'action':'wifi_connect', 'target':'previous'}
    match = re.fullmatch(r'connect(?: (?:my laptop|my computer))? to (?:wifi |wi-fi |wi fi |network )(.+)', text, re.I)
    if match:
        return {'action':'wifi_connect', 'target':match[1].strip(' "')}
    return None


def validate(command):
    action = command.get('action')
    if action not in ACTIONS:
        raise ValueError('Unsupported Settings action.')
    result = {'action':action, 'target':command.get('target', ''), 'value':command.get('value', ''), 'page':command.get('page', '')}
    if any(not isinstance(v, str) or len(v) > 512 or '\x00' in v for v in result.values()):
        raise ValueError('Invalid Settings target.')
    if action in ('radio_set', 'radio_status', 'settings_open'):
        result['target'] = canonical(result['target'])
    if action.startswith('radio_') and result['target'] not in ('bluetooth', 'wifi'):
        raise ValueError('Choose Bluetooth or Wi-Fi.')
    if action == 'radio_set' and result['value'] not in ('on', 'off'):
        raise ValueError('Choose on or off.')
    if action == 'settings_open' and result['target'] not in PAGES:
        raise ValueError('That Settings page is not in Bob’s page catalog.')
    if result['page']:
        result['page'] = canonical(result['page'])
        if result['page'] not in PAGES:
            raise ValueError('Choose a known Settings page.')
    if action == 'settings_set' and (not result['target'] or not result['value']):
        raise ValueError('Specify the exact Settings control label and its value.')
    known = canonical(result['target'])
    # Connectivity loss and arbitrary settings deserve a concrete confirmation.
    result['confirm'] = (action == 'wifi_disconnect' or
        action == 'radio_set' and result['target'] == 'wifi' and result['value'] == 'off' or
        action == 'settings_set' and not ((known == 'battery saver' and result['page'] == 'battery saver' and result['value'] in ('on','off')) or (known == 'airplane mode' and result['value'] == 'off')))
    return result


def _controls():
    from pywinauto import Desktop
    matches = [w for w in windows.window_inventory() if w['process'].lower() == 'systemsettings.exe'
               or (w['process'].lower() == 'applicationframehost.exe' and w['title'] == 'Settings')]
    if len(matches) != 1:
        raise ValueError('Open one Windows Settings window first. Bob could not identify it uniquely.')
    item = matches[0]
    root = Desktop(backend='uia').window(handle=item['handle']).wrapper_object()
    return [n for n in root.descendants(depth=12)[:1200]
            if n.is_visible() and not getattr(n.element_info, 'is_password', False)]


def inspect():
    with windows.com_thread():
        rows = []
        for node in _controls():
            name = node.element_info.name
            if not name: continue
            suffix = ' (disabled)' if not node.is_enabled() else ''
            try: suffix += ': ' + ('on' if node.iface_toggle.CurrentToggleState == 1 else 'off')
            except Exception: pass
            rows.append(f'{name[:120]} [{node.element_info.control_type}]{suffix}')
        return 'Visible Windows Settings controls:\n' + '\n'.join(dict.fromkeys(rows))[:8000]


def set_control(target, value, page=''):
    known = canonical(target)
    if known in ('airplane mode', 'battery saver'):
        page = known
    if page:
        os.startfile('ms-settings:' + PAGES[page])
    labels = {target.casefold()}
    if known == 'battery saver': labels |= {'battery saver', 'energy saver', 'always use energy saver'}
    if known == 'airplane mode': labels |= {'airplane mode', 'aeroplane mode'}
    with windows.com_thread():
        matches = []
        expanded = False
        for _ in range(25):
            try: nodes = _controls()
            except ValueError:
                time.sleep(.15)
                continue
            if known == 'battery saver' and not expanded:
                groups = [n for n in nodes if n.element_info.control_type == 'Group' and n.element_info.name.casefold().startswith(('energy saver,', 'battery saver,'))]
                if len(groups) == 1:
                    for child in groups[0].descendants(depth=3):
                        if child.element_info.control_type == 'Button' and child.element_info.name == 'Show more settings':
                            try:
                                pattern = child.iface_expand_collapse
                                if pattern.CurrentExpandCollapseState == 0: pattern.Expand()
                                expanded = True
                            except Exception: pass
                    if expanded:
                        time.sleep(.2)
                        continue
            matches = [n for n in nodes if n.element_info.name.casefold() in labels
                       and n.element_info.control_type in ('CheckBox', 'Button', 'ComboBox', 'Slider', 'Edit')]
            if len(matches) == 1: break
            time.sleep(.15)
        if len(matches) != 1:
            raise ValueError('That Settings control is absent or ambiguous. Say “inspect settings” and use an exact visible label. Windows versions expose different controls.')
        node = matches[0]
        if value is None:
            try: state = node.iface_toggle.CurrentToggleState
            except Exception as exc: raise ValueError('Windows does not expose a readable toggle for this setting.') from exc
            return f'{target.capitalize()} is ' + ({0:'off',1:'on'}.get(state,'indeterminate')) + '.'
        if not node.is_enabled():
            raise RuntimeError(f'{target} is disabled by Windows. Power, hardware or administrator policy may prevent this change.')
        kind = node.element_info.control_type
        if value.lower() in ('on', 'off'):
            desired = 1 if value.lower() == 'on' else 0
            try: toggle = node.iface_toggle
            except Exception as exc: raise ValueError('This control has no readable toggle state. No change was made.') from exc
            if toggle.CurrentToggleState not in (0, 1):
                raise ValueError('The setting has an indeterminate state; choose it in Windows Settings.')
            if toggle.CurrentToggleState != desired: toggle.Toggle()
            for _ in range(20):
                if toggle.CurrentToggleState == desired: return f'{target.capitalize()} is {value.lower()}.'
                time.sleep(.1)
        elif kind == 'ComboBox':
            node.select(value)
            if node.selected_text().casefold() == value.casefold(): return f'{target} is set to {value}.'
        elif kind == 'Slider':
            number = float(value)
            control = node.iface_range_value
            if not control.CurrentMinimum <= number <= control.CurrentMaximum:
                raise ValueError('The value is outside this slider’s range.')
            control.SetValue(number)
            if abs(control.CurrentValue - number) < .01: return f'{target} is set to {value}.'
        else:
            raise ValueError('This setting needs its Windows dialog. Bob supports exposed toggles, dropdowns and sliders; arbitrary buttons are available through inspect/click window commands.')
    raise RuntimeError('Windows did not confirm the new setting. Inspect Settings before trying again.')


def execute(command, context):
    command = validate(command)
    action, target = command['action'], command['target']
    if action.startswith('radio_'):
        result = network.radio(target, command['value'] if action == 'radio_set' else None)
        context['last_setting'] = target
        return result
    if action.startswith('wifi_'):
        result = network.wifi(action, target, context)
        context['last_setting'] = 'wifi'
        return result
    context['last_window'] = 'Settings'
    if action == 'settings_open':
        os.startfile('ms-settings:' + PAGES[target])
        context['last_settings_page'] = target
        if target in ('bluetooth', 'wifi', 'battery saver', 'airplane mode'): context['last_setting'] = target
        return f'Asked Windows to show {target} settings. The page is unverified; inspect settings to check it.'
    if action == 'settings_inspect': return inspect()
    result = set_control(target, None if action == 'settings_status' else command['value'], command['page'])
    context['last_setting'] = canonical(target)
    return result
