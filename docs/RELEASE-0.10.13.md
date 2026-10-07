# Bob 0.10.13 - Tab context and interruption filtering

## Changes from 0.10.12

- “Close all YouTube” and “close all YouTube tabs” select matching Edge tabs across windows, including windows on different monitors.
- After Bob reports several matching tabs, “close all”, “close all those”, “close both” and “close them” reuse that selection. “Close the first one” and “close the second one” select from it.
- Approval shows the selected count and titles. Tab identities are frozen before approval; tabs opened afterward are excluded. Closures are verified by identity, including duplicate titles. Focus failures and partial completion are reported honestly.
- Tab references belong to the current conversation and expire after five minutes. Ambiguous references ask for clarification rather than looking for a window named “all”. Recently opened browser windows support “close it”.
- Interruption detection rejects isolated clicks, broadband hiss and low-level residual noise, and requires sustained speech during playback. Longer pre-roll retains the beginning of the request. Echo cancellation remains enabled.
- Saved facts and voice identity context are retained when long prompts are trimmed.

## Install

1. Quit the old Bob using its tray menu.
2. Extract the new ZIP, then run **Bob.exe**. Existing settings and memory remain in the same local data folder.
3. Check **0.10.13** at the bottom of the sidebar. Keep Ollama running.

## Test the fixes

1. In Edge, open two YouTube tabs and one unrelated tab. You can put the YouTube tabs in different windows/monitors.
2. Say **“Close all YouTube tabs.”** Check Bob's selected titles, then say **“Yes.”** Both selected YouTube tabs should close; the unrelated tab should stay open.
3. Reopen two YouTube tabs. Say **“Close YouTube.”** If Bob lists several matches, say **“Close all those.”**, then **“Yes.”** You can also choose **“Close the second one.”**
4. Open another matching tab after Bob asks for approval. It should stay open when you approve the original selection.
5. Say **“Open YouTube.”**, then **“Close it.”** Review and approve the selected tab.
6. Start a voice conversation. Ask **“Explain how a computer works.”** Try a keyboard click or brief rustle while Bob speaks; it should not immediately stop him. Then speak clearly: **“Actually, open calculator.”** Bob should stop speaking, capture the complete request, and execute after you finish.

Actual recognition depends on your microphone and room. Television speech and nearby people can still be detected as speech; this filter is not speaker authentication. Use the optional voice matching setting or headphones where helpful. Closing tabs still requires approval because it can discard work.

## Verification

150 automated tests passed, including the complete ambiguity-to-approval flow, duplicate tab titles, unrelated tab protection, cancellation, focus failure and partial completion. The frontend production build passed. Generated speech through echo cancellation reached a reliable Calculator action plan at normal and quiet volume; Bob-only echo triggered no interruption. These checks do not replace testing your microphone and Edge windows using the steps above.
