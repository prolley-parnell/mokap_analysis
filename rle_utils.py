
import os
import pickle
import numpy as np
import pycocotools.mask as pmask
from tqdm import tqdm
from pathlib import Path


def open_silhouette_video(npz_file, memmap=True):
    """
        Open an npz file without loading everything in memory
    """
    if not memmap:
        data = np.load(npz_file, mmap_mode=None)['obj_0']
    else:
        data = np.load(npz_file, mmap_mode='r')['obj_0']
    img_indices, vector_indices = data.T
    return img_indices, vector_indices


def read_silhouette_frame(img_indices, vector_indices, image_shape, frame_index):
    """
        Read one single frame from an open npz container
    """
    silhouette = np.zeros((image_shape[1], image_shape[0]), dtype=np.uint8)
    silhouette.ravel()[vector_indices[img_indices == frame_index]] = 255
    return silhouette


def silhouettes_generator(img_indices, vector_indices, image_shape):
    """
        Generator for loading silhouettes one by one from an open npz container
    """
    frames = np.unique(img_indices)
    for frame in frames:
        silhouette = np.zeros((image_shape[1], image_shape[0]), dtype=np.uint8)
        silhouette.ravel()[vector_indices[img_indices == frame]] = 255
        yield silhouette


def sizeof_fmt(num, suffix="B"):
    """
        Pretty-print a size in bytes
        from: https://stackoverflow.com/a/1094933
    """
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:
            return f"{num:3.1f} {unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f} Yi{suffix}"


def convert_to_RLE(npz_file_path, image_shape=(1440, 1080), delete_source=False, skip_existing=True):
    """
        Convert a npz file containing a whole video worth of masks into a much smaller Run Length Encoding file
    """
    npz_file = Path(npz_file_path)
    rle_file = npz_file.parent / f"{npz_file.stem}.rle"

    if skip_existing and rle_file.exists():
        print(f"\nFile {rle_file.name} exists, skipping...")

    else:
        print(f"\nConverting {npz_file.name}...")
        img_indices, vector_indices = open_silhouette_video(npz_file)

        siz_before = os.path.getsize(npz_file)

        nb_frames = len(np.unique(img_indices))
        g = silhouettes_generator(img_indices, vector_indices, image_shape)

        all_silhouettes = []
        for silhouette in tqdm(g, total=nb_frames):
            all_silhouettes.append(pmask.encode(np.asfortranarray(silhouette)))

        with open(rle_file, 'wb') as f:
            pickle.dump(all_silhouettes, f, protocol=pickle.HIGHEST_PROTOCOL)

        siz_after = os.path.getsize(rle_file)

        print(f"  {sizeof_fmt(siz_before)} -> {sizeof_fmt(siz_after)}")

        if delete_source:
            os.remove(npz_file)


class VideoMask:
    """
        Small class to read a RLE file
    """
    def __init__(self, rle_file_path):
        self.rle_file = Path(rle_file_path)
        with open(self.rle_file, 'rb') as f:
            self.content = pickle.load(f)

    def __getitem__(self, item):
        return pmask.decode(self.content[item]) * 255


##

if __name__ == "__main__":
    
    folder = 'C:/Users/flolm/Desktop/segmentation'
    name_fmt = '240905-1616_cam*_*_session28'

    for npz_file in Path(folder).glob(f'{name_fmt}.npz'):
        convert_to_RLE(npz_file, image_shape=(1440, 1080), delete_source=False)

