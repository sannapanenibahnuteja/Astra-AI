# Bob 0.10.12 — Personality you can adjust

Changes from 0.10.11:

- Adds Funny companion, Serious professional, Discreet assistant and Candid
  advisor alongside the existing personality presets.
- Settings → Voice & personality includes Humor, Seriousness, Discretion and
  Honesty/candor sliders. Presets have different defaults; switching presets resets
  trait overrides. Reset traits restores that preset's defaults.
- Voice and text can change tone without waiting for model inference. Changes
  persist across restarts and apply to subsequent conversational replies.
- Honesty controls tactful versus frank wording. All settings require truthfulness,
  clear uncertainty and truthful execution results. Serious topics suppress jokes.
- Discretion asks the model to avoid volunteering sensitive details. It is a tone
  preference, not an access-control change or a guarantee of privacy.

## Setup and test

1. Quit old Bob from the tray and start this version's Bob.exe.
2. Open Settings → Voice & personality. Choose **Funny companion**, adjust the
   sliders if desired, and click **Save settings**.
3. Ask **“Tell me a short joke about computers.”** Then ask a practical follow-up.
   Bob should stay useful rather than adding a joke to every sentence.
4. Say **“Be serious.”** Then **“Help me plan my afternoon.”** Check the more focused
   tone. **“Be funnier”** switches back to Funny companion.
5. Say **“Set your humor to 80”**, **“Set discretion to 95”**, or **“Set honesty to
   100.”** Reopen Settings to check the saved values. **“Stop joking”** sets humor
   to zero. British “humour” spelling is supported.
6. Say **“Be discreet.”** Then ask a general planning question. Bob should avoid
   volunteering private details. Say **“Be more honest”** for candid feedback,
   then **“What is wrong with my plan to do ten projects this weekend?”**
7. Set honesty/candor low and ask an uncertain question. Bob should still admit
   uncertainty; this slider never permits dishonesty.
8. Restart Bob and check that your personality preferences remain saved.

Both model-generated text and spoken replies use this style. The existing speech
engine still determines vocal sound; this does not add emotional voice synthesis.
Fast native commands keep brief factual execution replies and confirmations.
Tone quality depends on the selected Ollama model and custom instructions.
No new action permissions or account integrations are introduced.
