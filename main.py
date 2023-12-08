import pyautogui
import cv2
import numpy as np
import multiprocessing
import asyncio
import time
from ctypes import windll

h_offset = 1380
h_watch = 780
w_watch = 1545
w_offset = 1200
height = 120
frame_cnt = 0
hold = False

def save_image(image, filename):
    cv2.imwrite(filename, image)

def capture_screen(region):
    screenshot = pyautogui.screenshot(region=region)
    return cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGR2RGB)

def find_color_range(rgb, color_lower = (205, 205, 205), color_upper = (255, 255, 255)):
    lower_bound = np.array(color_lower, dtype=np.uint8)
    upper_bound = np.array(color_upper, dtype=np.uint8)
    mask = cv2.inRange(rgb, lower_bound, upper_bound)
    coordinates = np.column_stack(np.where(mask > 0))
    if len(coordinates) > 0:
        return find_mean_val(coordinates)
    else:
        return None
    
def find_mean_val(coordinates):
    center = np.mean(coordinates, axis=0).astype(int)
    center[0] = center[0]
    center[1] = (center[1] * 2) + w_offset
    return center

async def click_at_position(position):
    await asyncio.sleep(0.14 + 0.001*(height-position[0]))
    pyautogui.mouseUp()
    pyautogui.mouseDown(position[1], 1380)

async def mouse_up(delay):
    await asyncio.sleep(delay)

async def task():
    global hold
    target_interval = 1/15
    while True:
        start_time = time.time()
        rgb = capture_screen((w_watch, h_watch, 700, height))
        pos = find_color_range(rgb, (240, 240, 240), (255, 255, 255))
        if pos is not None and len(pos) > 0:
            asyncio.create_task(click_at_position(pos))
            print("Clicking at:", pos)
            hold = True
        elapsed_time = time.time() - start_time
        sleep_time = max(0, target_interval - elapsed_time)
        await asyncio.sleep(sleep_time)

def mainloop():
    asyncio.run(task())

if __name__ == "__main__":
    windll.winmm.timeBeginPeriod(1)
    background_process = multiprocessing.Process(target=mainloop)
    background_process.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        background_process.terminate()
        background_process.join()
        windll.winmm.timeEndPeriod(1)
        print("Interruped")