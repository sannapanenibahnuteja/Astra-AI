import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { Activity, ArrowUp, AudioLines, Bot, Brain, ChevronRight, Command, Copy, Cpu, ExternalLink, Globe, Layers, MapPin, MessageSquare, Mic, MicOff, Plus, Radio, Settings2, Palette, PanelLeft, PanelRight, ShieldCheck, Sparkles, Square, Trash2, Volume2, X } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { nativeApi, pause } from './bridge';
import Core from './Core';
import Panels from './Panels';
import AutomationsPanel from './AutomationsPanel';
import PersonalSetup from './PersonalSetup';
import WelcomePanel from './WelcomePanel';
import FinancePanel, { FinanceWidget } from './FinancePanel';
import DayPlannerPanel from './DayPlannerPanel';
import './desktop.css';
import './hud.css';
import './minimal.css';
import './workspace.css';
import AppearancePanel from './AppearancePanel';
import { appearanceDefaults, accents, surfaces } from './appearanceTheme';

const defaults = { ollama_url: 'http://127.0.0.1:11434', model: 'qwen3:8b', personality: '', bob_url: '', voice_enabled: true, voice_rate: 0, voice_language: 'en-US', wake_enabled: true, greeting_enabled: true, auto_listen: true, project_path: '', keep_alive: '2m', context_size: 4096 };
const suggestions = [
  { icon: Command, title: 'Take care of a task', text: 'Open calculator', tag: 'WINDOWS' },
  { icon: Brain, title: 'Remember what matters', text: 'Remember that my favorite color is blue', tag: 'MEMORY' },
  { icon: Globe, title: 'Find something new', text: 'Search the web for space discoveries', tag: 'EXPLORE' },
  { icon: Sparkles, title: 'Think it through', text: 'Help me plan a productive morning', tag: 'IDEAS' },
];
const navigation = [{ id: 'chat', label: 'Assistant', icon: MessageSquare }, { id: 'welcome', label: 'Get started', icon: ShieldCheck }, { id: 'finance', label: 'Finance', icon: Layers }, { id: 'memory', label: 'Memory', icon: Brain }, { id: 'capabilities', label: 'Capabilities', icon: Layers }, { id: 'day', label: 'Day planner', icon: MapPin }, { id: 'automations', label: 'Automations', icon: Sparkles }, { id: 'settings', label: 'Settings', icon: Settings2 }];

