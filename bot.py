import os
import json
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
from moviepy.editor import VideoFileClip
import yt_dlp
import re
import threading
import queue
import logging


CONFIG_FILE = 'config.json'
LOG_FILE = 'app.log'

# Set up logging
logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def log_and_print(message, level=logging.INFO):
    logging.log(level, message)
    print(message)

# Function to sanitize folder names, we remove the underscore as python doesn't like them
def sanitize_folder_name(name):
    return re.sub(r'[\/:*?"<>|]', '', name).replace(' ', '_')

# we only take the actual link and remove anything after the & symbol as it is not needed
def clean_youtube_url(url):
    if '&' in url:
        url = url.split('&', 1)[0]
    return url

# download the vid in high format
def download_youtube_video(url, output_path='video.mp4'):
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best*',  # This will pick the best available formats
        'outtmpl': output_path,
        'quiet': True
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        log_and_print(f"Video downloaded successfully: {output_path}")
    except yt_dlp.DownloadError as e:
        log_and_print(f"Error downloading video: {str(e)}", logging.ERROR)
        raise

# split the video into defined lengths and save them in the parts folder
def split_video(input_path, segment_length=60, output_folder='parts', update_progress=None):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    video = VideoFileClip(input_path)
    video_duration = int(video.duration)
    total_parts = (video_duration + segment_length - 1) // segment_length

    for i, start in enumerate(range(0, video_duration, segment_length)):
        end = min(start + segment_length, video_duration)
        segment = video.subclip(start, end)
        
        output_path = os.path.join(output_folder, f"part{i + 1}.mp4")
        segment.write_videofile(output_path, codec="libx264")
        log_and_print(f"Segment {i + 1} saved: {output_path}")

        if update_progress:
            progress_percent = int((i + 1) / total_parts * 100)
            update_progress(progress_percent)

# process the video and add some error handling to it as well 
def process_video():
    progress_bar["value"] = 0
    progress_bar["maximum"] = 100
    status_label.config(text="")
    processing_image_label.config(image=processing_image)
    root.update_idletasks()

    youtube_url = url_entry.get()
    base_output_folder = folder_entry.get()
    part_length = part_length_entry.get()

    youtube_url = clean_youtube_url(youtube_url)

    try:
        part_length = int(part_length)
        if part_length <= 0:
            raise ValueError("Part length must be positive.")
    except ValueError as ve:
        status_label.config(text=f"Error: {str(ve)}")
        root.after(3000, clear_status)
        log_and_print(f"Validation error: {str(ve)}", logging.ERROR)
        return

    if not youtube_url:
        status_label.config(text="Error: Please enter a YouTube URL.")
        root.after(3000, clear_status)
        log_and_print("No YouTube URL provided.", logging.ERROR)
        return

    if not base_output_folder:
        status_label.config(text="Error: Please select an output folder.")
        root.after(3000, clear_status)
        log_and_print("No output folder selected.", logging.ERROR)
        return

    def update_progress(percent):
        progress_queue.put(percent)

    def background_task():
        try:
            ydl_opts = {
                'format': 'bestvideo+bestaudio/best*',
                'quiet': True,
                'extract_flat': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(youtube_url, download=False)
                video_title = info_dict.get('title', 'video')
                sanitized_title = sanitize_folder_name(video_title)
            
            video_folder = os.path.join(base_output_folder, sanitized_title)
            if not os.path.exists(video_folder):
                os.makedirs(video_folder)
            
            status_label.config(text="Downloading video...")
            root.update_idletasks()
            video_path = os.path.join(video_folder, 'video.mp4')
            try:
                download_youtube_video(youtube_url, output_path=video_path)
            except yt_dlp.DownloadError:
                status_label.config(text="Try again, something went wrong with the video download.")
                root.after(3000, clear_status)
                log_and_print("Video download failed.", logging.ERROR)
                return
            
            parts_folder = os.path.join(video_folder, 'parts')
            status_label.config(text="Splitting video into parts...")
            root.update_idletasks()
            
            split_video(video_path, segment_length=part_length, output_folder=parts_folder, update_progress=update_progress)
            
            status_label.config(text="Video processed and saved successfully!")
            processing_image_label.config(image='')
            root.after(3000, clear_status)
            log_and_print("Video processing completed successfully.")
        except Exception as e:
            status_label.config(text="Try again, something went wrong.")
            processing_image_label.config(image='')
            root.after(3000, clear_status)
            log_and_print(f"Error during video processing: {str(e)}", logging.ERROR)

    thread = threading.Thread(target=background_task)
    thread.start()

    def update_status():
        try:
            percent = progress_queue.get_nowait()
            progress_bar["value"] = percent
            status_label.config(text=f"Splitting video: {percent}% complete")
            root.after(100, update_status)
        except queue.Empty:
            root.after(100, update_status)

    progress_queue = queue.Queue()
    update_status()

# claer status function
def clear_status():
    status_label.config(text="")

# save configuration to a file
def save_config():
    config = {
        'output_folder': folder_entry.get(),
        'part_length': part_length_entry.get()
    }
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)
    log_and_print("Configuration saved.")

