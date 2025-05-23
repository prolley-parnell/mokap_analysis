import os

import matplotlib.pyplot as plt
import cv2
from numpy import asarray, savetxt
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--video_dir", type=str, required=True, help="Relative path of folder with video frames")
parser.add_argument("--video_name", type=str, required=True, help="Video name")

# `video_dir` a directory of JPEG frames with filenames like `<frame_index>.jpg`
#video_dir = "/Users/persie/Movies/Mokap_Video/mokap/240905-1616/240905-1616_cam0_avocado_session19"
#video_name = "240905-1616_cam0_avocado_session19"

def scan_frames(video_dir):
    # scan all the JPEG frame names in this directory
    frame_names = [
        p for p in os.listdir(video_dir)
        if os.path.splitext(p)[-1] in [".jpg", ".jpeg", ".JPG", ".JPEG"]
    ]
    frame_names.sort(key=lambda p: int(os.path.splitext(p)[0]))
    return frame_names

def drawAnnotations(annotation, frame_idx):
    global frame, frame_names

    frame = cv2.imread(os.path.join(args.video_dir, frame_names[frame_idx]))

    if annotation:
        cropped_list = list(filter(lambda tuple: tuple[4] == frame_idx, annotation))

        for point in cropped_list:
            if point[3] == 1:
                cv2.circle(frame, (point[1:3]), 25, (0, 255, 0), -1)
            else:
                cv2.circle(frame, (point[1:3]), 25, (0, 0, 255), -1)

            cv2.putText(frame, str(point[0]), (point[1]-7, point[2]+7), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, thickness=2, color=(0, 0, 0))


def getFrame(frame_nr):
    global annotation_list, frame_idx
    frame_idx = frame_nr
    drawAnnotations(annotation_list, frame_idx)

def mouseCB(event, x, y, flags, param):
    global annotation_list, frame_idx, object_id
    update = 1;
    if event == cv2.EVENT_MBUTTONDOWN and annotation_list:
        # Remove the last point
        annotation_list.remove(annotation_list[-1])
        print(annotation_list)
    elif event == cv2.EVENT_LBUTTONDOWN:
        # Add a positive point
        annotation_list.append([object_id, x, y, 1, frame_idx])
    elif event == cv2.EVENT_RBUTTONDOWN:
        # Add a negative point
        annotation_list.append([object_id, x, y, 0, frame_idx])
    else:
        update = 0

    if update == 1:
        drawAnnotations(annotation_list, frame_idx)


def main(args):
    global annotation_list, frame_idx, frame, frame_names, object_id
    frame_names = scan_frames(args.video_dir)
    frame_slider_max = len(frame_names)
    frame_idx = 0
    object_id = 0
    frame = cv2.imread(os.path.join(args.video_dir, frame_names[frame_idx]))

    annotation_list = []


    cv2.namedWindow(f"User Input: {args.video_name}", cv2.WINDOW_GUI_NORMAL )
    cv2.createTrackbar("Frame", f"User Input: {args.video_name}", frame_idx, frame_slider_max, getFrame)
    cv2.setMouseCallback(f"User Input: {args.video_name}", mouseCB)

    # main loop
    while 1:
        # show frame, break the loop if no frame is found

        cv2.imshow(f"User Input: {args.video_name}", frame)

        # stop playback when q is pressed
        k = cv2.waitKey(20) & 0xFF
        if k == ord('q'):
            break
        if k == ord('w'):
            object_id = object_id+1
        if k == ord('s'):
            object_id = max(object_id-1, 0)

    # release resources
    cv2.destroyAllWindows()
    cv2.waitKey(1)

    output = asarray(annotation_list)
    savetxt(f"{args.video_dir}/{args.video_name}.csv", output ,delimiter=",", header="Object_ID,X,Y,Score,Frame")

if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
    print(f"Printed to ''{args.video_dir}/{args.video_name}.csv''")