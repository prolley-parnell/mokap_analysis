import os
from pickletools import uint8

import matplotlib.pyplot as plt
import cv2
import numpy as np
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--video_file", type=str, required=True, help="Relative path of folder with video as mp4")
parser.add_argument("--experiment_name", type=str, required=True, help="Video name also referred to as experiment name")
parser.add_argument("--source_folder", type=str, required=True, help="Output file folder path, assumes the name of the file is the 'experiment_name.npz'")


def scan_frames(video_dir):
    # scan all the JPEG frame names in this directory
    frame_names = [
        p for p in os.listdir(video_dir)
        if os.path.splitext(p)[-1] in [".jpg", ".jpeg", ".JPG", ".JPEG"]
    ]
    frame_names.sort(key=lambda p: int(os.path.splitext(p)[0]))
    return frame_names


def mask_to_array(sparse_mask_list, n_frames, image_shape):
    empty_mask = np.zeros((*image_shape, int(n_frames)), dtype=np.uint8)
    for point in sparse_mask_list:
        r,c = np.unravel_index(point[1], image_shape, order='C')
        empty_mask[r,c, point[0]] = 255
    return empty_mask

# def mask_to_array(sparse_mask_list, n_frames, image_shape):
#     empty_mask = np.zeros((*image_shape, int(n_frames)), dtype=np.uint8)
#     uni = np.unique(sparse_mask_list)
#     for mask_idx in uni:
#         pix = sparse_mask_list[sparse_mask_list[:,0] == mask_idx, 1]
#         np.put(empty_mask[:,:, mask_idx], pix, 255)
#     return empty_mask


def main(args):
    colour = np.array([50., 100., 0.], dtype=np.uint8)
    loaded_mask_file = np.load(f"{args.source_folder}/{args.experiment_name}.npz")['obj_0'] #Allows the dict to be extracted from npy

    cap = cv2.VideoCapture(args.video_file)
    ret, frame = cap.read()

    if not ret:
        return

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    writer = cv2.VideoWriter(f'masked_{args.experiment_name}.avi', cv2.VideoWriter_fourcc(*'mp4v'), 60, (width, height))
    #Turn the video masks into an array
    mask_array = mask_to_array(loaded_mask_file, cap.get(cv2.CAP_PROP_FRAME_COUNT), (height, width))
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)


    # main loop
    while ret:
        # show frame, break the loop if no frame is found
        ret, frame = cap.read()
        frame_idx = cap.get(cv2.CAP_PROP_POS_FRAMES)
        frame_mask = np.dstack((mask_array[:,:,int(frame_idx)], mask_array[:,:,int(frame_idx)],mask_array[:,:,int(frame_idx)]))*colour
        combined_frame = cv2.addWeighted(frame, 0.5, frame_mask, 0.5, 0)
        combined_frame[mask_array[:,:,int(frame_idx)]==0] = frame[mask_array[:,:,int(frame_idx)]==0]
        cv2.imshow('frame', combined_frame)
        writer.write(combined_frame)

        # stop playback when q is pressed
        k = cv2.waitKey(5) & 0xFF
        if k == ord('q'):
            #writer.release()
            cap.release()
            break


    # release resources
    cv2.destroyAllWindows()
    cv2.waitKey(1)


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)