# load from the config file
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            folder_entry.delete(0, tk.END)
            folder_entry.insert(0, config.get('output_folder', ''))
            part_length_entry.delete(0, tk.END)
            part_length_entry.insert(0, config.get('part_length', '60'))
    log_and_print("Configuration loaded.")

# add the credits and help functions
def show_credits():
    messagebox.showinfo("Credits", "This app was made by DIVINUS from Nulled.")
    log_and_print("Credits shown.")

def show_help():
    messagebox.showinfo("Help", "Easily split YouTube videos into parts, to upload to TikTok, YT Shorts, etc. Need help? DM me on Nulled.")
    log_and_print("Help shown.")

def exit_program():
    root.quit()
    log_and_print("Program exited.")

# GUI setup
root = tk.Tk()
root.title("[DIVINUS] Auto YT Splitter")
root.geometry("600x350") 
root.resizable(False, False)

# darker colors for the GUI
background_color = "#2E2E2E"
foreground_color = "#E0E0E0"
button_color = "#000000"
button_hover_color = "#444444"
status_color = "#FF6F6F"
button_text_color = "#000000"

root.configure(bg=background_color)

logo_path = 'your/path/to/icon.ico'
if os.path.exists(logo_path):
    root.iconbitmap(logo_path)

processing_image_path = 'your/path/to/icon.png'
if os.path.exists(processing_image_path):
    processing_image = tk.PhotoImage(file=processing_image_path)
else:
    processing_image = tk.PhotoImage()

menu_bar = tk.Menu(root, bg=background_color, fg=foreground_color)
root.config(menu=menu_bar)

file_menu = tk.Menu(menu_bar, tearoff=0, bg=background_color, fg=foreground_color)
menu_bar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Exit", command=exit_program)

credits_menu = tk.Menu(menu_bar, tearoff=0, bg=background_color, fg=foreground_color)
menu_bar.add_cascade(label="Credits", menu=credits_menu)
credits_menu.add_command(label="Show Credits", command=show_credits)

help_menu = tk.Menu(menu_bar, tearoff=0, bg=background_color, fg=foreground_color)
menu_bar.add_cascade(label="Help", menu=help_menu)
help_menu.add_command(label="Show Help", command=show_help)

main_frame = ttk.Frame(root, padding="20", style="TFrame")
main_frame.grid(row=0, column=0, sticky="nsew")

title_label = ttk.Label(main_frame, text="Split your YT video into parts", font=("Arial", 16, "bold"), foreground=foreground_color, background=background_color)
title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))

url_label = ttk.Label(main_frame, text="YouTube URL:", foreground=foreground_color, background=background_color)
url_label.grid(row=1, column=0, sticky='w', pady=5, padx=5)
url_entry = ttk.Entry(main_frame, width=50)
url_entry.grid(row=1, column=1, columnspan=2, pady=5, padx=5, sticky='ew')

folder_label = ttk.Label(main_frame, text="Output Folder:", foreground=foreground_color, background=background_color)
folder_label.grid(row=2, column=0, sticky='w', pady=5, padx=5)
folder_entry = ttk.Entry(main_frame, width=50)
folder_entry.grid(row=2, column=1, pady=5, padx=5, sticky='ew')
select_button = ttk.Button(main_frame, text="Select Folder", command=lambda: select_folder())
select_button.grid(row=2, column=2, padx=5, pady=5)

part_length_label = ttk.Label(main_frame, text="Part Length (seconds):", foreground=foreground_color, background=background_color)
part_length_label.grid(row=3, column=0, sticky='w', pady=5, padx=5)
part_length_entry = ttk.Entry(main_frame, width=20)
part_length_entry.insert(0, "60")
part_length_entry.grid(row=3, column=1, pady=5, padx=5, sticky='ew')

process_button = ttk.Button(main_frame, text="Download & Split Video", command=lambda: [process_video(), save_config()])
process_button.grid(row=4, column=0, columnspan=3, pady=(10, 10))
process_button.configure(style="TButton")

status_label = ttk.Label(main_frame, text="", foreground=status_color, background=background_color)
status_label.grid(row=5, column=0, columnspan=3, pady=10)

progress_bar = ttk.Progressbar(main_frame, orient="horizontal", mode="determinate")
progress_bar.grid(row=6, column=0, columnspan=3, pady=10, sticky="ew")

processing_image_label = ttk.Label(main_frame, image=processing_image, background=background_color)
processing_image_label.grid(row=7, column=0, columnspan=3, pady=10)

def select_folder():
    folder_path = filedialog.askdirectory()
    folder_entry.delete(0, tk.END)
    folder_entry.insert(0, folder_path)
    log_and_print(f"Selected folder: {folder_path}")

style = ttk.Style()
style.configure("TFrame", background=background_color)
style.configure("TButton",
                background=button_color,
                foreground=button_text_color,
                relief="flat",
                padding=6)
style.map("TButton",
          background=[('active', button_hover_color)],
          foreground=[('active', button_text_color)])

load_config()

root.mainloop()