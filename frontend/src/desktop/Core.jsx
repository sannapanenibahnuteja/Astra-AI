export default function Core({ state = 'idle' }) {
  return <div className={`core-scene ${state}`} aria-label={`Bob ${state}`}>
    <svg className="hud-reticle" viewBox="0 0 260 260" aria-hidden="true">
      <defs><radialGradient id="core-glow"><stop offset="0" stopColor="#56eaff" stopOpacity=".24"/><stop offset="1" stopColor="#19c9ff" stopOpacity="0"/></radialGradient></defs>
      <circle cx="130" cy="130" r="126" fill="url(#core-glow)" />
      <g fill="none" stroke="#6ceaff">
        <circle className="reticle-slow" cx="130" cy="130" r="116" strokeWidth="2" strokeDasharray="1 5" opacity=".5" />
        <circle cx="130" cy="130" r="109" strokeWidth=".5" opacity=".45" />
        <circle className="reticle-reverse" cx="130" cy="130" r="103" strokeWidth="4" strokeDasharray="94 15 8 6 32 61" opacity=".6" />
        <circle cx="130" cy="130" r="95" strokeWidth=".5" opacity=".45" />
        <circle className="reticle-slow" cx="130" cy="130" r="88" strokeWidth="9" strokeDasharray="2 8" opacity=".23" />
        <circle className="reticle-reverse" cx="130" cy="130" r="76" strokeWidth="1.5" strokeDasharray="67 18 12 34" opacity=".8" />
        <path d="M130 1v16M130 243v16M1 130h16M243 130h16M39 39l11 11M210 210l11 11M39 221l11-11M210 50l11-11" strokeWidth="1" opacity=".8" />
        <path d="M102 10h-15l-9 10M158 250h15l9-10M10 158v15l10 9M250 102V87l-10-9" stroke="#edb75f" strokeWidth="1.5" opacity=".8" />
      </g>
    </svg>
    <span className="hud-coordinate hud-coordinate-left">NEURAL<br/>INTERFACE</span><span className="hud-coordinate hud-coordinate-right">LOCAL<br/>INTELLIGENCE</span>
    <div className="core-orbit orbit-one" /><div className="core-orbit orbit-two" />
    <div className="core-ticks" /><div className="core-halo" /><div className="core-sphere"><div className="core-sheen" /><span>B</span></div>
    <div className="core-satellite" /><div className="core-floor" />
  </div>;
}
