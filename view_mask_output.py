import os
import cv2
import numpy as np
import argparse
from src.rle_utils import VideoMask
from pathlib import Path


def scan_frames(video_dir):
    # scan all the JPEG frame names in this directory
    frame_path = sorted(video_dir.glob('*.jpg'))
    frame_path.sort(key=lambda p: int(p.stem))
    return frame_path

# def enc_dict_to_mask(dictionary_obj, obj_id, frame_idx):
#     #Use pycoco decode to extract the mask from the dict
#     mask = pmask.decode(dictionary_obj[obj_id][frame_idx])
#     return np.squeeze(mask) #Remove empty dimension if it exists

def drawMask(frame_idx, frame_name):
    global frame, video_mask
    frame = cv2.imread(os.path.join(args.video_dir, frame_name))
    # m = enc_dict_to_mask(loaded_mask_dict, obj_id=0, frame_idx=frame_idx)
    m = video_mask.frame(frame_idx)

    if m.any():
        color = np.array([50., 100., 0.], dtype=np.uint8)
        segment_mask = np.zeros_like(frame, dtype=np.uint8)
        segment_mask[m > 0] = 255 * color.reshape(1, 1, -1)
        frame_masked = cv2.addWeighted(frame, 0.5, segment_mask, 0.5, 0)
        frame_masked[segment_mask == 0] = frame[segment_mask == 0]
        frame = frame_masked


def getFrame(frame_nr):
    global frame_idx, frame_names
    frame_idx = frame_nr
    drawMask(frame_idx, frame_names[frame_idx])


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="View an rle file as a binary mask over a set of video frames", exit_on_error=False)
    parser.add_argument("video_dir", type=str, help="Relative path of folder with video frames")
    parser.add_argument("folder", type=str, help="Path to the datetime folder")
    parser.add_argument("prefix", type=str, help="Datetime prefix (example: '240905-1616')")
    parser.add_argument("session", type=int, help="Session number")
    parser.add_argument("camera", type=int, help="Camera number")

    try:
        args = parser.parse_args()
    except:
        from dataclasses import dataclass

        @dataclass
        class args:
            video_dir = Path('/home/persie/Videos/mokap')
            folder = Path('/home/persie/Code/3d_ant_data')
            prefix = '240905-1616'
            session = 6
            camera = 1

    PREFIX = args.prefix
    FOLDER = Path(args.folder) / PREFIX
    SESSION = args.session
    CAM_ID = args.camera

    INPUT_FOLDER = FOLDER / 'inputs'
    PREFIX_VIDEO_FOLDER = args.video_dir / PREFIX
    FRAME_FOLDER = Path(sorted(PREFIX_VIDEO_FOLDER.glob(f'{PREFIX}_cam{CAM_ID}*session{SESSION}'))[0]) #Should only collect one folder

    rle_file = sorted((INPUT_FOLDER / 'segmentation').glob(f'{PREFIX}_cam{CAM_ID}*session{SESSION}.rle')) #Should only collect one file

    video_mask = VideoMask(rle_file[0])
    # frame_names = sorted(video_mask.frames_numbers)
    frame_names = scan_frames(FRAME_FOLDER)
    frame_slider_max = len(frame_names)
    frame_idx = int(np.argmin(frame_names))
    frame = cv2.imread(FRAME_FOLDER / frame_names[frame_idx])

    cv2.namedWindow(f"User Input: {PREFIX} Session: {SESSION}, Camera: {CAM_ID}", cv2.WINDOW_KEEPRATIO)
    cv2.createTrackbar("Frame", f"User Input: {PREFIX} Session: {SESSION}, Camera: {CAM_ID}", frame_idx, frame_slider_max, getFrame)

    # main loop
    while 1:
        # show frame, break the loop if no frame is found

        cv2.imshow(f"User Input: {PREFIX} Session: {SESSION}, Camera: {CAM_ID}", frame)

        # stop playback when q is pressed
        k = cv2.waitKey(20) & 0xFF
        if k == ord('q'):
            break

    # release resources
    cv2.destroyAllWindows()
    cv2.waitKey(1)
