import unittest
from unittest.mock import patch, Mock
import cv2
from speech_analysis import SpeechAnalysis

class TestSpeechAnalysis(unittest.TestCase):

    @patch('cv2.VideoCapture')
    def test_frames_from_video(self, mock_video_capture):
        # Mocking the video capture and related methods
        mock_video = Mock()
        mock_video.get.return_value = 29.97  # Assuming 29.97 FPS
        mock_video.read.side_effect = [
            (True, 'frame1'), (True, 'frame2'), (True, 'frame3'),
            (True, 'frame4'), (True, 'frame5'), (True, 'frame6'),
            (True, 'frame7'), (True, 'frame8'), (True, 'frame9'),
            (True, 'frame10'), (False, None)
        ]
        mock_video_capture.return_value = mock_video

        # Expected frame timestamps for 30 frames at 29.7 FPS
        expected_frame_timestamp = {
            1: [0, 0.033366700033366704], 
            2: [0.033366700033366704, 0.06673340006673341], 
            3: [0.06673340006673341, 0.1001001001001001], 
            4: [0.1001001001001001, 0.13346680013346682], 
            5: [0.13346680013346682, 0.16683350016683351], 
            6: [0.16683350016683351, 0.2002002002002002], 
            7: [0.2002002002002002, 0.2335669002335669], 
            8: [0.2335669002335669, 0.26693360026693363], 
            9: [0.26693360026693363, 0.3003003003003003], 
            10: [0.3003003003003003, 0.33366700033366703]
        }

        # Testing
        sa = SpeechAnalysis('dummy_video_path', 'dummy_csv_path')
        result = sa.frames_from_video()
        self.assertEqual(result, expected_frame_timestamp)

if __name__ == '__main__':
    unittest.main()
