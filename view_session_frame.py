import os
from pickletools import uint8

import matplotlib.pyplot as plt
import cv2
import numpy as np
import argparse
from pathlib import Path

from dataclasses import dataclass

@dataclass
class args:
    video_dir = Path('/Users/persie/Desktop/Dataset_for_upload/Video')
    date = '240905'
    prefix = '240905-1616'
    session = 29
    frame_idx = 1807





def main(args):
    FRAME_IDX = args.frame_idx
    DATE = args.date
    PREFIX = args.prefix
    SESSION = args.session

    PREFIX_VIDEO_FOLDER = args.video_dir / DATE / PREFIX

    #Find videos for this session
    video_paths = sorted(PREFIX_VIDEO_FOLDER.glob(f'*session{SESSION}.mp4'))

    for video in video_paths:

        cap = cv2.VideoCapture(video)
        cap.set(cv2.CAP_PROP_POS_FRAMES, FRAME_IDX)
        ret, frame = cap.read()
        cap.release()

        if ret:
            cv2.imshow(f'{video.stem} - frame: {FRAME_IDX}', frame)
        else:
            return


    hold = 1
    # main loop
    while hold:

        # stop playback when q is pressed
        k = cv2.waitKey(5) & 0xFF
        if k == ord('q'):
            #writer.release()
            hold = 0
            break


    # release resources
    cv2.destroyAllWindows()
    cv2.waitKey(1)


if __name__ == "__main__":
    main(args)