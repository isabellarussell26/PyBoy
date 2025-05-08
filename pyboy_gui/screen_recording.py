import time
import os
import numpy as np
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
from moviepy.audio.AudioClip import AudioArrayClip


class VideoCreator:
    """
    A class for creating video files from emulator frames and audio data.
    """

    def __init__(self, emulator, output_path=None, sample_rate=48000, codec="libx264", audio_codec="aac"):
        """
        Initializes the VideoCreator object.

        Args:
            emulator: The emulator object.
            output_path (str, optional): The full path to save the video file.
                                         If None, it defaults to a path in the
                                         'screen_recordings' folder. Defaults to None.
            sample_rate (int, optional): The audio sample rate. Defaults to 48000.
            codec (str, optional): The video codec to use. Defaults to "libx264".
            audio_codec (str, optional): The audio codec to use. Defaults to "aac".
        """
        self.sample_rate = sample_rate
        self.codec = codec
        self.audio_codec = audio_codec
        self.video_frames = []
        self.audio_frames = []
        self.mp4_file_path = output_path
        self.emulator = emulator
        if output_path is None:
            self.scrn_rec_fold = os.path.join(os.path.dirname(__file__), '..', 'pyboy_gui', 'screen_recordings')
            self.cleaned_title = self.sanitize_game_title(emulator.gamerom)
            self.timestamp = time.strftime("%m.%d.%Y_%H.%M.%S")
            self.file_name = f"{self.cleaned_title}_{self.timestamp}"
            self.mp4_file_path = os.path.join(self.scrn_rec_fold, self.file_name + ".mp4")

    def get_video_frame(self, emulator):
        """
        Gets a video frame from the emulator's screen image.
        """
        frame_np = np.array(emulator.screen.image)
        if frame_np.shape != (144, 160, 4):
            frame_np = np.resize(frame_np, (144, 160, 4))
        return frame_np

    def sanitize_game_title(self, gamerom):
        """
        Sanitizes the game title from the ROM path for use as a filename.
        """
        file_name = os.path.splitext(os.path.basename(gamerom))[0]
        cleaned_file_name = file_name.replace(" - ", "_").replace(" ", "_")
        return cleaned_file_name

    def merge_av(self):
        """
        Merges audio and video frames and writes them to a video file.
        """
        # Ensure video frames are in the correct format (RGB)
        self.video_frames = [frame[:, :, :3] for frame in self.video_frames]
        video = ImageSequenceClip(self.video_frames, fps=60)

        audio = np.vstack(self.audio_frames)  # Stack frames into a large array

        # Convert audio to float if it isn't already
        if audio.dtype != np.float32 and audio.dtype != np.float64:
            audio = audio.astype(np.float32)

        # Normalize audio to the range [-0.5, 0.5] to prevent clipping
        max_val = np.max(np.abs(audio))
        if max_val > 1:
            audio = audio / max_val * 0.5

        audio_clip = AudioArrayClip(audio, fps=self.sample_rate)
        video = video.with_audio(audio_clip)
        video.write_videofile(self.mp4_file_path, codec=self.codec, audio_codec=self.audio_codec)


