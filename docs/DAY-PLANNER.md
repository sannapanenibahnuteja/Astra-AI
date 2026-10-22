# Bob 0.11.5: free local day planner

No Google Cloud account, API key or billing setup is needed. Use your installed Ollama model. Local AI cannot see current traffic or measure routes: its drive times are rough guesses. Verify destinations and current conditions in Maps before travel.

## Set up
1. Start Ollama. In Bob Settings choose an installed model and a local URL, normally http://127.0.0.1:11434. Save settings.
2. Open Day planner. Enter date, start time, starting address and arrival buffer. UTC offset defaults to +05:30; change it if traveling elsewhere.
3. Add up to eight stops: name, full address, optional fixed appointment time and time spent there. Blank appointment times are flexible. Enter manual drive minutes if known.
4. Reorder stops with arrows or Order appointments by time. Save day plan.
5. Choose Plan with local AI for rough estimates, or Use manual travel estimates for your own drive times. Manual planning needs no running model. No background model calls happen.
6. Read leave/arrival/start/finish times and conflicts. Appointments are not moved. The plan can cross midnight; Bob flags this.
7. Open each Google Maps route to check the destination and actual traffic for free. Maps only receives addresses when you open a route link. You can put its drive estimate into manual drive minutes, save, then recalculate manually.
8. Read day briefing speaks the first departure and conflicts. Delete saved day removes that schedule.

## Voice examples
- “Tomorrow I’ll start at 8 AM from [full starting address], with a 15-minute arrival buffer.”
- “Add a dentist appointment tomorrow at 10 AM at [full clinic address]. I’ll stay for 30 minutes.”
- “Show my day tomorrow.”
- “Plan my day tomorrow.”
- “When should I leave?” (uses the selected day)
- “Open the driving route to stop two for tomorrow.”

Natural start/add requests use the existing local LLM tools. Bob asks for missing addresses, times or durations. Route/show/plan follow-ups have direct fast matching. No external calendar is changed. AI output is validated; if a leg is unknown or invalid, Bob asks you to use checked manual times instead of silently substituting them.

## Quick test
Create tomorrow with start 08:00, buffer 15, one appointment at 09:00, duration 60 and manual drive 30. Save and calculate manually: leave 08:15, arrive 08:45, start 09:00, finish 10:00. Change day start to 08:50, save and calculate: a 35-minute buffer-inclusive conflict should appear. Add a flexible stop and reorder it. Try local AI using real public addresses: estimates must display Local AI estimate and no live traffic. Stop Ollama: manual planning still works; AI planning must report failure rather than pretend success. Delete the test day afterward.

## Limits and costs
This feature uses one loopback-only Ollama request per AI calculation, with a 60-second timeout, a small structured response and no model thinking. Cold model loading and PC hardware affect speed. Remote/cloud Ollama URLs are refused for this planner. Maps links do not require an API key (https://developers.google.com/maps/documentation/urls/get-started). No automatic GPS, shortest-route optimization, calendar sync or live traffic polling is implemented.

This change removes routing API billing. Existing optional Twilio carrier calls and Azure voices retain their provider costs if you enable them; they are not used by day planning. Choose local voices to avoid optional speech-provider costs.

## Current location

Enable Allow current PC location for trip planning, allow Windows Location services and desktop app access under Privacy & security → Location, and click Refresh current location. Select Start from my current location, add a destination name with its city/area or an address, and save. Every calculation and first-route request refreshes the Windows position. Later legs start from the preceding stop. Locations stay transient; the saved origin is a current-location marker. No background tracking. Accuracy depends on Windows location services; unavailable/stale fixes ask for a refresh or manually entered place. Opening Maps shares route locations with Google; local Ollama estimates remain on this PC and are not live traffic.
