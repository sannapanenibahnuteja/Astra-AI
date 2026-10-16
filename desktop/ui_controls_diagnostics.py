"""Native UI contract checks; integrations are simulated, no personal data used."""
import json
import time
import threading


def configure(runtime):
    state = {'calls': [], 'samples': 0, 'mobile': False, 'speak_error': False}

    def stub(name, function):
        def call(*args):
            state['calls'].append(name)
            return function(*args)
        setattr(runtime, name, call)

    bootstrap = runtime.bootstrap
    stub('bootstrap', lambda: dict(bootstrap(), apps=['Calculator', 'Notepad']))
    stub('ollama_status', lambda: {'online': True, 'ready': True, 'models': ['fixture'], 'message': 'Fixture ready'})
    stub('save_settings', lambda values: runtime._store.save_settings(values))
    for name in ('new_conversation', 'get_messages', 'delete_conversation', 'save_memory', 'delete_memory', 'profile_memories', 'memory_spaces', 'personality_options', 'personal_setup', 'automations_list', 'automation_save', 'automation_delete', 'day_plans', 'day_save', 'day_delete', 'day_result'):
        original = getattr(runtime, name)
        stub(name, original)
    stub('start_chat', lambda *args: 'fixture-job')
    stub('poll_chat', lambda *args: {'text': 'Fixture reply.', 'done': True, 'voice_managed': True, 'error': ''})
    stub('copy_text', lambda text: state.update(copied_text=text) or True)
    stub('cancel_chat', lambda: True)
    enrollment_done = threading.Event()
    def stop_voice():
        state['enrollment_cancelled'] = True
        enrollment_done.set()
        return True
    stub('stop_voice', stop_voice)
    stub('finish_enrollment', lambda: enrollment_done.set() or True)
    stub('voice_session', lambda active: True)
    stub('voice_status', lambda: {'phase': 'listening', 'wake': 'off', 'level': 0, 'error': '', 'aec': 'active', 'pending_audio': False, 'speaker':state.get('speaker',{'state':'disabled'}), 'voice_notice':state.get('voice_notice','')})
    stub('location_settings', lambda: True)
    stub('location_refresh', lambda: {'latitude':12,'longitude':77,'accuracy':100,'timestamp':time.time()})

    def listen():
        time.sleep(.1)
        return {'text': '', 'confidence': 0, 'needs_review': False}
    stub('listen', listen)

    def speak(*args):
        if state['speak_error']:
            raise ValueError('Fixture speech output failed')
        return True
    stub('speak', speak)
    stub('read_aloud', speak)
    stub('day_read', speak)
    original_day_status = runtime.day_status
    stub('day_status', lambda: {**original_day_status(), 'model':'fixture'})
    original_day_calculate = runtime.day_calculate
    def day_calculate(day, traffic=True):
        value = original_day_calculate(day, False)
        if traffic:
            value['mode'] = 'local'
        return value
    stub('day_calculate', day_calculate)
    stub('voice_options', lambda: {'windows': [{'id': 'fixture', 'label': 'Fixture Windows voice'}], 'neural': [], 'azure_ready': False})
    stub('preview_voice', lambda *args: True)
    for name in ('open_data_folder', 'open_link'):
        stub(name, lambda *args: True)
    for name in ('phone_setup', 'neural_voice_setup', 'choose_project'):
        stub(name, lambda *args: str(runtime._store.root))

    def profile():
        enrolled = state['samples'] >= 3
        return {'samples': state['samples'], 'enrolled': enrolled, 'name': 'Fixture', 'active': 'fixture', 'profiles': [{'id': 'fixture', 'name': 'Fixture', 'personality': 'inherit'}] if enrolled else []}
    def enroll(*args):
        enrollment_done.clear()
        state['enrollment_cancelled'] = False
        if not enrollment_done.wait(15): raise RuntimeError('Fixture enrollment was not finished')
        if state['enrollment_cancelled']: return {'cancelled': True}
        state['samples'] += 1
        return profile()
    def forget(*args):
        state['samples'] = 0
        return profile()
    stub('microphone_status', lambda: {'name':'Fixture laptop microphone','calibrated':False,'gain':1})
    def calibrate(stage):
        time.sleep(.4)
        if stage == 'noise': return {'noise_ready':True,'name':'Fixture laptop microphone'}
        value={'device':'fixture','name':'Fixture laptop microphone','noise_rms':.0001,'speech_rms':.01,'gain':3.5}
        runtime._store.save_settings({'microphone_calibration':value})
        return {'profile':value}
    stub('calibrate_microphone', calibrate)
    stub('cancel_speaker_enrollment', profile)
    stub('speaker_status', profile)
    stub('enroll_speaker', enroll)
    stub('test_speaker', lambda: {'state': 'matched', 'name': 'Fixture', 'similarity': .9, 'threshold': .65})
    stub('personalize_speaker', lambda *args: profile())
    stub('forget_speaker', forget)

    def mobile():
        return {'enabled': state['mobile'], 'remote_ready': False, 'url': 'http://127.0.0.1:8787/#fixture'}
    def set_mobile(enabled):
        state['mobile'] = enabled
        return mobile()
    stub('mobile_status', mobile)
    stub('enable_mobile', lambda *args: set_mobile(True))
    stub('disable_mobile', lambda: set_mobile(False))
    return state


