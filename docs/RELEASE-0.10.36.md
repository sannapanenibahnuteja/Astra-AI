# Bob 0.10.36

- Separates the audio used for identifying a speaker from the heavily noise-suppressed audio used for transcription. Speaker verification now uses its own synchronized echo canceller without extra noise suppression, making the signal closer to enrollment input. Whisper retains noise suppression. Both paths share the same microphone blocks, playback reference and stream delay.
- The completed turn keeps both channels aligned. Only a successful saved-voice match can release the cleaned transcription channel to Whisper or interrupt a reply. Matching thresholds and ambiguity checks are unchanged.
- Allows short live requests with at least half a second of usable speech to reach the matcher instead of rejecting everything below one second. The higher short-utterance similarity threshold, template consensus and ambiguity checks remain; enrollment still requires four seconds per sample. Very brief or uncertain speech can still be rejected.
- Fixes a confidently matched full request failing to interrupt Bob after an early partial voice check missed. The full match can now interrupt once for that turn; stale or duplicate results cannot stop a newer reply.
- Adds Re-record next to each saved voice. Record three replacement samples for that same profile; the encrypted old profile remains intact until all three are accepted. The profile ID, memories, conversation association and personality are preserved. Cancel re-recording keeps the old enrollment.
- Newly completed enrollment selects the profile just created instead of showing another saved person's sample statistics.

## Test with your voice

1. Close old Bob. Launch this Bob.exe with _internal beside it. Your existing microphone calibration remains available.
2. Stop voice mode. Settings → Recognize my voice → Test voice match. Speak a full sentence in your normal voice. This runs a diagnostic, not a command.
3. If Test voice match passes, keep your profile. Start conversation and say “Bob, please open calculator for me.” Speaker verification should now use the signal closer to enrollment, while transcription uses cleaned speech.
4. If your existing profile still fails, click Re-record beside the profile whose memories you want to keep. Record three varied eight-to-twelve-second takes, using Finish sample each time. You do not need to delete the profile or add another name.
5. Try Cancel re-recording after one accepted take. The old profile and memories must remain. Complete three takes only when you want to replace that enrollment.
6. Test a new sentence and an interruption while Bob replies. Unknown people must still be ignored while saved-voice listening is enabled.

Identification remains approximate. These changes do not guarantee recognition in every room, separate overlapping speakers or turn voice matching into authentication. Existing duplicate profiles are not automatically merged or deleted. The standalone voice-check helper records only after a user click, keeps audio in memory, saves anonymous local diagnostic scores and never executes commands or changes profiles.

The live full-sentence diagnostic passed on both raw and noise-suppressed microphone audio without changing the user profile. This supports keeping the existing enrollment; it does not establish that every short request will match.
