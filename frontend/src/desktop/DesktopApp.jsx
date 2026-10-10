import { useCallback, useEffect, useRef, useState } from 'react';
import { Activity, ArrowUp, AudioLines, Bot, Brain, ChevronRight, Command, Cpu, ExternalLink, Globe, Layers, MessageSquare, Mic, MicOff, Plus, Radio, Settings2, ShieldCheck, Sparkles, Square, Trash2, Volume2, X } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { nativeApi, pause } from './bridge';
import Core from './Core';
import Panels from './Panels';
import './desktop.css';
import './hud.css';
import './minimal.css';

const defaults = { ollama_url: 'http://127.0.0.1:11434', model: 'qwen3:8b', personality: '', bob_url: '', voice_enabled: true, voice_rate: 0, voice_language: 'en-US', wake_enabled: true, greeting_enabled: true, auto_listen: true, project_path: '', keep_alive: '2m', context_size: 4096 };
const suggestions = [
  { icon: Command, title: 'Your PC, one sentence away', text: 'Open calculator', tag: 'WINDOWS' },
  { icon: Brain, title: 'A little more personal', text: 'Remember that my preferred name is Bhanu', tag: 'MEMORY' },
  { icon: Globe, title: 'Follow your curiosity', text: 'Search the web for the latest space discoveries', tag: 'EXPLORE' },
  { icon: Sparkles, title: 'Make room for ideas', text: 'Help me plan a productive morning', tag: 'THINK' },
];
const navigation = [{ id: 'chat', label: 'Assistant', icon: MessageSquare }, { id: 'memory', label: 'Memory', icon: Brain }, { id: 'capabilities', label: 'Capabilities', icon: Layers }, { id: 'settings', label: 'Settings', icon: Settings2 }];

