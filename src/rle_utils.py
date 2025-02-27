import pickle
import numpy as np
import pycocotools.mask as pmask
from pathlib import Path
from collections import deque


class VideoMask:
    """
        Class to read a RLE file and access frames with optional temporal filtering
    """

    def __init__(self, silhouette_file_path, cache_processed=False):
        self.file_path = Path(silhouette_file_path)

        self.o = 0 # Assumes that the object of interest is always at idx 0 but this is not true for multiple objects in frame

        if 'rle' in self.file_path.suffix:

            with open(self.file_path, 'rb') as f:
                self._content = pickle.load(f)

                if 'dimensions' in self._content.keys() and 'objects' in self._content.keys():
                    print('Detected new style .rle')
                    self._version = 3
                    self._dims = self._content['dimensions']
                    self._nb_objects = len(self._content['objects'])
                else:
                    print('Detected old style .rle')
                    self._content = [self._content]
                    self._version = 2
                    self._dims = next(iter(self._content[self.o].values()))['size']
                    self._nb_objects = len(self._content)

        elif 'npz' in self.file_path.suffix:

            with np.load(self.file_path, mmap_mode='r', allow_pickle=True) as d:
                if 'mask_dict' in d.keys():
                    print('Detected new style .npz')
                    self._version = 1
                    self._content = d['mask_dict'].item()
                    first_entry = next(iter(self._content[self.o].values()))
                    self._dims = [first_entry[0]['size'][1], len(first_entry)]
                    self._nb_objects = len(self._content)
                else:
                    raise NotImplemented("Old style .npz detected, not yet implemented (sorry)")

        self._cache_processed = cache_processed

        # Initialize caches
        self._raw_cache = {}  # Cache for raw frames
        self._processed_cache = {}  # Cache for processed frames (in RLE format)
        self._window_size = None
        self._window_half = None
        self._window_frames = deque(maxlen=200)
        self._window_indices = deque(maxlen=200)

    @property
    def frames_numbers(self):
        if self._version == 3:
            return list(self._content['objects'][self.o].keys())
        elif self._version == 2:
            return [int(k) for k in self._content[self.o].keys()]
        elif self._version == 1:
            return list(self._content[self.o].keys())
        else:
            raise ValueError("Old style .npz not supported yet")

    def __len__(self):
        return len(self.frames_numbers)

    def frame(self, frame_number, time_window=1):
        """
        Returns the frame corresponding to the given frame number
        If window_size > 1, performs temporal median filtering with the specified window size.
        If cache_processed is True, caches the processed frames in RLE format for memory efficiency.
        """

        # If no filtering, return the raw frame directly
        if not bool(time_window) or time_window <= 1:
            return self._get_raw_frame(frame_number)

        else:
            # Check if we already have the filtered frame in the cache
            cache_key = (frame_number, time_window)
            if cache_key in self._processed_cache:
                rle = self._processed_cache[cache_key]
                return pmask.decode(rle) * 255

            else:
                # If not, filter it and cache it
                processed_frame = self._get_processed_frame(frame_number, time_window)
                if self._cache_processed:
                    rle = pmask.encode(np.asfortranarray(processed_frame // 255))
                    self._processed_cache[cache_key] = rle

                return processed_frame

    def iframe(self, idx, time_window=1):
        frame_number = self.frames_numbers[idx]
        return self.frame(frame_number, time_window=time_window)

    def _get_raw_frame(self, frame_number):
        if frame_number in self._raw_cache:
            return self._raw_cache[frame_number]
        else:
            if self._version == 3:
                frame_data = pmask.decode({'size': self._dims, 'counts': self._content['objects'][self.o][frame_number]}) * 255
            elif self._version == 2:
                frame_data = pmask.decode(self._content[self.o][frame_number]) * 255
            elif self._version == 1:
                frame_data = pmask.decode(self._content[self.o][frame_number]).squeeze() * 255
            else:
                raise ValueError("Old style .npz not supported yet")

            self._raw_cache[frame_number] = frame_data
            return frame_data

    def _get_processed_frame(self, frame_number, window_size):
        index = self.frames_numbers.index(frame_number)

        # Check if window_size has changed
        if self._window_size != window_size:
            self._window_size = window_size
            self._window_half = window_size // 2
            self._window_frames.clear()
            self._window_indices.clear()

        # Determine window start and end indices
        start_index = max(0, index - self._window_half)
        end_index = min(len(self), index + self._window_half + 1)
        required_indices = range(start_index, end_index)

        # Update window frames cache
        # Remove frames no longer in window
        while self._window_indices and self._window_indices[0] < start_index:
            old_idx = self._window_indices.popleft()
            old_frame_number = self.frames_numbers[old_idx]
            self._window_frames.popleft()
            # Optionally remove from frame cache
            if old_frame_number in self._raw_cache:
                del self._raw_cache[old_frame_number]

        # Add new frames to window
        for idx in required_indices:
            if idx not in self._window_indices:
                frame_number_in_window = self.frames_numbers[idx]
                frame_mask = self._get_raw_frame(frame_number_in_window).astype(np.uint8) // 255
                self._window_frames.append(frame_mask)
                self._window_indices.append(idx)

        # Stack frames in window
        frames_stack = np.stack(self._window_frames, axis=0)
        # Compute median
        median_frame = np.median(frames_stack, axis=0)
        # Threshold
        final_mask = (median_frame > 0.5).astype(np.uint8) * 255

        return final_mask

    def clear_caches(self):
        """
        Clears all internal caches
        """
        self._raw_cache.clear()
        self._processed_cache.clear()
        self._window_frames.clear()
        self._window_indices.clear()
        self._window_size = None
        self._window_half = None

