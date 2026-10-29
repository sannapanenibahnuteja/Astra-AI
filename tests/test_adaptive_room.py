import unittest
import numpy as np
from desktop.audio_pipeline import AdaptiveRoom
from desktop.duplex_audio import TurnDetector, BLOCK


class AdaptiveRoomTests(unittest.TestCase):
    def test_sustained_quiet_relaxes_but_one_frame_does_not(self):
        room=AdaptiveRoom()
        for _ in range(199):self.assertEqual(room.observe(.0001),'balanced')
        self.assertEqual(room.observe(.0001),'quiet')

    def test_quiet_preference_still_requires_room_evidence(self):
        room=AdaptiveRoom(prefer_quiet=True)
        for _ in range(99):self.assertEqual(room.observe(.0001),'balanced')
        self.assertEqual(room.observe(.0001),'quiet')

    def test_noise_restores_caution_without_flapping_on_one_tap(self):
        room=AdaptiveRoom()
        for _ in range(200):room.observe(.0001)
        self.assertEqual(room.observe(.005),'quiet')
        for _ in range(7):room.observe(.005)
        self.assertEqual(room.mode,'balanced')
        for _ in range(199):room.observe(.0001)
        self.assertEqual(room.mode,'balanced')

    def test_playback_and_speech_never_establish_quiet(self):
        for flags in ({'speech':True},{'playing':True}):
            room=AdaptiveRoom()
            for _ in range(500):room.observe(.00001,**flags)
            self.assertEqual(room.mode,'balanced')

    def test_invalid_or_clipping_resets_quiet(self):
        for rms,clipped in ((float('nan'),False),(.0001,True)):
            room=AdaptiveRoom()
            for _ in range(200):room.observe(.0001)
            self.assertEqual(room.observe(rms,clipped=clipped),'balanced')

    def test_quiet_capture_accepts_soft_speech_still_needs_duration(self):
        frame=np.full(BLOCK,.00019,np.float32)
        quiet=TurnDetector();quiet.room_mode='quiet'
        balanced=TurnDetector()
        for _ in range(8):
            quiet.feed(frame,.99)
            balanced.feed(frame,.99)
        self.assertTrue(quiet.started)
        self.assertFalse(balanced.started)
        tap=TurnDetector();tap.room_mode='quiet'
        tap.feed(frame,.99)
        for _ in range(20):tap.feed(np.zeros(BLOCK,np.float32),0)
        self.assertFalse(tap.started)
