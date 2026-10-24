# Selling the complete Bob app to customers

Bob remains your project. The commercial direction is selling access to the
complete Windows app to end users, rather than transferring its source or ownership.
This release adds a customer setup foundation; it is not yet a completed paid launch.

## Product promise

**Your private Windows copilot. Talk naturally, launch apps, remember what
matters, and build daily routines—with local AI on your PC.**

Use this promise with the actual limits: local conversation requires Ollama and
a separate downloaded model; some optional providers send data off-device and
charge separately. Sell supported, demonstrable workflows rather than “any task,”
flawless speaker recognition or unmeasured instant performance.

Keep the initial offer simple: one complete Bob desktop edition. Do not create
artificial feature locks before reliability is established. Price, payment
provider, update entitlement, trial terms and support commitment remain decisions
for the owner. No checkout, subscription or license activation is implemented by
this release. Do not accept payment for an unavailable entitlement.

## New customer setup flow

1. Install Ollama and download a supported conversation model. Launch Bob.exe
   with its `_internal` folder beside it.
2. Optional personal setup asks what Bob should remember. Skip any question.
3. **Get started** checks connection/model availability, speech files, input and
   output devices. Calibration and personal voice focus are optional.
4. Open Settings to fix unavailable items. **Check again** refreshes on demand;
   there is no new background polling or microphone recording.
5. Pick a first task. It is placed in the composer, not executed automatically.
   Send it and verify the actual result. Review remembered facts in Memory.
6. **Copy setup summary** copies only fixed readiness states. Customers can
   review that text before sharing it with support. It includes no chats,
   profile names, device names, server addresses, paths or credentials.

Availability checks do not certify permissions, acoustic quality, model tool
compatibility, speech synthesis or real action execution. Use the live tests below.

## Customer acceptance tests

Use a disposable Windows account, temporary files and test conversations.

| Test | Customer action | Observe |
| --- | --- | --- |
| Initial setup | Open Get started; Check again | Available essentials or concrete next steps; no automatic recording |
| Disconnected model | Stop Ollama, check again, then restart it | Local intelligence needs setup, then recovers |
| First action | Choose Open calculator, then Send | Composer changes first; actual Calculator window opens after Send |
| Web fallback | Say “Hey Bob, open YouTube” | Browser actually opens YouTube |
| Complete speech | Ask for an explanation with voice output on | Whole reply is spoken; Test voice output also works |
| Voice focus | Enroll a consenting tester and test a match | Accurate enough for this setup; disclose observed failures |
| Interruption | During a reply, use the saved voice and explicit wake/stop phrase | Eligible completed speech stops the reply; small noises do not |
| Memory | Remember a test preference; inspect and delete it | Fact is visible, then removed in Memory |
| Routine | Create a daily test routine a few minutes ahead | Runs once at intended local time while Bob/PC stay awake; pause/resume works |
| Personalization | Adjust orb/accent, restart | Settings persist; animations respect reduced motion |
| Support | Copy setup summary and inspect pasted text | Only readiness states and scope notice |
| Shutdown | Press window X | App exits; microphone, local scheduling and phone access stop |

Repeat on representative laptops, desktops and microphones. Record cold launch,
first text, first audio and actual action completion separately, together with
hardware/model details. No aggregate performance claim is established here.

## Honest 60-second demonstration

Show a real Windows session: open Calculator by voice, open a website without an
installed app, save and delete a preference, show a daily routine, then customize
the orb. Show the actual results and the setup screen. Mention that Ollama is
required. Do not invent testimonials, customer counts, time savings or benchmarks.
Show phone calls only when actually configured and authorized; they are optional
paid-provider functionality, not included free service.

## Before charging customers

- Finish live acceptance tests and address the failures before advertising the
  affected workflows. Automated fixture results are not complete field validation.
- Ship a clean, signed installer and an upgrade/rollback strategy. The current
  application is a portable unsigned EXE folder. Publisher signing needs a real
  signing identity and certificate; this release does not fabricate one.
- Establish project ownership and licensing. `docs/LICENSE` is currently only a
  partial MIT notice. Do not silently replace it or claim exclusive rights.
  Review redistribution terms for all dependencies, models, artwork and fonts;
  the existing speaker notice is not a full third-party audit.
- Complete a security review of credentials, remote access, pairing and tool
  permissions. Inspect repository history for secrets before public distribution.
- Choose payment/entitlement handling and test purchase, activation, refund and
  recovery with provider test accounts before taking real payments.
- Publish accurate privacy, support, update and purchase terms. Explain which
  integrations leave the PC, what needs extra accounts, and how to delete data.
- Start with a clearly labeled, limited pilot. Collect consent-based bug reports
  and measured workflow success. Resolve recurring failures before a broad launch.

The customer-ready product is the app plus reliable installation, support and
updates. This document is a delivery checklist, not a valuation or assurance of
commercial readiness.