export default function DesktopApp() {
  const [connected, setConnected] = useState(false);
  const [appearanceOpen, setAppearanceOpen] = useState(false);
  const [appearanceSaving, setAppearanceSaving] = useState(false);
  const [appearanceError, setAppearanceError] = useState('');
  const [page, setPage] = useState('chat');
  const [setup, setSetup] = useState(false);
  const [requestedDay, setRequestedDay] = useState(null);
  const [dayProgress, setDayProgress] = useState('');
  const dayRevision = useRef(0);
  const [dayResultRevision, setDayResultRevision] = useState(0);
  const [settings, setSettings] = useState(defaults);
  const [status, setStatus] = useState({ online: false, ready: false, models: [], message: 'Waiting for desktop connection' });
  const [conversations, setConversations] = useState([]);
  const [conversation, setConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [memories, setMemories] = useState([]);
  const [apps, setApps] = useState([]);
  const [input, setInput] = useState('');
  const [phase, setPhase] = useState('idle');
  const [busy, setBusy] = useState(false);
  const [taskProgress, setTaskProgress] = useState('');
  const [handsFree, setHandsFree] = useState(false);
  const [voiceStatus, setVoiceStatus] = useState({ phase: 'idle', wake: 'off', level: 0, error: '' });
  const captureRef = useRef(null);
  const capturing = useRef(false);
  const [notice, setNotice] = useState('');
  const bottom = useRef(null);
  const active = useRef(false);
  const voiceLoop = useRef(false);
  const voiceEpoch = useRef(0);
  const captureEpoch = useRef(0);
  const submitRef = useRef(null);
  const inputRef = useRef(null);
  const appearance = useMemo(() => ({ ...appearanceDefaults, ...settings.appearance }), [settings.appearance]);
  const orbState = voiceStatus.phase === 'speaking' ? 'speaking' : phase;
  const orbLevel = orbState === 'speaking' ? voiceStatus.output_level || 0 : voiceStatus.level || 0;
  const recognizedSpeaker = settings.speaker_enabled && voiceStatus.speaker?.state === 'matched' ? voiceStatus.speaker : null;
  const speakerInitials = recognizedSpeaker?.name?.trim().split(/\s+/).slice(0, 2).map(word => Array.from(word)[0]).join('').toUpperCase();

  async function refresh() {
    const data = await nativeApi().bootstrap();
    setConversations(data.conversations); setMemories(data.memories); setApps(data.apps);
    setSettings(data.settings);
    return data;
  }
  async function checkConnection() {
    try { setStatus(await nativeApi().ollama_status()); } catch (error) { setNotice(error.message); }
  }
  useEffect(() => {
    let alive = true;
    async function init() {
      try {
        const data = await nativeApi().bootstrap();
        if (!alive) return;
        setConnected(true); setSettings(data.settings); setSetup(!data.settings.onboarding_done);
        if (!data.settings.onboarding_done) setPage('welcome');
        setConversations(data.conversations); setMemories(data.memories); setApps(data.apps);
        const id = data.conversations[0]?.id || await nativeApi().new_conversation();
        const history = await nativeApi().get_messages(id);
        if (!alive) return;
        setConversation(id); setMessages(history);
        const connection = await nativeApi().ollama_status();
        if (alive) setStatus(connection);
      } catch (error) { if (alive) setNotice(error.message); }
    }
    if (window.pywebview?.api) init();
    window.addEventListener('pywebviewready', init);
    return () => { alive = false; window.removeEventListener('pywebviewready', init); voiceLoop.current = false; };
  }, []);
  useEffect(() => { bottom.current?.scrollIntoView({ behavior: busy ? 'instant' : 'smooth' }); }, [messages, busy]);
  useEffect(() => {
    function shortcut(event) {
      if ((event.ctrlKey || event.metaKey) && event.key === '/') { event.preventDefault(); setPage('chat'); requestAnimationFrame(() => inputRef.current?.focus()); }
    }
    window.addEventListener('keydown', shortcut);
    return () => window.removeEventListener('keydown', shortcut);
  }, []);

  useEffect(() => {
    if (!connected) return;
    let alive = true;
    const timer = setInterval(async () => {
      if (document.hidden || document.documentElement.classList.contains('background-mode')) return;
      try {
        const state = await nativeApi().day_status();
        if (alive) setDayProgress(state.progress || '');
        if (alive && state.revision > dayRevision.current) {
          dayRevision.current = state.revision;
          setDayResultRevision(state.revision);
          if (state.day) { setRequestedDay(state.day); setPage('day'); }
        }
      } catch { /* The native status call is optional during startup/shutdown. */ }
    }, 2000);
    return () => { alive = false; clearInterval(timer); };
  }, [connected]);

  async function send(text, spoken = false, speaker = null) {
    text = text.trim();
    if (!text || active.current) return;
    if (!connected) { setNotice('Launch Bob.exe for chat, voice and Windows actions.'); return; }
    active.current = true; setBusy(true); setNotice(''); setInput(''); setPage('chat'); setPhase('thinking');
    let finalText, voiceManaged;
    setTaskProgress('Planning your request');
    try {
      if (!spoken) { voiceEpoch.current += 1; voiceLoop.current = false; setHandsFree(false); await nativeApi().stop_voice(); }
      const id = spoken ? await nativeApi().voice_conversation(conversation, speaker, text) : conversation || await nativeApi().new_conversation();
      setConversation(id);
      const base = await nativeApi().get_messages(id);
      setMessages([...base, { role: 'user', content: text }, { role: 'assistant', content: '' }]);
      const job = await nativeApi().start_chat(id, text, spoken, speaker);
      while (true) {
        const response = await nativeApi().poll_chat(job);
        finalText = response.text;
        voiceManaged = !!response.voice_managed;
        setTaskProgress(response.progress || 'Working on your request');
        setMessages([...base, { role: 'user', content: text }, { role: 'assistant', content: finalText }]);
        if (response.done) { if (response.error) { setNotice(response.error); } break; }
        await pause(55);
      }
      await refresh();
      if (settings.voice_enabled && !voiceManaged && !finalText.includes('[Response stopped.]')) {
        setPhase('speaking');
        await nativeApi().speak(finalText.replace(/```[\s\S]*?```/g, ' Code is shown on screen. ').replace(/[*#`]/g, ''));
      }
    } catch (error) { setNotice(error.message); }
    finally { active.current = false; setBusy(false); setPhase('idle'); }
  }
  useEffect(() => { submitRef.current = send; });
  useEffect(() => {
    function hidden() {
      voiceEpoch.current += 1; voiceLoop.current = false; setHandsFree(false);
      nativeApi().stop_voice();
      if (!active.current) setPhase('idle');
    }
    window.addEventListener('bob-hide', hidden);
    function visibility() { document.documentElement.classList.toggle('background-mode', document.hidden); }
    document.addEventListener('visibilitychange', visibility);
    return () => { window.removeEventListener('bob-hide', hidden); document.removeEventListener('visibilitychange', visibility); };
  }, []);
  async function capture(loop = false) {
    if (active.current || capturing.current) return;
    if (!connected) { setNotice('Voice is available in the Windows desktop app.'); return; }
    capturing.current = true;
    const epoch = ++voiceEpoch.current;
    captureEpoch.current = epoch;
    let pendingTranscript = null;
    let pendingAudio = false;
    voiceLoop.current = loop; setHandsFree(loop);
    setNotice(''); setPage('chat');
    try {
      await nativeApi().voice_session(true);
      do {
        if (active.current) break;
        setPhase('listening');
        const result = await nativeApi().listen();
        if (epoch !== voiceEpoch.current) break;
        if (result.speaker) setVoiceStatus(previous => ({ ...previous, speaker: result.speaker }));
        setPhase(voiceLoop.current ? 'listening' : 'idle');
        if (result.wake_triggered) { voiceLoop.current = true; setHandsFree(true); setNotice('Wake phrase heard. Say your request.'); }
        if (/^(stop listening|stop voice|go to sleep)[.!?]?$/i.test(result.text?.trim() || '')) { pendingTranscript = null; voiceLoop.current = false; break; }
        if (result.text && result.confidence >= 0.65 && !result.needs_review) {
          let text = result.text.replace(/^(?:(?:hey|okay)\s+)?bob\b[,\s]*/i, '');
          const request = await nativeApi().prepare_voice_request(text);
          if (request.stop_listening) {
            voiceLoop.current = false; pendingTranscript = null; setHandsFree(false);
            await nativeApi().voice_session(false);
            text = request.text;
            if (!text) break;
          }
          if (pendingTranscript) {
            if (/^(yes|yes please|correct|that's right|send it)[.!?]?$/i.test(text)) text = pendingTranscript;
            else if (/^(no|cancel|never mind)[.!?]?$/i.test(text)) { pendingTranscript = null; setInput(''); setNotice('Okay. Say your request again after the tone.'); continue; }
            pendingTranscript = null; setInput('');
          }
          if (/^(stop listening|stop voice|go to sleep)[.!?]?$/i.test(text)) { voiceLoop.current = false; break; }
          if (result.speaker?.state === 'matched') setNotice(`Voice recognized as ${result.speaker.name}`);
          else if (result.speaker && result.speaker.state !== 'not_enrolled') setNotice('Voice identity uncertain. Your request can still be processed.');
          await submitRef.current(text, true, result.speaker || null);
        } else if (result.text) {
          pendingTranscript = result.text;
          setInput(result.text); setNotice('Please confirm what Bob heard: say “yes”, repeat your request, or edit it below.');
          if (settings.voice_enabled) { setPhase('speaking'); await nativeApi().speak(`I heard: ${result.text}. Is that right? Say yes, or repeat your request.`); }

        } else if (result.ignored) {
          setNotice(result.trigger_required ? 'Waiting for “Hey Bob” or “Okay Bob”.' : result.speaker?.message || 'Focused listening ignored another or uncertain voice. Speak a full sentence.');
        } else if (result.capture_status === 'no_words') {
          setNotice(result.message || 'Speech was captured, but no words were decoded. Please repeat your request; nothing was executed.');
        } else {
          const audio = await nativeApi().voice_status();
          if (!(voiceLoop.current && audio.aec === 'active')) {
            setNotice('No speech detected. Say Hey Bob to try again, or check Windows Settings → Sound → Input.'); voiceLoop.current = false;
          }
        }
        // A spoken interruption is a new turn, even after a single-command capture.
        // Keep the native session alive until that queued request is consumed.
        const audio = await nativeApi().voice_status();
        pendingAudio = audio.aec === 'active' && audio.pending_audio;
        if (voiceLoop.current || pendingAudio) await pause(75);
      } while ((voiceLoop.current || pendingTranscript || pendingAudio) && epoch === voiceEpoch.current);
    } catch (error) { if (epoch === voiceEpoch.current) setNotice(error.message); }
    finally { capturing.current = false; await nativeApi().voice_session(false); if (epoch === voiceEpoch.current) { voiceLoop.current = false; setHandsFree(false); setPhase('idle'); } }
  }
  useEffect(() => { captureRef.current = capture; });
  useEffect(() => {
    if (!connected) return;
    let alive = true, timer, voiceActive = false;
    async function pollVoice() {
      try { const value = await nativeApi().voice_status(); if (alive) { setVoiceStatus(value); voiceActive = value.phase === 'speaking'; if (active.current && capturing.current) setPhase(value.phase === 'speaking' ? 'speaking' : 'thinking'); } } catch { /* connection shutting down */ }
      if (alive) timer = setTimeout(pollVoice, capturing.current || voiceActive ? 100 : 1500);
    }
    function wake() { if (!document.querySelector('.personal-setup')) captureRef.current?.(true); }
    window.addEventListener('bob-wake', wake);
    window.bobVoiceReady = true;
    pollVoice();
    return () => { alive = false; clearTimeout(timer); window.bobVoiceReady = false; window.removeEventListener('bob-wake', wake); };
  }, [connected]);
  async function stop() {
    voiceEpoch.current += 1; voiceLoop.current = false; setHandsFree(false);
    try { await nativeApi().stop_voice(); await nativeApi().cancel_chat(); } catch (error) { setNotice(error.message); }
    if (!active.current) setPhase('idle');
  }
  async function interruptAndCapture(loop = false) {
    await stop();
    for (let attempt = 0; attempt < 63 && (active.current || capturing.current); attempt += 1) await pause(40);
    if (!active.current && !capturing.current) await capture(loop);
  }
  async function startVoiceSession() {
    if (capturing.current && captureEpoch.current !== voiceEpoch.current) {
      // A cancelled listen is still unwinding. It must finish before a new
      // session starts, or its finally block can shut the new session down.
      await interruptAndCapture(true);
      return;
    }
    if (capturing.current && !active.current) {
      voiceLoop.current = true; setHandsFree(true);
      return;
    }
    if (active.current || phase === 'speaking') await interruptAndCapture(true);
    else await capture(true);
  }
  async function readAloud(text) {
    setPhase('speaking');
    try { await nativeApi().read_aloud(text); }
    catch (error) { setNotice(error.message); }
    finally { if (!active.current && !capturing.current) setPhase('idle'); }
  }
  function openSettings(label = 'Model') {
    setPage('settings');
    requestAnimationFrame(() => {
      const field = [...document.querySelectorAll('.settings-page label')].find(item => item.textContent.startsWith(label))?.querySelector('input,select,textarea');
      field?.scrollIntoView({ behavior: 'smooth', block: 'center' });
      field?.focus({ preventScroll: true });
    });
  }
  function prepareCommand(text) {
    setInput(text); setPage('chat');
    requestAnimationFrame(() => inputRef.current?.focus());
  }
  async function copyMessage(text) {
    try { if (connected) await nativeApi().copy_text(text); else await navigator.clipboard.writeText(text); setNotice('Message copied.'); }
    catch { setNotice('Clipboard unavailable. Select the message text to copy it.'); }
  }
  async function selectConversation(id) {
    if (active.current) return;
    await stop();
    try { setMessages(await nativeApi().get_messages(id)); setConversation(id); setPage('chat'); } catch (error) { setNotice(error.message); }
  }
  async function newChat() {
    if (active.current) return;
    try { await stop(); const id = await nativeApi().new_conversation(); setConversation(id); setMessages([]); setPage('chat'); await refresh(); } catch (error) { setNotice(error.message); }
  }
  async function deleteChat(id) {
    try { await nativeApi().delete_conversation(id); if (conversation === id) { setConversation(null); setMessages([]); } await refresh(); } catch (error) { setNotice(error.message); }
  }
  const invoke = useCallback(async (method, ...args) => {
    try { return await nativeApi()[method](...args); } catch (error) { setNotice(error.message); return null; }
  }, []);

  async function updateAppearance(patch) {
    if (appearanceSaving) return;
    setAppearanceSaving(true); setAppearanceError('');
    try { const saved=await nativeApi().appearance_update(patch);setSettings(saved); }
    catch(error) {setAppearanceError(error.message);setNotice(error.message);}
    finally {setAppearanceSaving(false);}
  }
  const appearanceStyle = {'--accent':accents[appearance.accent], '--cyan':accents[appearance.accent],
    '--surface':surfaces[appearance.background], '--sidebar-surface':surfaces[appearance.sidebar_color] || 'var(--surface)',
    '--composer-surface':surfaces[appearance.composer_color] || '#121214',
    '--chat-font':({small:'13px',medium:'15px',large:'17px','extra large':'19px'})[appearance.font_size],
    '--ui-font':({system:'"Segoe UI",system-ui,sans-serif',rounded:'"Arial Rounded MT Bold","Segoe UI",sans-serif',mono:'Consolas,monospace'})[appearance.font_family],
    '--radius':({round:'22px',soft:'12px',square:'4px'})[appearance.corners],
    '--orb-size':({small:'150px',medium:'224px',large:'290px'})[appearance.orb_size]};
  return <div className={`bob-app phase-${phase}`} style={appearanceStyle} data-sidebar={appearance.sidebar} data-details={appearance.details} data-density={appearance.density} data-motion={appearance.motion} data-suggestions={appearance.suggestions} data-messages={appearance.message_style} data-composer={appearance.composer} data-width={appearance.chat_width} data-status={appearance.status} data-orb={appearance.orb_visible}>
    {appearanceOpen && <AppearancePanel appearance={appearance} update={updateAppearance} close={()=>setAppearanceOpen(false)} saving={appearanceSaving} error={appearanceError} />}
    {setup && <PersonalSetup invoke={invoke} onDone={data => { setSetup(false); setSettings(data.settings); setMemories(data.memories); setNotice('All set. Let’s make this feel like your workspace.'); }} />}
    <aside className="sidebar">
      <button type="button" className="brand" aria-label="Go to assistant" onClick={() => setPage("chat")}><span className="brand-mark">B<span /></span><span>BOB<small>Personal assistant</small></span></button>
      <button className="new-chat" aria-label="New conversation" onClick={newChat} disabled={busy}><Plus size={17} /> New conversation <span>+</span></button>
      <div className="section-label">WORKSPACE</div>
      <nav>{navigation.map(({ id, label, icon: Icon }) => <button key={id} className={page === id ? 'nav-item selected' : 'nav-item'} aria-label={label} title={label} onClick={() => setPage(id)}><Icon size={18} />{label}{page === id && <span className="nav-light" />}</button>)}</nav>
      <div className="section-label recent-label">RECENT CONVERSATIONS <span>{conversations.length.toString().padStart(2, '0')}</span></div>
      <div className="conversation-list">{conversations.length === 0 && <p className="quiet">Your conversations will appear here.</p>}{conversations.map(item => <div key={item.id} className={`conversation-row ${conversation === item.id ? 'current' : ''}`}><button disabled={busy} onClick={() => selectConversation(item.id)}><MessageSquare size={13} /><span>{item.title}</span></button><button className="delete-chat" aria-label={`Delete ${item.title}`} disabled={busy} onClick={() => deleteChat(item.id)}><Trash2 size={13} /></button></div>)}</div>
      <button type="button" className="local-card" aria-label="Open local resource settings" onClick={() => openSettings("Unload model after idle")}><ShieldCheck size={18} /><span>Local by design<small>Memory stays on this PC</small></span><span className="tiny-dot" /></button>
      <div className="sidebar-footer"><button type="button" className={`user-avatar${recognizedSpeaker ? ' recognized' : ''}`} aria-label="Manage voice profiles" title={recognizedSpeaker ? `Voice matched to ${recognizedSpeaker.name} · approximate identification` : 'Manage optional voice identification'} onClick={() => openSettings("Recognize my voice")} >{speakerInitials || (settings.speaker_enabled && voiceStatus.speaker?.state === 'uncertain' ? '?' : 'YOU')}</button><div>{recognizedSpeaker?.name || 'Personal workspace'}<small>BOB DESKTOP · 0.11.13</small></div><button type="button" className="sidebar-settings" aria-label="Open settings" onClick={() => setPage("settings")}><Settings2 size={15} /></button></div>
    </aside>
    <section className="workspace">
      <header className="topbar"><div><span className="breadcrumb">Workspace</span><ChevronRight size={13} /><span>{navigation.find(n => n.id === page)?.label}</span></div><div className="topbar-right"><button type="button" className="toolbar-icon" aria-label="Toggle navigation" title="Toggle navigation" disabled={appearanceSaving} onClick={()=>updateAppearance({sidebar:appearance.sidebar==='expanded'?'compact':'expanded'})}><PanelLeft size={18}/></button><button type="button" className="toolbar-icon" aria-label="Customize appearance" title="Make it yours" onClick={()=>setAppearanceOpen(true)}><Palette size={18}/></button><button type="button" className="toolbar-icon" aria-label="Toggle assistant details" title="Assistant details" aria-pressed={appearance.details} disabled={appearanceSaving} onClick={()=>updateAppearance({details:!appearance.details})}><PanelRight size={18}/></button><button type="button" className={`connection-pill ${status.ready ? 'online' : ''}`} aria-label="Manage Ollama connection" onClick={() => openSettings("Ollama address")}><span className="tiny-dot" />{status.ready ? 'OLLAMA CONNECTED' : status.online ? 'MODEL NEEDED' : connected ? 'OLLAMA OFFLINE' : 'DESKTOP PREVIEW'}</button><button type="button" className="local-tag" aria-label="Manage local resources" onClick={() => openSettings("Unload model after idle")}><Cpu size={13} /> ON DEVICE</button></div></header>
      {notice && <div className="notice" role="status"><span>{notice}</span><button aria-label="Dismiss notification" onClick={() => setNotice('')}><X size={16} /></button></div>}
      {busy && phase === 'thinking' && taskProgress && <div className="voice-status" role="status" style={{ padding: '8px 32px' }}><Activity size={15} /><span>{taskProgress}</span></div>}
      {settings.speaker_enabled && voiceStatus.speaker && <div className="voice-status" role="status" style={{ padding: '8px 32px' }}><Mic size={15} /><span>{voiceStatus.speaker.state === 'matched' ? `Voice recognized as ${voiceStatus.speaker.name}` : voiceStatus.speaker.state === 'not_enrolled' ? 'Voice recognition enabled · enroll in Settings' : 'Voice identity uncertain'}</span></div>}
      {page === 'chat' ? <div className="chat-layout"><div className="chat-main"><div className="chat-scroll">
        {settings.finance_enabled && <FinanceWidget invoke={invoke} open={() => setPage('finance')} />}
        {!messages.length ? <div className="welcome"><div className="eyebrow"><span /> PERSONAL INTELLIGENCE</div><Core appearance={appearance} state={orbState} level={orbLevel} onClick={() => handsFree ? stop() : startVoiceSession()} disabled={busy && phase !== "speaking" && !handsFree} label={handsFree ? "End voice from Bob core" : "Talk to Bob"} /><div className="core-caption"><span className="tiny-dot" />{phase === 'listening' ? 'LISTENING TO YOU' : 'READY WHEN YOU ARE'}</div><h1>Your world.<br /><span>One conversation away.</span></h1><p>Speak naturally. Think bigger. Let Bob handle the next step.</p><div className="suggestion-grid">{suggestions.map(({ icon: Icon, title, text, tag }) => <button key={tag} onClick={() => prepareCommand(text)}><div><Icon size={18} /><span>{tag}</span><ChevronRight size={14} /></div><strong>{title}</strong><small>{text}</small></button>)}</div></div>
        : <div className="messages">{messages.map((message, index) => <article key={index} className={`message ${message.role}`}><div className="message-avatar">{message.role === 'assistant' ? <Bot size={18} /> : 'Y'}</div><div className="message-body"><div className="message-meta">{message.role === 'assistant' ? 'BOB' : 'YOU'}{message.role === 'assistant' && <span>PERSONAL AI</span>}</div><div className="markdown">{message.content ? <ReactMarkdown remarkPlugins={[remarkGfm]} components={{ a: ({ href, children }) => <button className="inline-link" onClick={() => invoke('open_link', href)}>{children}<ExternalLink size={12} /></button> }}>{message.content}</ReactMarkdown> : <span className="thinking-dots"><i /><i /><i /></span>}</div>{message.role === 'assistant' && message.content && <button className="read-response" disabled={busy || phase === 'listening' || phase === 'speaking'} onClick={() => readAloud(message.content)}><Volume2 size={13} /> Read aloud</button>}{message.content && <button type="button" className="copy-message" aria-label={message.role === "assistant" ? "Copy reply" : "Copy your message"} onClick={() => copyMessage(message.content)}><Copy size={13} /> Copy</button>}</div></article>)}<div ref={bottom} /></div>}
      </div><div className="composer-area"><div className="voice-status" aria-live="polite">{messages.length > 0 && <Core appearance={appearance} state={orbState} level={orbLevel} />}{phase !== 'idle' ? <><AudioLines size={15} /><span>{phase === 'thinking' ? 'Bob is responding…' : phase === 'listening' ? (voiceStatus.phase === 'loading' ? 'Preparing local speech model…' : voiceStatus.phase === 'transcribing' ? 'Transcribing your words…' : voiceStatus.phase === 'verifying' || voiceStatus.verification_pending ? 'Checking your saved voice…' : `${voiceStatus.aec === 'active' ? (voiceStatus.recording_command ? `Capturing your request · ${voiceStatus.captured_seconds || 0}s` : 'Ready for your next request') : 'Listening · speak after the tone'} · mic ${Math.round(voiceStatus.level * 100)}%`) : 'Bob is speaking…'}</span></> : <><span className="tiny-dot" />Bob is ready to help</>}</div><div className="field-help" aria-live="off" aria-label="Provisional speech caption">{handsFree && voiceStatus.partial_text ? `Hearing: ${voiceStatus.partial_text} …` : null}</div><form className="composer" onSubmit={event => { event.preventDefault(); send(input); }}><textarea ref={inputRef} rows={2} maxLength={16000} aria-label="Message Bob" placeholder="Ask anything, or tell Bob what to do…" value={input} onChange={event => setInput(event.target.value)} onKeyDown={event => { if (event.key === 'Enter' && !event.shiftKey && !event.nativeEvent.isComposing) { event.preventDefault(); send(input); } }} /><div className="composer-toolbar"><button type="button" className="model-shortcut" aria-label="Choose AI model" onClick={() => openSettings("Model")}><Sparkles size={13} />{settings.model}</button><div><button type="button" className={`voice-session-button ${handsFree ? "active" : ""}`} aria-label={handsFree ? "End voice conversation" : "Start voice conversation"} disabled={busy && phase !== "speaking" && !handsFree} onClick={() => handsFree ? stop() : startVoiceSession()}>{handsFree ? <MicOff size={15} /> : <Radio size={15} />}<span>{handsFree ? "End voice" : "Voice"}</span></button><button type="button" className={phase === 'listening' ? 'mic-button active' : 'mic-button'} title="Speak one command" aria-label="Speak one command" disabled={busy && phase !== 'speaking'} onClick={() => phase === 'listening' ? stop() : (busy || phase === 'speaking' ? interruptAndCapture(false) : capture(false))}><Mic size={18} /></button>{busy || phase !== 'idle' ? <button type="button" className="send-button stop-button" aria-label="Stop response or voice" onClick={stop}><Square size={15} /></button> : <button className="send-button" type="submit" aria-label="Send message" disabled={!input.trim()}><ArrowUp size={19} /></button>}</div></div></form><div className="composer-foot"><span>Enter to send <i>·</i> Shift + Enter for a new line</span><button type="button" aria-label="Manage saved memory" onClick={() => setPage("memory")}><ShieldCheck size={11} /> LOCAL MEMORY</button></div></div></div>
      <aside className="insight-panel"><div className="panel-heading">YOUR ASSISTANT <Activity size={14} /></div><div className="status-orb"><Core appearance={appearance} state={orbState} level={orbLevel} /></div><h3>{phase === 'idle' ? 'Standing by' : phase === 'listening' ? 'All ears' : phase === 'speaking' ? 'Speaking' : 'Thinking with you'}</h3><p className="status-copy">{phase === 'idle' ? 'Awaiting your instructions.' : 'One conversation. Full attention.'}</p><div className="metrics"><button type="button" aria-label="Configure engine" onClick={() => openSettings("Ollama address")}><span>Engine</span><strong>Ollama <span className={`tiny-dot ${status.ready ? '' : 'amber'}`} /></strong></button><button type="button" aria-label="Configure model" onClick={() => openSettings("Model")}><span>Model</span><strong title={settings.model}>{settings.model}</strong></button><button type="button" aria-label="Open memory from status" onClick={() => setPage("memory")}><span>Memory</span><strong>{memories.length} saved facts</strong></button><button type="button" aria-label="Configure voice" onClick={() => openSettings("Bob’s voice")}><span>Voice</span><strong>Whisper · local</strong></button></div><button className={`voice-mode ${handsFree ? 'enabled' : ''}`} disabled={busy && !handsFree && phase !== 'speaking'} onClick={() => handsFree ? stop() : startVoiceSession()}>{handsFree ? <MicOff size={18} /> : <Radio size={18} />}<div>{handsFree ? 'End voice conversation' : 'Start voice conversation'}<small>{handsFree ? 'Say “stop listening” to finish' : 'Say Hey Bob before each request'}</small></div></button><p className="voice-hint">{voiceStatus.error || voiceStatus.voice_notice || (voiceStatus.aec === 'active' ? (!settings.speaker_enabled ? 'Saved-voice recognition is off: voice cannot interrupt replies. Enable it and select yourself in Settings; Stop is always available.' : settings.audio_verified_interruptions === false ? 'Voice interruptions are off. Use Stop, or enable verified voice interruptions in Settings.' : settings.audio_wake_phrase_only !== false ? 'Say “Hey Bob” or “Okay Bob” before each request. Say “Hey Bob, please stop talking” to interrupt.' : settings.audio_verified_interruptions !== false ? (settings.speaker_enabled ? 'Completed saved-voice guard · say “Hey Bob, please stop talking” to interrupt.' : 'Enable your saved voice in Settings for voice interruptions. The Stop button is available.') : 'Completed saved-voice and explicit-phrase checks protect playback.') : (settings.wake_enabled ? (voiceStatus.wake === 'ready' ? 'Say “Hey Bob”, wait for the tone, then speak. Wake listening stays on in the tray.' : `Wake listener: ${voiceStatus.wake}. You can also press the microphone.`) : 'Wake listening is off. Press the microphone and speak after the tone.'))}</p><div className="context-card"><Brain size={18} /><h4>Context that carries forward</h4><p>Your recent messages stay in the conversation. Say “remember that…” to save something for next time.</p><button onClick={() => setPage('memory')}>Explore memory <ChevronRight size={13} /></button></div><div className="panel-bottom"><span className="tiny-dot" /> BUILT FOR YOUR WORLD</div></aside></div>
      : page === 'day' ? <DayPlannerPanel key={dayResultRevision} invoke={invoke} requestedDay={requestedDay} onSettings={setSettings} progress={dayProgress} talking={busy || handsFree} />
      : page === 'automations' ? <AutomationsPanel invoke={invoke} send={send} busy={busy} />
      : page === 'welcome' ? <WelcomePanel invoke={invoke} onSettings={() => setPage('settings')} prepareCommand={prepareCommand} />
      : page === 'finance' ? <FinancePanel enabled={!!settings.finance_enabled} invoke={invoke} setSettings={setSettings} />
      : <Panels key={page} page={page} settings={settings} setSettings={setSettings} status={status} checkConnection={checkConnection} memories={memories} setMemories={setMemories} apps={apps} invoke={invoke} send={send} busy={busy} setNotice={setNotice} prepareCommand={prepareCommand} openSetup={() => setSetup(true)} />}
    </section>
  </div>;
}