def verify(window, runtime, state):
    checks = []

    def wait(expression):
        deadline = time.monotonic() + 8
        while time.monotonic() < deadline:
            if window.evaluate_js(expression):
                return
            time.sleep(.04)
        raise AssertionError(expression)

    def click(label):
        wait(f"[...document.querySelectorAll('button')].some(b => (b.getAttribute('aria-label') === {json.dumps(label)} || b.textContent.trim() === {json.dumps(label)}) && !b.disabled)")
        window.evaluate_js(f"window.fixtureClick({json.dumps(label)})")

    def called(name, action):
        before = state['calls'].count(name)
        action()
        deadline = time.monotonic() + 8
        while state['calls'].count(name) == before and time.monotonic() < deadline:
            time.sleep(.04)
        assert state['calls'].count(name) > before, name
        checks.append(name)

    def saved_focus(value):
        deadline=time.monotonic()+8
        while time.monotonic()<deadline:
            if runtime._store.settings()['speaker_focus']==value: return
            time.sleep(.04)
        raise AssertionError('Focused listening preference was not saved: '+value)

    try:
        wait("!!window.bobVoiceReady && !!document.querySelector('.welcome')")
        wait("document.querySelector('.particle-canvas')?.width > 0")
        wait("(()=>{const c=document.querySelector('.particle-canvas'),d=c.getContext('2d').getImageData(0,0,c.width,c.height).data;let n=0;for(let i=0;i<d.length;i+=4)if(d[i]+d[i+1]+d[i+2]>40)n++;return n>500})()")
        checks.append('particle-orb-rendered')
        window.evaluate_js("""
          Object.defineProperty(navigator, 'clipboard', {configurable:true, value:{writeText:async text=>{window.fixtureClipboard=text;}}});
          window.fixtureClick = label => {
            const buttons = [...document.querySelectorAll('button')];
            const button = buttons.find(b => b.getAttribute('aria-label') === label || b.textContent.trim() === label);
            if (!button || button.disabled) throw Error('Unavailable control: '+label);
            button.click();
          };
          window.fixtureInput = (label, value) => {
            const target = [...document.querySelectorAll('label')].find(l=>l.textContent.startsWith(label))?.querySelector('input,select,textarea') || document.querySelector(`[aria-label="${label}"]`);
            if (!target) throw Error('Missing input: '+label);
            const prototype = target.tagName === 'SELECT' ? HTMLSelectElement.prototype : target.tagName === 'TEXTAREA' ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
            Object.getOwnPropertyDescriptor(prototype,'value').set.call(target,value);
            target.dispatchEvent(new Event('input',{bubbles:true}));
            target.dispatchEvent(new Event('change',{bubbles:true}));
          };
        """)
        for label in ('Memory', 'Capabilities', 'Settings', 'Assistant'):
            click(label)
            wait(f"document.querySelector('.topbar').textContent.includes({json.dumps(label)})")
            checks.append('navigation:' + label)
        for index, expected in enumerate(('Open calculator', 'Remember that my favorite color is blue', 'Search the web for space discoveries', 'Help me plan a productive morning')):
            window.evaluate_js(f"document.querySelectorAll('.suggestion-grid button')[{index}].click()")
            wait(f"document.querySelector('.composer textarea').value === {json.dumps(expected)}")
            checks.append('starter-card:' + str(index + 1))
        window.evaluate_js("document.querySelector('.suggestion-grid button').click()")
        wait("document.querySelector('.composer textarea').value === 'Open calculator'")
        
        called('start_chat', lambda: click('Send message'))
        wait("document.querySelector('.message.assistant')?.textContent.includes('Fixture reply.')")
        called('read_aloud', lambda: click('Read aloud'))
        called('copy_text', lambda: click('Copy reply'))
        assert state.get('copied_text') == 'Fixture reply.'
        checks.append('copy-reply')
        state['speak_error'] = True
        wait("!document.querySelector('.read-response').disabled")
        called('read_aloud', lambda: click('Read aloud'))
        wait("document.querySelector('.notice')?.textContent.includes('Fixture speech output failed') && !document.querySelector('.read-response').disabled")
        checks.append('read-aloud-error-recovery')
        state['speak_error'] = False
        click('Dismiss notification')
        called('new_conversation', lambda: click('New conversation'))
        wait("!!document.querySelector('.welcome')")
        wait("document.querySelectorAll('.delete-chat').length > 0")
        called('delete_conversation', lambda: window.evaluate_js("document.querySelector('.delete-chat').click()"))
        called('listen', lambda: click('Speak one command'))
        wait("document.querySelector('.voice-status').textContent.includes('Listening') || document.querySelector('.voice-status').textContent.includes('Ready for')")
        click('Start voice conversation')
        wait("document.querySelector('.voice-session-button').textContent.includes('End voice')")
        checks.append('upgrade-single-capture-to-hands-free')
        called('stop_voice', lambda: click('End voice conversation'))
        wait("document.querySelector('.voice-session-button').textContent.trim() === 'Voice'")
        click('Memory')
        wait("!!document.querySelector('.memory-form')")
        window.evaluate_js("window.fixtureInput('Memory name','fixture-fact');window.fixtureInput('The detail to remember','test only')")
        called('save_memory', lambda: click('Save memory'))
        wait("!!document.querySelector('[aria-label=\"Forget fixture-fact\"]')")
        click('Edit fixture-fact')
        wait("document.querySelector('.memory-form input').value === 'fixture-fact'")
        window.evaluate_js("window.fixtureInput('The detail to remember','updated fixture')")
        called('save_memory', lambda: click('Save memory'))
        wait("document.querySelector('.memory-grid').textContent.includes('updated fixture')")
        checks.append('edit-memory')
        called('delete_memory', lambda: click('Forget fixture-fact'))
        click('Capabilities')
        window.evaluate_js("window.fixtureInput('Filter applications','CALC')")
        wait("document.querySelectorAll('.app-chips button').length === 1")
        called('start_chat', lambda: click('Calculator'))
        checks.append('case-insensitive-app-filter')
        click('Open settings')
        wait("!!document.querySelector('.settings-page')")
        called('ollama_status', lambda: click('Refresh'))
        called('open_link', lambda: click('Get Ollama for Windows'))
        called('read_aloud', lambda: click('Test voice output'))
        called('preview_voice', lambda: click('Listen to this voice'))
        wait("[...document.querySelectorAll('button')].some(b=>b.textContent==='Listen to this voice' && !b.disabled)")
        called('voice_options', lambda: click('Refresh voices'))
        called('neural_voice_setup', lambda: click('Set up neural voice'))
        click('Reset traits to this personality')
        called('choose_project', lambda: click('Browse for a folder'))
        window.evaluate_js("window.fixtureInput('Conversation mode','fast')")
        called('save_settings', lambda: click('Save settings'))
        wait("document.querySelector('.notice')?.textContent.includes('Settings saved')")
        assert runtime._store.settings()['conversation_mode'] == 'fast'
        called('open_data_folder', lambda: click('Open data folder'))
        called('enable_mobile', lambda: click('Enable mobile access'))
        wait("[...document.querySelectorAll('button')].some(b=>b.textContent==='Create a new pairing link')")
        called('enable_mobile', lambda: click('Create a new pairing link'))
        called('disable_mobile', lambda: click('Disable & revoke links'))
        called('phone_setup', lambda: click('Create calling configuration'))
        called('neural_voice_setup', lambda: click('Create neural voice configuration'))
        called('calibrate_microphone', lambda: click('Measure room noise'))
        wait("[...document.querySelectorAll('button')].some(b=>b.textContent.trim()==='Record my normal voice' && !b.disabled)")
        called('calibrate_microphone', lambda: click('Record my normal voice'))
        wait("document.querySelector('.settings-page').textContent.includes('calibrated · 3.5')")
        assert runtime._store.settings()['microphone_calibration']['gain'] == 3.5
        checks.append('microphone-calibration-saved')
        window.evaluate_js("window.fixtureInput('Your name','Fixture')")
        called('enroll_speaker', lambda: click('Record sample'))
        wait("[...document.querySelectorAll('button')].some(b=>b.textContent.trim()==='Cancel recording' && !b.disabled)")
        called('stop_voice', lambda: click('Cancel recording'))
        wait("document.querySelector('.notice')?.textContent.includes('Recording cancelled')")
        assert state['samples'] == 0
        checks.append('cancel-enrollment-preserves-samples')
        for _ in range(3):
            wait("[...document.querySelectorAll('button')].some(b=>b.textContent.trim()==='Record sample' && !b.disabled)")
            called('enroll_speaker', lambda: click('Record sample'))
            wait("[...document.querySelectorAll('button')].some(b=>b.textContent.trim()==='Finish sample' && !b.disabled)")
            called('finish_enrollment', lambda: click('Finish sample'))
        checks.append('finish-enrollment-control')
        wait("[...document.querySelectorAll('button')].some(b=>b.textContent.trim()==='Test voice match')")
        click('Re-record Fixture')
        wait("[...document.querySelectorAll('button')].some(b=>b.textContent.trim()==='Cancel re-recording')")
        called('cancel_speaker_enrollment', lambda: click('Cancel re-recording'))
        checks.append('re-record-cancel-preserves-profile')
        window.evaluate_js("window.fixtureInput('Focused listening','fixture')")
        called('save_settings',lambda: click('Save settings'))
        saved_focus('fixture')
        window.evaluate_js("window.fixtureInput('Focused listening','*')")
        called('save_settings',lambda: click('Save settings'))
        saved_focus('*')
        checks.append('saved-voices-only-setting')
        called('test_speaker', lambda: click('Test voice match'))
        wait("document.querySelector('.settings-page').textContent.includes('Recognized as Fixture')")
        click('Add another person')
        wait("[...document.querySelectorAll('label')].some(l=>l.textContent==='Your name')")
        called('personalize_speaker', lambda: window.evaluate_js("window.fixtureInput('Active: Fixture','friend')"))
        called('forget_speaker', lambda: click("Delete Fixture's voice"))
        called('forget_speaker', lambda: click('Delete voice profile / restart enrollment'))
        for label, field in [('Manage Ollama connection', 'Ollama address'), ('Manage local resources', 'Unload model after idle'), ('Open local resource settings', 'Unload model after idle'), ('Manage voice profiles', 'Recognize my voice')]:
            click(label)
            wait(f"document.activeElement?.closest('label')?.textContent.startsWith({json.dumps(field)})")
            checks.append('shortcut:' + label)
        called('new_conversation', lambda: click('New conversation'))
        wait("!!document.querySelector('.welcome')")
        called('listen', lambda: click('Talk to Bob'))
        wait("document.querySelector('.voice-session-button').textContent.includes('End voice')")
        called('stop_voice', lambda: click('End voice from Bob core'))
        wait("document.querySelector('.voice-session-button').textContent.trim()==='Voice'")
        for label, field in [('Choose AI model', 'Model'), ('Configure engine', 'Ollama address'), ('Configure model', 'Model'), ('Configure voice', 'Bob’s voice')]:
            click('Go to assistant')
            wait("!!document.querySelector('.composer')")
            click(label)
            wait(f"document.activeElement?.closest('label')?.textContent.startsWith({json.dumps(field)})")
            checks.append('shortcut:' + label)
        for label in ('Manage saved memory', 'Open memory from status'):
            click('Go to assistant')
            wait("!!document.querySelector('.composer')")
            click(label)
            wait("!!document.querySelector('.memory-form')")
            checks.append('shortcut:' + label)
        for title in ('Applications & folders', 'Search & explore', 'Sound & system', 'Connections & settings', 'Files, with context', 'Music & video', 'Microsoft Edge', 'Memory & notes'):
            click('Capabilities')
            wait("!!document.querySelector('.capability-grid')")
            before = state['calls'].count('start_chat')
            click('Try ' + title)
            wait("!!document.querySelector('.composer textarea') && document.querySelector('.composer textarea').value.length>0")
            assert state['calls'].count('start_chat') == before, 'Example executed without review'
            checks.append('capability-example:' + title)
        assert window.evaluate_js("getComputedStyle(document.querySelector('.bob-app')).backgroundColor === 'rgb(0, 0, 0)'")
        checks.append('plain-black-background')
        click('Settings')
        click('Personal setup')
        wait("!!document.querySelector('.personal-setup')")
        window.evaluate_js("window.fixtureInput('preferred name', 'Fixture person')")
        click('Continue')
        for _ in range(3): click('Skip question')
        called('personal_setup', lambda: click('Save selected memories'))
        wait("!document.querySelector('.personal-setup')")
        assert runtime._store.memories()[0]['value'] == 'Fixture person'
        checks.append('onboarding-selected-fact-only')
        click('Personal setup')
        called('personal_setup', lambda: click('Skip setup'))
        wait("!document.querySelector('.personal-setup')")
        click('Automations')
        wait("!!document.querySelector('.routine-builder')")
        click('Use focus template')
        click('Add step')
        click('Remove step 3')
        called('automation_save', lambda: click('Save routine'))
        wait("!!document.querySelector('.routine-card')")
        click('Edit Focus time')
        window.evaluate_js("window.fixtureInput('Daily time', '09:00')")
        called('automation_save', lambda: click('Save routine'))
        called('automations_list', lambda: click('Refresh results'))
        checks.append('routine-daily-edit')
        called('automation_save',lambda: click('Pause routine Focus time'))
        wait("document.querySelector('.routine-card').textContent.includes('daily time will not trigger')")
        assert runtime._automations.rows()[0]['enabled'] is False
        checks.append('paused-routine-warning')
        called('automation_save',lambda: click('Enable routine Focus time'))
        wait("[...document.querySelectorAll('button')].some(b=>b.getAttribute('aria-label')==='Pause routine Focus time')")
        assert runtime._automations.rows()[0]['enabled'] is True
        checks.append('enable-scheduled-routine')
        called('start_chat', lambda: click('Run Focus time'))
        wait("!!document.querySelector('.message.assistant')")
        click('Automations')
        wait("!!document.querySelector('.routine-card')")
        called('automation_delete', lambda: click('Delete routine Focus time'))
        wait("!document.querySelector('.routine-card')")
        checks.append('routine-delete')
        click('Day planner')
        wait("!!document.querySelector('.day-stop') || [...document.querySelectorAll('button')].some(b=>b.textContent==='Add stop')")
        from desktop.day_planner import day_date
        called('location_settings',lambda: click('Windows location permissions'))
        window.evaluate_js("[...document.querySelectorAll('label')].find(l=>l.textContent.startsWith('Allow current PC location')).querySelector('input').click()")
        called('location_refresh',lambda: click('Refresh current location'))
        wait("document.body.textContent.includes('accuracy about 100')")
        checks.append('location-enable-refresh')
        tomorrow = day_date('tomorrow')
        window.evaluate_js(f"window.fixtureInput('Plan date', {json.dumps(tomorrow)}); window.fixtureInput('Day start','08:00'); window.fixtureInput('Starting place or address','Fixture home, City')")
        click('Add stop')
        window.evaluate_js("window.fixtureInput('Stop 1 name','Fixture meeting'); window.fixtureInput('Stop 1 address','Fixture office, City'); window.fixtureInput('Stop 1 appointment','09:00')")
        click('Add stop')
        window.evaluate_js("window.fixtureInput('Stop 2 name','Fixture shop'); window.fixtureInput('Stop 2 address','Fixture shop, City'); window.fixtureInput('Stop 2 appointment','11:00')")
        click('Move stop 2 earlier')
        click('Order appointments by time')
        click('Remove stop 2')
        checks.append('day-stop-add-reorder-remove')
        called('day_save', lambda: click('Save day plan'))
        called('day_calculate', lambda: click('Use manual travel estimates'))
        wait("!!document.querySelector('.day-leg') && document.querySelector('.traffic-detail').textContent.includes('manually entered')")
        checks.append('day-manual-timeline')
        called('day_calculate', lambda: click('Plan with local AI'))
        wait("!!document.querySelector('.maps-attribution')")
        called('day_read', lambda: click('Read day briefing'))
        called('open_link', lambda: click('Open driving route in Google Maps ↗'))
        called('day_status', lambda: click('Refresh local model'))
        called('day_delete', lambda: click('Delete saved day'))
        wait("!document.querySelector('.day-leg')")
        click('New day')
        checks.append('day-new-delete')
        runtime._store.save_settings({'speaker_enabled':True})
        state['speaker']={'state':'matched','name':'Fixture User','profile_id':'fixture'}
        click('New conversation')
        wait("document.querySelector('.user-avatar').textContent==='FU' && document.querySelector('.sidebar-footer').textContent.includes('Fixture User')")
        checks.append('recognized-speaker-avatar')
        state['speaker']={'state':'uncertain'}
        wait("document.querySelector('.user-avatar').textContent==='?' && !document.querySelector('.sidebar-footer').textContent.includes('Fixture User')")
        checks.append('uncertain-speaker-neutral-avatar')
        state['voice_notice']='Speech captured, but the saved-voice filter could not match it.'
        wait("document.querySelector('.voice-hint').textContent.includes('saved-voice filter')")
        checks.append('voice-filter-rejection-visible')
        result = {'passed': True, 'checks': checks, 'count': len(checks), 'scope': 'Isolated UI contracts; voice, app, local LLM estimates, links, picker and phone integrations are simulated.'}
    except Exception as error:
        result = {'passed': False, 'checks': checks, 'error': str(error)}
    (runtime._store.root / 'ui-controls-test.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
