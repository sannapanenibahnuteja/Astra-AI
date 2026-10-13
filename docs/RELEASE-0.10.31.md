# Bob 0.10.31

The running 0.10.30 app's saved timed routine was disabled. A daily time alone does not activate a paused routine. The scheduler was not reporting an error.

- Prominent warnings now explain that a paused routine cannot trigger at its daily time, both in its card and when editing it.
- Each scheduled routine has a direct Enable schedule / Pause schedule button. These actions preserve its time and steps; they no longer require opening the editor.
- Intentional pauses remain respected; this update does not automatically activate disabled routines.

Test: open Automations, find the scheduled routine and click Enable schedule. Verify the card says enabled. To test from scratch, set a PC local time one minute ahead and save with Enabled checked. Keep Bob running; allow ten seconds after the due time. The existing scheduler runs during passive listening and queues active-task delays. Pause the routine and verify the warning; it must not run while paused. Enabling a recently due routine may execute it immediately within the existing 30-minute catch-up window.
