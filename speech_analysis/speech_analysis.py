#!/usr/bin/env python

import argparse
import parselmouth
from datetime import datetime
from moviepy.video.io.VideoFileClip import VideoFileClip
import cv2
import pandas as pd
import os
from parselmouth.praat import call
from itertools import zip_longest


class SpeechAnalysis:
    """Class to extract speech analysis metrics from a video and save to a CSV file."""
    
    def __init__(self, video_path, csv_path):
        self.video_path = video_path
        self.csv_path = csv_path
        self.audio = self.to_audio()
        self.sound = parselmouth.Sound(self.audio)
        self.frames = self.frames_from_video()


    def frames_from_video(self):
        video = cv2.VideoCapture(self.video_path)
        fps = video.get(cv2.CAP_PROP_FPS)
        success, image = video.read()
        count = 0
        frames = []
        while success:
            count += 1
            frames.append(count / fps)
            success, frame = video.read()
        frame_timestamp = {}
        index = 1
        while index <= len(frames):
            if index == 1:
                frame_timestamp[index] = [0, frames[index - 1]]
            else:
                frame_timestamp[index] = [frames[index - 2], frames[index - 1]]
            index += 1
        return frame_timestamp

    def to_audio(self):
        video = VideoFileClip(self.video_path, verbose=False)
        audio_file = video.audio
        current_date = datetime.now().timestamp()
        path = "/tmp/" + str(current_date) + ".wav"   
        audio_file.write_audiofile(path, logger=None)
        return path

    def pitches(self):
        sound = self.sound
        pitch = sound.to_pitch()
        pitch_values = pitch.selected_array['frequency']
        times = pitch.xs()
        time_pitch = {}
        for i in range(len(times)):
            if pitch_values[i] > 0:
                time_pitch[times[i]] = pitch_values[i]
        frame_video = self.frames
        frame_pitches = {}
        for f_v in frame_video:
            arr_pitches = []
            for pair in time_pitch:
                if frame_video[f_v][0] <= pair <= frame_video[f_v][1]:
                    arr_pitches.append(time_pitch[pair])
            if len(arr_pitches) == 0:
                frame_pitches[f_v] = [frame_video[f_v], 'NA']
            else:
                frame_pitches[f_v] = [frame_video[f_v], arr_pitches]
        arr_frames = []
        timestamps = []
        pitches = []
        for pair in frame_pitches:
            if len(frame_pitches[pair][1]) > 0:
                arr_frames.append(pair)
                timestamps.append(frame_pitches[pair][0])
                pitches.append(frame_pitches[pair][1])
        reformat_timestamps_start = []
        reformat_timestamps_end = []
        for i in range(len(timestamps)):
            reformat_timestamps_start.append(str(round(timestamps[i][0], 4)))
            reformat_timestamps_end.append(str(round(timestamps[i][1], 4)))
        reformat_pitches = []
        for i in range(len(pitches)):
            arr_measurements = pitches[i]
            string = ''
            for j in range(len(arr_measurements)):
                if pitches[i] != 'NA':
                    string += (str(round(arr_measurements[j], 4)) + ",")
                else:
                    string += 'NA'
            reformat_pitches.append(string[:len(string) - 2].strip())
        return [arr_frames, reformat_timestamps_start, reformat_timestamps_end, reformat_pitches]

    def intensities(self):
        global frame_intensity
        frames = self.frames
        sound = self.sound
        intensity = sound.to_intensity()
        times = intensity.xs()
        intensity_values = intensity.values[0]
        time_intensity = {}
        for i in range(len(times)):
            time_intensity[times[i]] = intensity_values[i]
        frame_intensity = {}
        for pair in frames:
            arr = []
            for pair2 in time_intensity:
                if frames[pair][0] <= pair2 <= frames[pair][1]:
                    arr.append(time_intensity[pair2])
            if len(arr) > 0:
                frame_intensity[pair] = arr
        arr_same_frames = []
        frame_pitch = self.pitches()
        for i in range(len(frame_pitch[0])):
            if frame_pitch[0][i] in frame_intensity.keys():
                arr_same_frames.append(frame_pitch[0][i])
        arr_intensities = []
        for pair in frame_intensity:
            string = ' '
            if pair in arr_same_frames:
                for i in range(len(frame_intensity[pair])):
                    string += str(round(frame_intensity[pair][i], 4)) + ","
                arr_intensities.append(string[:len(string) - 2].strip())
        return arr_intensities

    def harmonicities(self):
        sound = self.sound
        pitch = sound.to_pitch()
        min_pitch = call(pitch, "Get minimum", 0, 0, "hertz", "Parabolic")
        harmonicity = call(sound, 'To Harmonicity (cc)', 0.01, min_pitch, 0.1, 1.0)
        frames_from_harmonicity = call(harmonicity, "Get number of frames")
        count = 1
        arr_times = []
        arr_values = []
        while count <= frames_from_harmonicity:
            time_for_frame = call(harmonicity, "Get time from frame number", count)
            value_for_time = call(harmonicity, "Get value at time", time_for_frame, "Linear")
            arr_times.append(time_for_frame)
            arr_values.append(value_for_time)
            count += 1
        frames = self.frames
        arr_harmonicities = []
        for pair in frames:
            values_for_frame = ' '
            for i in range(len(arr_times)):
                if frames[pair][0] <= arr_times[i] <= frames[pair][1]:
                    values_for_frame += str(round(arr_values[i], 4)) + ","
            arr_harmonicities.append(values_for_frame[:len(values_for_frame) - 1].strip())
        return arr_harmonicities

    def formants(self):
        sound = self.sound
        frames = self.frames
        formants = call(sound, "To Formant (burg)", 0.0, 5, 5500, 0.025, 50)
        frames_formants = call(formants, 'Get number of frames')
        count = 1
        arr_times = []
        while count <= frames_formants:
            arr_times.append(call(formants, 'Get time from frame number', count))
            count += 1
        time_formants = {}
        arr_formant1 = []
        arr_formant2 = []
        arr_formant3 = []
        arr_formant4 = []
        for i in range(len(arr_times)):
            arr_formant1.append(call(formants, 'Get value at time', 1, arr_times[i], 'Hertz', 'Linear'))
            arr_formant2.append(call(formants, 'Get value at time', 2, arr_times[i], 'Hertz', 'Linear'))
            arr_formant3.append(call(formants, 'Get value at time', 3, arr_times[i], 'Hertz', 'Linear'))
            arr_formant4.append(call(formants, 'Get value at time', 4, arr_times[i], 'Hertz', 'Linear'))
        for i in range(len(arr_times)):
            time_formants[arr_times[i]] = [arr_formant1[i], arr_formant2[i], arr_formant3[i], arr_formant4[i]]
        frame_all_formants = {}
        for pair in frames:
            arr = []
            for pair2 in time_formants:
                if frames[pair][0] <= pair2 <= frames[pair][1]:
                    arr.append(time_formants[pair2])
                frame_all_formants[pair] = arr
        frame_order_formants = {}
        for pair in frame_all_formants:
            count = 0
            arr1 = []
            arr2 = []
            arr3 = []
            arr4 = []
            # we know that we have four formants
            while count < len(frame_all_formants[pair]):
                arr1.append(str(round(frame_all_formants[pair][count][0], 4)))
                arr2.append(str(round(frame_all_formants[pair][count][1], 4)))
                arr3.append(str(round(frame_all_formants[pair][count][2], 4)))
                arr4.append(str(round(frame_all_formants[pair][count][3], 4)))
                count += 1
            frame_order_formants[pair] = [arr1, arr2, arr3, arr4]
        index = 0
        # because we have 4 formants
        arr_formants = []
        while index < 4:
            arr_first = []
            for pair in frame_order_formants:
                arr = frame_order_formants[pair][index]
                string = ''
                for i in range(len(arr)):
                    string += arr[i] + ","
                arr_first.append(string[:len(string) - 2].strip())
            arr_formants.append(arr_first)
            index += 1
        return arr_formants

    def file_process(self):
        pitches_by_frames = self.pitches()
        intensity_by_frames = self.intensities()
        harmonicity_by_frames = self.harmonicities()
        formants_by_frames = self.formants()

        # Find the maximum length among all lists
        # Sometimes (I don't know why) the lists are not the same length (intensity is shorter than the others by 1)
        # TODO: Find out why this happens
        all_lists = [pitches_by_frames[0], pitches_by_frames[1], pitches_by_frames[2], pitches_by_frames[3], intensity_by_frames, harmonicity_by_frames, formants_by_frames[0], formants_by_frames[1], formants_by_frames[2], formants_by_frames[3]]
        max_length = max(len(lst) for lst in all_lists)

        # Pad shorter lists with empty strings
        for lst in all_lists:
            while len(lst) < max_length:
                lst.append('NA')
       
        # Now you can create your DataFrame
        data_frame = pd.DataFrame({
            'Frame': pitches_by_frames[0],
            'Start': pitches_by_frames[1],
            'End': pitches_by_frames[2],
            'Pitches': pitches_by_frames[3],
            'Intensities': intensity_by_frames,
            'Harmonicities': harmonicity_by_frames,
            'Formant 1': formants_by_frames[0],
            'Formant 2': formants_by_frames[1],
            'Formant 3': formants_by_frames[2],
            'Formant 4': formants_by_frames[3]
        })
        data_frame.to_csv(index=False, path_or_buf=self.csv_path)

    def __del__(self):
        try:
            os.remove(self.audio)
        except Exception as e:
            print(f"Failed to delete {self.audio}. Reason: {e}")



def main():
    """Main function to process the video and extract speech analysis metrics."""
    parser = argparse.ArgumentParser(description="Extract speech analysis metrics from a video and save to a CSV file.")
    
    # Define command-line arguments
    parser.add_argument('-v', '--video', type=str, required=True, help="Path to the input video file.")
    parser.add_argument('-c', '--csv', type=str, required=True, help="Path to the output CSV file.")
    
    args = parser.parse_args()

    try:
        analysis = SpeechAnalysis(args.video, args.csv)
        analysis.file_process()
        print(f"Analysis completed. Results saved to {args.csv}")
    except Exception as e:
        print(f"An error occurred while processing the video: {e}")
    

if __name__ == "__main__":
    main()