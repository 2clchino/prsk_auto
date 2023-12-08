

from PIL import Image, ImageTk, ImageDraw
import pygetwindow as gw
import tkinter as tk
import ctypes

def draw_overlay(window, position, size):
    # Create a blank image with an alpha channel for transparency
    img = Image.new("RGBA", (window.winfo_width(), window.winfo_height()), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Draw the rectangle on the image with a semi-transparent color
    draw.rectangle([position[0], position[1], position[0] + size[0], position[1] + size[1]],
                   outline=(255, 0, 0, 128), width=2)

    # Convert the PIL image to a Tkinter-compatible format
    img_tk = ImageTk.PhotoImage(img)

    # Create a Tkinter canvas and display the image
    canvas = tk.Canvas(window, width=window.winfo_width(), height=window.winfo_height(), bd=0, highlightthickness=0)
    canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
    canvas.pack(fill=tk.BOTH, expand=tk.YES)

# Windows APIの定数
GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x00080000
LWA_ALPHA = 0x00000002

# ウィンドウの透明度を設定する関数
def set_window_opacity(hwnd, opacity):
    # ウィンドウのスタイルを取得
    extended_style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    # WS_EX_LAYEREDスタイルを追加
    extended_style |= WS_EX_LAYERED
    ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, extended_style)
    # ウィンドウの透明度を設定
    ctypes.windll.user32.SetLayeredWindowAttributes(hwnd, 0, int(opacity * 255), LWA_ALPHA)

def main():
    active_window = gw.getActiveWindow()

    frame_position = (100, 100)
    frame_size = (200, 200)
    if active_window:
        root = tk.Tk()
        root.attributes("-alpha", 0.3)
        set_window_opacity(root.winfo_id(), 0.1)
        label = tk.Label(root, text="こんにちは、透明なウィンドウ！", font=("Helvetica", 16))
        label.pack(padx=20, pady=20)
        root.geometry(f"{active_window.width}x{active_window.height}+{active_window.left}+{active_window.top}")
        draw_overlay(root, frame_position, frame_size)
        root.mainloop()

    else:
        print("アクティブなウィンドウが見つかりませんでした。")