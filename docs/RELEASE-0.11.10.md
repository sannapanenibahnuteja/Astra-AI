# Bob 0.11.10 — more relaxed quiet-room listening

Settings → Conversational audio → **Room listening mode** now offers:

- **Quiet room:** less aggressive speech detection, a lower bounded acoustic
  floor, more tolerance for gaps in a completed utterance, and more sensitive
  independent neural speech verification for softer/shorter speech.
- **Balanced:** retains the previous behavior for mixed environments.

End the voice conversation and response before changing modes, click **Save
settings**, then start a new voice session. Existing installations default to
Balanced unless configured otherwise. The requested local quiet-room preference
can be saved separately without changing voice profiles or calibration.

Saved-speaker thresholds, explicit wake/request rules, word confidence, completed
transcripts and response-scoped one-use cancellation permits are unchanged. Quiet
mode does not enable sound-only interruption or playback lowering. It changes
listening sensitivity, not pitch, speaking pace or the selected output voice.

## Use and test

1. Quit the older Bob. Open `dist/release-0.11.10/Bob/Bob.exe` with `_internal`
   beside it.
2. Choose **Quiet room** under **Room listening mode** and save before starting
   voice conversation. Say a normal request softly, with natural gaps.
3. During a reply, use your saved voice and the complete phrase **“Hey Bob,
   please stop talking.”** A wake phrase alone still cannot stop a reply.
4. Check that isolated taps/coughs do not stop replies. Quiet mode is more
   sensitive to speech candidates; final neural, identity and intent checks still
   decide whether an interruption is allowed.
5. Select **Balanced** again when the room becomes noisy. Stop the voice session
   before switching. No microphone calibration or re-enrollment is required merely
   to change this preference.

Generated-noise tests do not establish live microphone accuracy. The unresolved
live interruption acceptance from 0.11.8 is not marked passed by this update.
