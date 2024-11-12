import os
from pickletools import uint8

import matplotlib.pyplot as plt
import cv2
import numpy as np
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--video_dir", type=str, required=True, help="Relative path of folder with video frames")
parser.add_argument("--experiment_name", type=str, required=True, help="Video name also referred to as experiment name")
parser.add_argument("--source_folder", type=str, required=True, help="Output file folder path, assumes the name of the file is the 'experiment_name.npy'")


def scan_frames(video_dir):
    # scan all the JPEG frame names in this directory
    frame_names = [
        p for p in os.listdir(video_dir)
        if os.path.splitext(p)[-1] in [".jpg", ".jpeg", ".JPG", ".JPEG"]
    ]
    frame_names.sort(key=lambda p: int(os.path.splitext(p)[0]))
    return frame_names

def drawMask(frame_idx, frame_name):
    global frame, mask_file
    frame = cv2.imread(os.path.join(args.video_dir, frame_name))
    if frame_idx in mask_file:
        print("We have a mask")
        for out_obj_id, out_mask in mask_file[frame_idx].items():
            h, w = out_mask.shape[-2:]
            color = np.array([50., 100., 0.], dtype=np.uint8)
            mask_image = out_mask.reshape(h, w, 1) * color.reshape(1, 1, -1)
            frame_masked = cv2.addWeighted(frame, 0.5, mask_image, 0.5, 0)
            frame_masked[mask_image == 0] = frame[mask_image == 0]
            frame = frame_masked


def getFrame(frame_nr):
    global frame_idx, frame_names
    frame_idx = frame_nr
    drawMask(frame_idx, frame_names[frame_idx])

def main(args):
    global frame_names, mask_file, frame
    mask_file = np.load(f"{args.source_folder}/{args.experiment_name}.npy", allow_pickle=True)[()] #Allows the dict to be extracted from npy

    frame_names = scan_frames(args.video_dir)
    frame_slider_max = len(frame_names)
    frame_idx = 0
    frame = cv2.imread(os.path.join(args.video_dir, frame_names[frame_idx]))

    cv2.namedWindow(f"User Input: {args.experiment_name}", cv2.WINDOW_AUTOSIZE)
    cv2.createTrackbar("Frame", f"User Input: {args.experiment_name}", frame_idx, frame_slider_max, getFrame)

    # main loop
    while 1:
        # show frame, break the loop if no frame is found

        cv2.imshow(f"User Input: {args.experiment_name}", frame)

        # stop playback when q is pressed
        k = cv2.waitKey(20) & 0xFF
        if k == ord('q'):
            break

    # release resources
    cv2.destroyAllWindows()
    cv2.waitKey(1)


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)