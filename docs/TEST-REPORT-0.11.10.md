# Bob 0.11.10 verification — 26 October 2026

[Machine-readable evidence](TEST-RESULTS-0.11.10.json).

- **519 Python regressions passed** in 42.007s, including six new quiet-room
  tests. A six-test follow-up passed after strengthening the active-session mode
  switch guard to compare the actual running policy rather than a preference
  that could have changed on disk.
- Frontend production build and audio-panel ESLint passed.
- **187 packaged native UI checks passed**, including Quiet/Balanced selection
  and save, existing Finance controls, voice handoff and appearance/settings.
- Native synthetic audio checks passed, including seeded noise/tap rejection
  using the actual local neural detector under both Balanced and Quiet policies.
  Echo diagnostics retained 17.7dB seeded attenuation. No microphone was used.
- Startup/voice handoff passed with eight navigation destinations and no
  horizontal overflow at 1366px. X-button shutdown stopped fixture schedulers
  and reminders.
- The user's local `audio_room_mode` preference alone was set to `quiet` for the
  next app launch. Calibration, identity settings, Finance data and other
  preferences were not changed. No private measurements or profiles are bundled.

Coverage confirms that quiet completed utterances with more gaps may reach final
verification; short impulses and sparse speech evidence cannot. A shorter neural
speech span can qualify in Quiet mode, but model failure retains playback. Quiet
mode keeps completed authorization and disables sound-only lowering/stopping.
Invalid modes and mid-session changes are rejected, including when the stored
preference differs from the running engine. Speaker thresholds stay unchanged.

The first packaged controls run encountered an asynchronous test race: a stale
“Settings saved” notice allowed a public-mode assertion before persistence
finished. The saved value was subsequently observed in SQLite. The fixture now
waits for the actual setting value; the final packaged rerun passed all checks.
The application setting was not bypassed or the assertion removed.

UI integrations are isolated fixtures; synthetic DSP and neural checks do not
establish real quiet-room speech accuracy. No live microphone test, provider call
or real external action was performed. Earlier live interruption acceptance
remains pending; this release does not declare the broader voice issue resolved.

[Quiet-room setup and manual tests](RELEASE-0.11.10.md).
