import time
import pyautogui
import cv2
import numpy as np
import multiprocessing
import pygame
import time

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
    global frame_cnt, buff
    if (len(buff) > 0):
        coordinates = buff[0]
        buff = []
        return find_mean_val(coordinates, True)

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
        return find_mean_val(coordinates, False)
    else:
        return None
    
def find_mean_val(coordinates, isBuff):
    global buff
    center = np.mean(coordinates, axis=0).astype(int)
    if (center[0] < 60 and not isBuff):
        buff.append(coordinates)
        return None
    center[0] = center[0]
    center[1] = (center[1] * 2) + w_offset
    return center

def click_at_position(position):
    pyautogui.mouseDown(position[1], 1380)

def macr():
    pygame.init()
    desired_fps = 60
    clock = pygame.time.Clock()
    cnt = 0
    while True:
        # Find the target location
        # target_location = find_target_location(target_image_path, confidence=0.8)
        rgb = capture_screen((w_watch, h_watch, 700, 80))
        fifo.append(find_tap_notes(rgb))
        if len(fifo) > delay:
            fifo.pop(0)
        # Click at the target location
        if fifo[0] is not None and len(fifo[0]) > 0:
            click_at_position(fifo[0])
            print("Clicking at:", fifo[0])
            # pyautogui.press("a")
        else:
            print(f'Target image not found. {cnt}')
            pyautogui.mouseUp()
            cnt += 1
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