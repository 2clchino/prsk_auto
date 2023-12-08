import pyautogui
import cv2
import numpy as np
import multiprocessing
import asyncio

h_offset = 1380
h_watch = 780
w_watch = 1545
w_offset = 1200
frame_cnt = 0

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
    await asyncio.sleep(0.48 + 0.001*(120-position[0]))
    pyautogui.mouseDown(position[1], 1380)

async def mouse_up(delay):
    await asyncio.sleep(0)
    pyautogui.mouseUp()

async def task():
    while True:
        rgb = capture_screen((w_watch, h_watch, 700, 120))
        pos = find_color_range(rgb, (205, 205, 205), (255, 255, 255))
        if pos is not None and len(pos) > 0:
            asyncio.create_task(click_at_position(pos))
            print("Clicking at:", pos)
        else:
            print(f'Target image not found.')
            pyautogui.mouseUp()
        await asyncio.sleep(1/60)
    

def mainloop():
    asyncio.run(task())

if __name__ == "__main__":
    background_process = multiprocessing.Process(target=mainloop)
    background_process.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        background_process.terminate()
        background_process.join()