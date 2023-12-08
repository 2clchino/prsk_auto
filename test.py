import time
import pyautogui
import cv2
import numpy as np
import multiprocessing
import pygame
import time
import asyncio

h_offset = 1380
h_watch = 780
w_watch = 1545
w_offset = 1200
fifo = []
delay = 3
frame_cnt = 0
buff = []

def save_image(image, filename):
    # OpenCVを使用して画像を保存
    cv2.imwrite(filename, image)

def capture_screen(region):
    screenshot = pyautogui.screenshot(region=region)
    return cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGR2RGB)

def find_tap_notes(rgb):
    color_lower = (205, 205, 205)  # Adjust the lower bound accordingly
    color_upper = (255, 255, 255)

    # Define the color range to match (in HSV format)
    lower_bound = np.array(color_lower, dtype=np.uint8)
    upper_bound = np.array(color_upper, dtype=np.uint8)

    # 色の範囲に基づいてマスクを作成
    mask = cv2.inRange(rgb, lower_bound, upper_bound)

    # マスクを使用して元画像から対象のピクセルを抽出
    coordinates = np.column_stack(np.where(mask > 0))

    if len(coordinates) > 0:
        return find_mean_val(coordinates)
    else:
        return None
    
def find_mean_val(coordinates):
    global buff
    center = np.mean(coordinates, axis=0).astype(int)
    center[0] = center[0]
    center[1] = (center[1] * 2) + w_offset
    return center

async def click_at_position(position):
    await asyncio.sleep(0.01*(80-position[0]))
    pyautogui.mouseDown(position[1], 1380)

def macr():
    pygame.init()
    desired_fps = 60
    clock = pygame.time.Clock()
    while True:
        # Find the target location
        # target_location = find_target_location(target_image_path, confidence=0.8)
        rgb = capture_screen((w_watch, h_watch, 700, 80))
        fifo.append(find_tap_notes(rgb))
        if len(fifo) > delay:
            fifo.pop(0)
        # Click at the target location
        if fifo[0] is not None and len(fifo[0]) > 0:
            asyncio.create_task(click_at_position(fifo[0]))
            print("Clicking at:", fifo[0])
            # pyautogui.press("a")
        else:
            print(f'Target image not found.')
            pyautogui.mouseUp()
        # Add a sleep or adjust the loop frequency as needed
        clock.tick(desired_fps)

if __name__ == "__main__":
    # バックグラウンドプロセスとして実行
    background_process = multiprocessing.Process(target=macr)
    background_process.start()

    try:
        # メインプロセスで他の処理を実行
        while True:
            # ここに他の処理を追加
            pass

    except KeyboardInterrupt:
        # Ctrl+Cで中断された場合、バックグラウンドプロセスを終了
        background_process.terminate()
        background_process.join()