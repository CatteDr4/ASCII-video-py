#! /bin/python3

from alive_progress import alive_bar
import re
from moviepy.editor import VideoFileClip
import os
import numpy as np
import argparse
from PIL import Image
import json
import shutil

###### GETTING FRAMES ######


def GetVideoFrames(video, frames):

    vidobj = VideoFileClip(video)
    # make video object

    filename, _ = os.path.splitext(video)
    filename += "-video_maker-temp"
    if not os.path.isdir(filename):
        os.mkdir(filename)
    # make folder

    if frames is None:
        saving_fps = vidobj.fps
    else:
        saving_fps = min(vidobj.fps, frames)
    # get fps

    step = 1 / vidobj.fps if saving_fps == 0 else 1 / saving_fps
    # set frame time

    frame_count = 0

    frame_list = np.arange(0, vidobj.duration, step)

    with alive_bar(len(frame_list), title="Separating Frames", stats = False) as bar:
        # animated bar
        for current_duration in frame_list:
            vidobj.save_frame(os.path.join(filename, f"{frame_count}.jpg"), current_duration)
            # saving frames to files
            frame_count += 1
            bar()

    return filename, vidobj.filename, saving_fps

###### GETTING ASCII ######


def FetchFrames(path, w, mode, scale):
    image_paths = []
    image_frames = []
    # func lists

    for root, dirs, files in os.walk(path):
        for file in files:
            image_paths.append(os.path.join(root,file))
            # getting file paths
    with alive_bar(len(image_paths), title="Transforming frames", stats = False) as bar:
        for name in sorted(image_paths, key=natural_key):
            if mode == "RGB":
                image_frames.append(TransformImageRGB(Image.open(name), w))
            else:
                image_frames.append(TransformImageBW(Image.open(name), w, scale))
            bar()
            """ CHANGE TO ONLY FETCH 500 AT ONCE """
        # transforming images into PIL objects

    return image_frames


def TransformImageRGB(img, width):
    x, y = img.size
    wpercent = (width/float(x))
    hsize = int((float(y)*float(wpercent)))
    # changing resolution

    img = img.resize((width, hsize))
    img = img.convert("RGB", dither = None)
    # resizing image

    pixels = []
    ascii_image = ""

    for i in range(hsize):
        row = []
        for j in range(width):
            r, g, b = img.getpixel((j, i))
            row.append(str(f"\x1b[38;2;{r};{g};{b}m█\x1b[0m"))
        pixels.append(row)
    # transforming frame to ascii

    for row in pixels:
        for i in row:
            ascii_image += i
        ascii_image += "\n"
    # outputting to string

    return ascii_image


def TransformImageBW(image, cols, scale):
    gray_scale = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'. "
    image = image.convert("L")
    W, H = image.size
    w = W / cols
    h = w / scale
    rows = int(H / h)
    pixels = []
    ascii_image = ""

    for j in range(rows):
        y1 = int(j * h)
        y2 = int((j + 1) * h)

        if j == rows - 1:
            y2 = H

        pixels.append("")

        for i in range(cols):

            x1 = int(i * w)
            x2 = int((i + 1) * w)

            if i == cols - 1:
                x2 = W

            img = image.crop((x1, y1, x2, y2))
            avg = int(getAverageL(img))
            val = gray_scale[int((avg * 69) / 255)]
            pixels[j] += val

    for row in pixels:
        for i in row:
            ascii_image += i
        ascii_image += '\n'

    return ascii_image

###### SAVING TO FILE ######


def SaveToFile(frames, outfile, videoName, fps, color):
    obj = {
        "name": videoName.split("/")[-1],
        "FPS": fps,
        "isColored": color,
        "frames": frames
    }
    with open(outfile, "w") if not os.path.isdir(outfile) else open(outfile, "x") as f:
        f.write(json.dumps(obj))
    # saving (obviously)

    print("Saved at " + os.getcwd() + '/' + outfile)

###### OTHER ######


def natural_key(string_):
    """See https://blog.codinghorror.com/sorting-for-humans-natural-sort-order/"""
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]


def getAverageL(image):
    im = np.array(image)
    w,h = im.shape
    return np.average(im.reshape(w*h))

###### MAIN ######


def main():
    parser = argparse.ArgumentParser(description="Video-to-ASCII converter")
    parser.add_argument('--file', '-f', dest='Video', required=True, help="Path to file")
    parser.add_argument('--fps', dest="frames_per_second", required=False, help="Frames per second to save")
    parser.add_argument('--out', dest="outfile", required=False, help="Name for the output file")
    parser.add_argument('--width', '-w', dest='width', required=False, help="Image width")
    parser.add_argument('--play-after', '-pa', dest="play_after", required=False, help="Use this if you immediately want to play the video", action='store_true')
    parser.add_argument('--mode', "-mode", dest="mode", required=False, help="Defaults to RGB, other mode is BW")
    parser.add_argument('--scale', '-s', dest='scale', required=False, help="Scale ratio, used with BW mode")

    args = parser.parse_args()

    Video = args.Video

    fps = None
    if args.frames_per_second:
        fps = int(args.frames_per_second)

    width = 40
    if args.width:
        width = int(args.width)

    outfile = "out.json"
    if args.outfile:
        outfile = args.outfile+".json"

    scale = 0.43
    if args.scale:
        scale = float(args.scale)

    mode = "RGB"
    if args.mode:
        mode = args.mode.upper()

    if mode not in ["RGB", "BW"]:
        print("Unspecified color mode selected, defaulting to Grayscale")
        mode = "BW"

    path, vidname, frames_per_second = GetVideoFrames(Video, fps)
    print(f"Frames separated (at {path})")
    frames = FetchFrames(path, width, mode, scale)
    print("Frames transformed")
    print("Saving...")
    SaveToFile(frames, outfile, vidname, frames_per_second, True if mode == "RGB" else False)
    print("Cleaning up...")
    shutil.rmtree(path)

    if args.play_after:
        """TODO: IMPLEMENT PLAYER (player is implemented cba to do anything about it tho)"""


if __name__ == '__main__':
    main()
