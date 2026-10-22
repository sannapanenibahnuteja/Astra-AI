import { useEffect, useRef } from 'react';
import { X, RotateCcw, Sparkles } from 'lucide-react';

import { appearanceDefaults, accents } from './appearanceTheme';
const groups = [
 ['Layout', [['sidebar','Navigation',['expanded','compact','hidden']],['chat_width','Conversation width',['focused','wide']],['density','Spacing',['compact','comfortable','roomy']],['message_style','Messages',['plain','bubbles']],['composer','Message box',['compact','comfortable']]]],
 ['Type & shape', [['font_size','Text size',['small','medium','large','extra large']],['font_family','Typeface',['system','rounded','mono']],['corners','Corners',['round','soft','square']]]],
 ['The orb', [['orb_size','Orb size',['small','medium','large']],['orb_color','Orb palette',['multicolor','accent']],['orb_speed','Orb movement',['calm','balanced','lively']],['motion','Interaction motion',['off','subtle','playful']]]],
 ['Surfaces', [['background','Background',['black','graphite','midnight']],['sidebar_color','Sidebar surface',['default','black','graphite','midnight']],['composer_color','Message box surface',['default','black','graphite','midnight']]]],
];
export default function AppearancePanel({ appearance, update, close, saving, error }) {
 const dialog=useRef(null);
 useEffect(()=>{ const node=dialog.current;node.showModal();return()=>node.close(); },[]);
 return <dialog ref={dialog} className="appearance-panel" aria-labelledby="appearance-title" onCancel={event=>{event.preventDefault();close();}} onClick={event=>{if(event.target===dialog.current)close();}}>
 <div className="appearance-inner"><header><div><span className="eyebrow">MAKE IT YOURS</span><h2 id="appearance-title">Your space. Your Bob.</h2></div><button type="button" aria-label="Close appearance" onClick={close}><X size={20}/></button></header>
 <p className="appearance-intro">A little more you. Changes save automatically. Try saying <strong>“Hey Bob, make the accent mint.”</strong></p>
 <div className="appearance-presets">{['focus','studio','playful'].map(name=><button key={name} disabled={saving} onClick={()=>update(name==='focus'?{details:false,suggestions:false,sidebar:'compact',motion:'subtle'}:name==='studio'?{details:true,suggestions:true,sidebar:'expanded',motion:'subtle',chat_width:'wide'}:{accent:'rose',motion:'playful',orb_speed:'lively',corners:'round'})}><Sparkles size={14}/>{name}</button>)}</div>
 <section><h3>Accent</h3><div className="accent-swatches">{Object.entries(accents).map(([name,color])=><button key={name} disabled={saving} aria-label={`Accent ${name}`} aria-pressed={appearance.accent===name} style={{'--swatch':color}} onClick={()=>update({accent:name})}><span/>{name}</button>)}</div></section>
 {groups.map(([name,fields])=><section key={name}><h3>{name}</h3><div className="appearance-fields">{fields.map(([key,label,values])=><label key={key}>{label}<select disabled={saving} value={appearance[key]} onChange={event=>update({[key]:event.target.value})}>{values.map(value=><option key={value} value={value}>{value}</option>)}</select></label>)}</div></section>)}
 <section><h3>Only what you need</h3>{[['details','Assistant details'],['suggestions','Starter suggestions'],['status','Status labels'],['orb_visible','Show the orb']].map(([key,label])=><label className="toggle-row" key={key}>{label}<input type="checkbox" disabled={saving} checked={appearance[key]} onChange={event=>update({[key]:event.target.checked})}/></label>)}</section>
 <footer><span role="status">{error || (saving?'Saving…':'Saved on this PC')}</span><button disabled={saving} onClick={()=>update(appearanceDefaults)}><RotateCcw size={14}/> Reset appearance</button></footer>
 <p className="field-help">Voice examples: “hide details”, “make the orb larger”, “set the sidebar compact”, “turn off animations”, “reset appearance”. Add Hey Bob before each voice request. Appearance changes do not alter voice recognition, memory or action permissions.</p>
 </div></dialog>;
}