export default function DesktopApp() {
  const [connected, setConnected] = useState(false);
  const [page, setPage] = useState('chat');
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
  const submitRef = useRef(null);
  const inputRef = useRef(null);

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
        setConnected(true); setSettings(data.settings);
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
      if ((event.ctrlKey || event.metaKey) && event.key === '/') { event.preventDefault(); setPage('chat'); inputRef.current?.focus(); }
    }
    window.addEventListener('keydown', shortcut);
    return () => window.removeEventListener('keydown', shortcut);
  }, []);

  async function send(text, spoken = false, speaker = null) {
    text = text.trim();
    if (!text || active.current) return;
    if (!connected) { setNotice('Launch Bob.exe for chat, voice and Windows actions.'); return; }
    active.current = true; setBusy(true); setNotice(''); setInput(''); setPage('chat'); setPhase('thinking');
    let finalText, voiceManaged;
    setTaskProgress('Planning your request');
    try {
      if (!spoken) { voiceEpoch.current += 1; voiceLoop.current = false; setHandsFree(false); await nativeApi().stop_voice(); }
      const id = spoken && speaker?.state === 'matched' ? await nativeApi().voice_conversation(conversation, speaker) : conversation || await nativeApi().new_conversation();
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
        setPhase('idle');
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

        } else {
          pendingTranscript = null;
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
    let alive = true, timer;
    async function pollVoice() {
      try { const value = await nativeApi().voice_status(); if (alive) { setVoiceStatus(value); if (active.current && capturing.current) setPhase(value.phase === 'speaking' ? 'speaking' : 'thinking'); } } catch { /* connection shutting down */ }
      if (alive) timer = setTimeout(pollVoice, capturing.current ? 200 : 1500);
    }
    function wake() { captureRef.current?.(true); }
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

  return <div className="bob-app">
    <aside className="sidebar">
      <div className="brand"><div className="brand-mark">B<span /></div><div>BOB<small>PERSONAL INTELLIGENCE</small></div></div>
      <button className="new-chat" onClick={newChat} disabled={busy}><Plus size={17} /> New conversation <span>+</span></button>
      <div className="section-label">WORKSPACE</div>
      <nav>{navigation.map(({ id, label, icon: Icon }) => <button key={id} className={page === id ? 'nav-item selected' : 'nav-item'} onClick={() => setPage(id)}><Icon size={18} />{label}{page === id && <span className="nav-light" />}</button>)}</nav>
      <div className="section-label recent-label">RECENT CONVERSATIONS <span>{conversations.length.toString().padStart(2, '0')}</span></div>
      <div className="conversation-list">{conversations.length === 0 && <p className="quiet">Your conversations will appear here.</p>}{conversations.map(item => <div key={item.id} className={`conversation-row ${conversation === item.id ? 'current' : ''}`}><button disabled={busy} onClick={() => selectConversation(item.id)}><MessageSquare size={13} /><span>{item.title}</span></button><button className="delete-chat" aria-label={`Delete ${item.title}`} disabled={busy} onClick={() => deleteChat(item.id)}><Trash2 size={13} /></button></div>)}</div>
      <div className="local-card"><ShieldCheck size={18} /><div>Local by design<small>Memory stays on this PC</small></div><span className="tiny-dot" /></div>
      <div className="sidebar-footer"><div className="user-avatar">YOU</div><div>Personal workspace<small>BOB DESKTOP · 0.10.20</small></div><Settings2 size={15} /></div>
    </aside>
    <section className="workspace">
      <header className="topbar"><div><span className="breadcrumb">Workspace</span><ChevronRight size={13} /><span>{navigation.find(n => n.id === page)?.label}</span></div><div className="topbar-right"><span className={`connection-pill ${status.ready ? 'online' : ''}`}><span className="tiny-dot" />{status.ready ? 'OLLAMA CONNECTED' : status.online ? 'MODEL NEEDED' : connected ? 'OLLAMA OFFLINE' : 'DESKTOP PREVIEW'}</span><span className="local-tag"><Cpu size={13} /> ON DEVICE</span></div></header>
      {notice && <div className="notice" role="status"><span>{notice}</span><button aria-label="Dismiss notification" onClick={() => setNotice('')}><X size={16} /></button></div>}
      {busy && phase === 'thinking' && taskProgress && <div className="voice-status" role="status" style={{ padding: '8px 32px' }}><Activity size={15} /><span>{taskProgress}</span></div>}
      {settings.speaker_enabled && voiceStatus.speaker && <div className="voice-status" role="status" style={{ padding: '8px 32px' }}><Mic size={15} /><span>{voiceStatus.speaker.state === 'matched' ? `Voice recognized as ${voiceStatus.speaker.name}` : voiceStatus.speaker.state === 'not_enrolled' ? 'Voice recognition enabled · enroll in Settings' : 'Voice identity uncertain'}</span></div>}
      {page === 'chat' ? <div className="chat-layout"><div className="chat-main"><div className="chat-scroll">
        {!messages.length ? <div className="welcome"><div className="eyebrow"><span /> B O B  /  PERSONAL INTELLIGENCE</div><Core state={phase} /><div className="core-caption"><span className="tiny-dot" />{phase === 'listening' ? 'LISTENING TO YOU' : 'READY WHEN YOU ARE'}</div><h1>Your mind. Amplified.<br /><span>What are we doing next?</span></h1><p>A thought, a question, a command. Start anywhere.</p><div className="suggestion-grid">{suggestions.map(({ icon: Icon, title, text, tag }) => <button key={tag} onClick={() => { setInput(text); inputRef.current?.focus(); }}><div><Icon size={18} /><span>{tag}</span><ChevronRight size={14} /></div><strong>{title}</strong><small>{text}</small></button>)}</div></div>
        : <div className="messages">{messages.map((message, index) => <article key={index} className={`message ${message.role}`}><div className="message-avatar">{message.role === 'assistant' ? <Bot size={18} /> : 'Y'}</div><div className="message-body"><div className="message-meta">{message.role === 'assistant' ? 'BOB' : 'YOU'}{message.role === 'assistant' && <span>PERSONAL AI</span>}</div><div className="markdown">{message.content ? <ReactMarkdown remarkPlugins={[remarkGfm]} components={{ a: ({ href, children }) => <button className="inline-link" onClick={() => invoke('open_link', href)}>{children}<ExternalLink size={12} /></button> }}>{message.content}</ReactMarkdown> : <span className="thinking-dots"><i /><i /><i /></span>}</div>{message.role === 'assistant' && message.content && <button className="read-response" disabled={busy || phase === 'listening'} onClick={async () => { setPhase('speaking'); await invoke('speak', message.content); setPhase('idle'); }}><Volume2 size={13} /> Read aloud</button>}</div></article>)}<div ref={bottom} /></div>}
      </div><div className="composer-area"><div className="voice-status" aria-live="polite">{phase !== 'idle' ? <><AudioLines size={15} /><span>{phase === 'thinking' ? 'Bob is responding…' : phase === 'listening' ? (voiceStatus.phase === 'loading' ? 'Preparing local speech model…' : voiceStatus.phase === 'transcribing' ? 'Transcribing your words…' : `${voiceStatus.aec === 'active' ? (voiceStatus.recording_command ? `Capturing your request · ${voiceStatus.captured_seconds || 0}s` : 'Ready for your next request') : 'Listening · speak after the tone'} · mic ${Math.round(voiceStatus.level * 100)}%`) : 'Bob is speaking…'}</span></> : <><span className="tiny-dot" />Bob is ready to help</>}</div><form className="composer" onSubmit={event => { event.preventDefault(); send(input); }}><textarea ref={inputRef} rows={2} maxLength={16000} aria-label="Message Bob" placeholder="Ask anything, or tell Bob what to do…" value={input} onChange={event => setInput(event.target.value)} onKeyDown={event => { if (event.key === 'Enter' && !event.shiftKey && !event.nativeEvent.isComposing) { event.preventDefault(); send(input); } }} /><div className="composer-toolbar"><span><Sparkles size={13} />{settings.model}</span><div><button type="button" className={phase === 'listening' ? 'mic-button active' : 'mic-button'} title="Speak one command" aria-label="Speak one command" disabled={busy && phase !== 'speaking'} onClick={() => phase === 'listening' ? stop() : (busy || phase === 'speaking' ? interruptAndCapture(false) : capture(false))}><Mic size={18} /></button>{busy || phase !== 'idle' ? <button type="button" className="send-button stop-button" aria-label="Stop response or voice" onClick={stop}><Square size={15} /></button> : <button className="send-button" type="submit" aria-label="Send message" disabled={!input.trim()}><ArrowUp size={19} /></button>}</div></div></form><div className="composer-foot"><span>Enter to send <i>·</i> Shift + Enter for a new line</span><span><ShieldCheck size={11} /> LOCAL MEMORY</span></div></div></div>
      <aside className="insight-panel"><div className="panel-heading">YOUR ASSISTANT <Activity size={14} /></div><div className="status-orb"><Core state={phase} /></div><h3>{phase === 'idle' ? 'Standing by' : phase === 'listening' ? 'All ears' : phase === 'speaking' ? 'Speaking' : 'Thinking with you'}</h3><p className="status-copy">{phase === 'idle' ? 'Awaiting your instructions.' : 'One conversation. Full attention.'}</p><div className="metrics"><div><span>Engine</span><strong>Ollama <span className={`tiny-dot ${status.ready ? '' : 'amber'}`} /></strong></div><div><span>Model</span><strong title={settings.model}>{settings.model}</strong></div><div><span>Memory</span><strong>{memories.length} saved facts</strong></div><div><span>Voice</span><strong>Whisper · local</strong></div></div><button className={`voice-mode ${handsFree ? 'enabled' : ''}`} disabled={busy && !handsFree && phase !== 'speaking'} onClick={() => handsFree ? stop() : (busy || phase === 'speaking' ? interruptAndCapture(true) : capture(true))}>{handsFree ? <MicOff size={18} /> : <Radio size={18} />}<div>{handsFree ? 'End voice conversation' : 'Start voice conversation'}<small>{handsFree ? 'Say “stop listening” to finish' : 'Speak naturally · interrupt anytime'}</small></div></button><p className="voice-hint">{voiceStatus.error || (voiceStatus.aec === 'active' ? 'Echo cancellation active · speak anytime to interrupt Bob.' : (settings.wake_enabled ? (voiceStatus.wake === 'ready' ? 'Say “Hey Bob”, wait for the tone, then speak. Wake listening stays on in the tray.' : `Wake listener: ${voiceStatus.wake}. You can also press the microphone.`) : 'Wake listening is off. Press the microphone and speak after the tone.'))}</p><div className="context-card"><Brain size={18} /><h4>Context that carries forward</h4><p>Your recent messages stay in the conversation. Say “remember that…” to save something for next time.</p><button onClick={() => setPage('memory')}>Explore memory <ChevronRight size={13} /></button></div><div className="panel-bottom"><span className="tiny-dot" /> BUILT FOR YOUR WORLD</div></aside></div>
      : <Panels page={page} settings={settings} setSettings={setSettings} status={status} checkConnection={checkConnection} memories={memories} setMemories={setMemories} apps={apps} invoke={invoke} send={send} busy={busy} setNotice={setNotice} />}
    </section>
  </div>;
}

