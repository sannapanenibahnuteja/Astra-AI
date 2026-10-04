# Bob 0.10.1

Fixes the reported “close YouTube → several windows → close all those” failure. Window choices are held per conversation for three minutes, with exact window identity checks at execution. Group closure displays all selected windows and asks once; changed or missing windows stop execution. These are whole-window closures, including all browser tabs in each window.

Phone status reads now have timeouts, retry backoff, one active poll, lower hidden-page polling, and foreground/network-return reconnection. New links replace the remembered token; revoked tokens stop polling. PC commands are never retried automatically. Pairing persistence failure stops the gateway instead of leaving an unsaved connection active.

Validation: 95 Python tests passed; `node scripts/verify-mobile-client.cjs` verifies offline recovery, hidden-page intervals, duplicate poll prevention, remembered-token replacement and revocation. Production frontend build passed. No personal browser windows were closed during testing. Real iPhone networking and microphone use were not tested here.

iPhone locked-screen custom wake-word support is not included. The phone guide describes a Siri shortcut to open Bob, with unlocking required; carrier reminder calls remain separate.
