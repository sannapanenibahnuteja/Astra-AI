# Bob 0.10.11 — Voice matching refinements

Changes from 0.10.10:

- Removes DC offset and leading/trailing silence, normalizes microphone gain
  gently, and caps model input at eight seconds to bound inference work.
- Checks clipping, insufficient speech and strong stationary broadband hiss.
  Rejected samples explain how to retry. These checks do not remove all noise.
- Enrollment requires three seconds of useful audio per sample and compares each
  new embedding with every earlier sample before accepting it.
- New encrypted profiles retain all three embedding templates. Matching requires
  the averaged profile and at least two templates to agree.
- Short requests can be matched after at least 1.2 seconds of captured audio and
  one second of useful audio, with a stricter similarity cutoff below two seconds.
- Optional recognition remains off by default. Settings offers Balanced (0.65)
  and Strict (0.75); short-request cutoffs increase by 0.07. These are heuristic
  cosine cutoffs, not accuracy percentages or calibrated probabilities.
- **Test voice match** records a sentence and displays the result without
  executing its words as commands. Matching remains a convenience, not a login.

## Quick setup and testing

1. Quit old Bob and start this version's EXE. Open Settings → Recognize my voice.
2. Existing profiles still work. For the new three-template checks, delete the old
   profile and record all three sentences again in a quiet room.
3. Enable the optional switch, choose Balanced, and Save settings.
4. Stop any active voice conversation. Click **Test voice match** and say a new
   sentence for five seconds. Check that your name appears.
5. With their agreement, let another person test a sentence. If they match your
   profile, choose Strict, save and test both voices again. Strict can reject your
   own voice more often too. Re-enroll if matching remains unreliable.
6. Test ordinary voice commands and short requests. An uncertain voice identity
   does not block otherwise valid commands. Noise or very short speech may need
   a longer sentence; wake-word standby is not restricted to your voice.
7. Turn recognition off and save to stop matching. Delete erases the profile.

These changes tune preprocessing and matching, not neural model weights. No user
recordings or labeled training set were available for model fine-tuning or for
measuring live recognition accuracy. Test on your microphone after enrollment.
The current checks estimate useful audio from frame energy; they are not a
speaker separation or liveness system. Phone carrier calls are not identified.

Validation includes 136 automated tests and generated-speech model/encryption
checks. Generated identical-clip matching establishes packaging, not recognition
accuracy on real people. See [the original enrollment guide](RELEASE-0.10.10.md).
