import os
import subprocess
import threading
import customtkinter as ctk
from tkinter import messagebox, ttk
from yt_dlp import YoutubeDL
import json
import sys

# Setup
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

app = ctk.CTk()
app.iconbitmap('icon.ico')
app.title("Enhanced Video Downloader")
app.geometry("650x550")
app.resizable(False, False)

# Modern warning frame for missing cookies.txt
cookies_warning_frame = ctk.CTkFrame(app, fg_color="#2d1a1a", corner_radius=10)
cookies_main_label = ctk.CTkLabel(
    cookies_warning_frame,
    text="⚠️  Some sites (like Instagram) require a cookies.txt file for downloads!",
    font=("Arial", 15, "bold"),
    text_color="#ff4d4d"
)
cookies_main_label.pack(pady=(8, 0), padx=10, anchor="w")
cookies_instr_label = ctk.CTkLabel(
    cookies_warning_frame,
    text="Please export your browser cookies and place 'cookies.txt' in this folder.\n"
         "How to get it: Use a Chrome extension like 'Get cookies.txt' to export your cookies while logged in.",
    font=("Arial", 12),
    text_color="#ffb3b3",
    wraplength=600,
    justify="left"
)
cookies_instr_label.pack(pady=(2, 8), padx=10, anchor="w")

def check_cookies_file():
    if not os.path.exists("cookies.txt"):
        cookies_warning_frame.pack(pady=(10, 0), padx=10, fill="x")
    else:
        cookies_warning_frame.pack_forget()

check_cookies_file()

# Global Variables
downloaded_file_path = ""
stop_download_event = threading.Event()
video_formats = []
current_video_info = None

# Detect system Downloads folder
if sys.platform == "win32":
    from pathlib import Path
    downloads_folder = str(Path.home() / "Downloads")
else:
    downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")

# Functions
def fetch_formats():
    """Fetch available formats for the given URL"""
    video_url = url_entry.get().strip()
    if not video_url or video_url == placeholder_text:
        messagebox.showerror("Error", "Please paste a video URL.")
        return

    status_label.configure(text="🔍 Fetching available formats...", text_color="yellow")
    format_dropdown.configure(values=["Loading..."])
    format_dropdown.set("Loading...")
    
    def fetch_thread():
        global video_formats, current_video_info
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'cookiefile': 'cookies.txt' if os.path.exists('cookies.txt') else None,
            }
            
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                current_video_info = info
                
                # Get title
                title = info.get('title', 'Unknown Title')
                title_label_info.configure(text=f"📹 {title[:60]}{'...' if len(title) > 60 else ''}")
                
                # Process formats
                formats = info.get('formats', [])
                video_formats = []
                format_options = []
                
                # Best combined format
                if 'requested_formats' not in info:
                    best_format = {
                        'format_id': 'best',
                        'display': '🏆 Best Quality (Auto)',
                        'ext': info.get('ext', 'mp4'),
                        'filesize': info.get('filesize') or info.get('filesize_approx', 0),
                        'note': 'Best available quality'
                    }
                    video_formats.append(best_format)
                    format_options.append(best_format['display'])
                
                # Video + Audio combined formats
                video_audio_formats = []
                video_only_formats = []
                audio_only_formats = []
                
                for fmt in formats:
                    if not fmt.get('format_id'):
                        continue
                    
                    vcodec = fmt.get('vcodec', 'none')
                    acodec = fmt.get('acodec', 'none')
                    ext = fmt.get('ext', 'unknown')
                    height = fmt.get('height')
                    fps = fmt.get('fps')
                    filesize = fmt.get('filesize') or fmt.get('filesize_approx', 0)
                    
                    # Format size display
                    size_str = ""
                    if filesize:
                        if filesize > 1024*1024*1024:  # GB
                            size_str = f" ({filesize/(1024*1024*1024):.1f}GB)"
                        else:  # MB
                            size_str = f" ({filesize/(1024*1024):.1f}MB)"
                    
                    # Combined video+audio
                    if vcodec != 'none' and acodec != 'none' and height:
                        fps_str = f"{fps}fps " if fps else ""
                        display = f"📺 {height}p {fps_str}{ext.upper()}{size_str}"
                        video_audio_formats.append({
                            'format_id': fmt['format_id'],
                            'display': display,
                            'ext': ext,
                            'height': height,
                            'filesize': filesize,
                            'note': fmt.get('format_note', ''),
                            'fps': fps or 0
                        })
                    
                    # Video only
                    elif vcodec != 'none' and acodec == 'none' and height:
                        fps_str = f"{fps}fps " if fps else ""
                        display = f"🎬 {height}p {fps_str}{ext.upper()} (Video Only){size_str}"
                        video_only_formats.append({
                            'format_id': fmt['format_id'],
                            'display': display,
                            'ext': ext,
                            'height': height,
                            'filesize': filesize,
                            'note': fmt.get('format_note', ''),
                            'fps': fps or 0
                        })
                    
                    # Audio only
                    elif vcodec == 'none' and acodec != 'none':
                        abr = fmt.get('abr', 0)
                        abr_str = f"{abr}kbps " if abr else ""
                        display = f"🎵 Audio {abr_str}{ext.upper()}{size_str}"
                        audio_only_formats.append({
                            'format_id': fmt['format_id'],
                            'display': display,
                            'ext': ext,
                            'filesize': filesize,
                            'abr': abr or 0,
                            'note': fmt.get('format_note', '')
                        })
                
                # Sort formats
                video_audio_formats.sort(key=lambda x: (x['height'], x['fps']), reverse=True)
                video_only_formats.sort(key=lambda x: (x['height'], x['fps']), reverse=True)
                audio_only_formats.sort(key=lambda x: x['abr'], reverse=True)
                
                # Combine all formats
                video_formats.extend(video_audio_formats)
                if video_only_formats:
                    video_formats.append({'separator': True, 'display': '--- Video Only ---'})
                    video_formats.extend(video_only_formats)
                if audio_only_formats:
                    video_formats.append({'separator': True, 'display': '--- Audio Only ---'})
                    video_formats.extend(audio_only_formats)
                
                # Create display list
                format_options = [fmt['display'] for fmt in video_formats if not fmt.get('separator')]
                
                # Update UI
                app.after(0, lambda: update_format_dropdown(format_options))
                
        except Exception as e:
            app.after(0, lambda: handle_fetch_error(str(e)))
    
    threading.Thread(target=fetch_thread, daemon=True).start()

def update_format_dropdown(options):
    if options:
        format_dropdown.configure(values=options)
        format_dropdown.set(options[0])
        status_label.configure(text="✅ Formats loaded! Select quality and download.", text_color="lightgreen")
        download_button.configure(state="normal")
    else:
        format_dropdown.configure(values=["No formats found"])
        format_dropdown.set("No formats found")
        status_label.configure(text="❌ No downloadable formats found.", text_color="red")

def handle_fetch_error(error):
    messagebox.showerror("Error", f"Failed to fetch formats:\n{error}")
    status_label.configure(text="❌ Failed to fetch formats.", text_color="red")
    format_dropdown.configure(values=["Error loading formats"])
    format_dropdown.set("Error loading formats")

def start_download():
    if not video_formats or format_dropdown.get() in ["Loading...", "No formats found", "Error loading formats"]:
        messagebox.showerror("Error", "Please fetch formats first.")
        return
    
    stop_download_event.clear()
    terminate_button.pack(side='right', padx=5, pady=6)
    download_button.configure(state="disabled")
    fetch_button.configure(state="disabled")
    threading.Thread(target=download_video, daemon=True).start()

def progress_hook(d):
    if stop_download_event.is_set():
        raise Exception("Download terminated by user.")
    
    if d['status'] == 'downloading':
        downloaded_bytes = d.get('downloaded_bytes', 0)
        total_bytes = d.get('total_bytes_estimate', d.get('total_bytes', 0))
        speed = d.get('speed', 0)
        
        if total_bytes > 0:
            percent = downloaded_bytes / total_bytes * 100
            # Schedule UI updates on main thread
            app.after(0, lambda p=percent: update_progress_ui(p, speed))
        else:
            app.after(0, lambda: update_progress_ui(0, speed))
    
    elif d['status'] == 'finished':
        app.after(0, lambda: finish_progress_ui())

def update_progress_ui(percent, speed):
    """Update progress UI elements safely on main thread"""
    try:
        progress_bar.set(percent / 100)
        percent_label.configure(text=f"{percent:.1f}%")
        
        # Show download speed
        if speed and speed > 0:
            if speed > 1024*1024:  # MB/s
                speed_str = f"📶 {speed/(1024*1024):.1f} MB/s"
            else:  # KB/s
                speed_str = f"📶 {speed/1024:.1f} KB/s"
            speed_label.configure(text=speed_str)
    except Exception:
        pass  # Ignore errors if UI elements are destroyed

def finish_progress_ui():
    """Finish progress UI safely on main thread"""
    try:
        progress_bar.stop()  # Stop spinner
        progress_bar.set(1.0)
        percent_label.configure(text="100%")
        speed_label.configure(text="✅ Complete")
    except Exception:
        pass  # Ignore errors if UI elements are destroyed

def download_video():
    global downloaded_file_path
    
    try:
        # Get selected format
        selected_display = format_dropdown.get()
        selected_format = None
        
        for fmt in video_formats:
            if fmt.get('display') == selected_display:
                selected_format = fmt
                break
        
        if not selected_format:
            app.after(0, lambda: messagebox.showerror("Error", "Invalid format selected."))
            return
        
        # Reset progress on main thread
        app.after(0, lambda: reset_progress_ui())
        
        # Setup download options
        ydl_opts = {
            'outtmpl': os.path.join(downloads_folder, '%(uploader)s - %(title)s.%(ext)s'),
            'quiet': True,
            'noplaylist': True,
            'cookiefile': 'cookies.txt' if os.path.exists('cookies.txt') else None,
            'progress_hooks': [progress_hook],
            'no_color': True,  # Disable color codes that might interfere
        }
        
        # Set format
        if selected_format['format_id'] == 'best':
            ydl_opts['format'] = 'best'
        else:
            ydl_opts['format'] = selected_format['format_id']
        
        # Use aria2c for faster downloads if available
        try:
            if subprocess.run(['where', 'aria2c'], capture_output=True, shell=True, timeout=5).returncode == 0:
                ydl_opts['external_downloader'] = 'aria2c'
                ydl_opts['external_downloader_args'] = ['-x', '16', '-k', '1M']
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass  # Continue without aria2c
        
        # Create Downloads directory
        os.makedirs(downloads_folder, exist_ok=True)
        
        # Download
        video_url = url_entry.get().strip()
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            downloaded_file_path = os.path.abspath(ydl.prepare_filename(info))
        
        # Success - update UI on main thread
        app.after(0, lambda: download_success_ui())
        
    except Exception as e:
        if "terminated by user" in str(e):
            app.after(0, lambda: status_label.configure(text="⛔ Download terminated.", text_color="orange"))
        else:
            app.after(0, lambda: download_error_ui(str(e)))
    
    finally:
        app.after(0, lambda: download_cleanup_ui())

def reset_progress_ui():
    """Reset progress UI elements"""
    progress_bar.set(0)
    progress_bar.start()  # Start spinner
    percent_label.configure(text="")
    speed_label.configure(text="")
    status_label.configure(text="📥 Downloading...", text_color="yellow")

def download_success_ui():
    """Update UI for successful download"""
    status_label.configure(text="✅ Download complete!", text_color="lightgreen")
    open_button.pack(pady=(10, 5))

def download_error_ui(error_msg):
    """Update UI for download error"""
    messagebox.showerror("Download Failed", error_msg)
    status_label.configure(text="❌ Download failed.", text_color="red")

def download_cleanup_ui():
    """Cleanup UI after download completion"""
    progress_bar.stop()  # Stop spinner
    terminate_button.pack_forget()
    download_button.configure(state="normal")
    fetch_button.configure(state="normal")

def open_file_location():
    if downloaded_file_path and os.path.exists(downloaded_file_path):
        folder_path = os.path.dirname(downloaded_file_path)
        if os.name == 'nt':  # Windows
            subprocess.Popen(f'explorer /select,"{downloaded_file_path}"')
        else:  # Linux/Mac
            subprocess.Popen(['xdg-open', folder_path])

def terminate_download():
    stop_download_event.set()
    status_label.configure(text="⛔ Terminating download...", text_color="orange")

def clear_all():
    global video_formats, current_video_info
    url_entry.delete(0, ctk.END)
    url_entry.insert(0, placeholder_text)
    url_entry.configure(text_color="gray")
    status_label.configure(text="")
    title_label_info.configure(text="")
    speed_label.configure(text="")
    open_button.pack_forget()
    progress_bar.set(0)
    percent_label.configure(text="")
    stop_download_event.clear()
    terminate_button.pack_forget()
    video_formats = []
    current_video_info = None
    format_dropdown.configure(values=["Fetch formats first"])
    format_dropdown.set("Fetch formats first")
    download_button.configure(state="disabled")
    fetch_button.configure(state="normal")

# UI Elements

# Title
title_label = ctk.CTkLabel(app, text="Enhanced Video Downloader", font=("Arial", 24, "bold"))
title_label.pack(pady=15)

# Frame for input
input_frame = ctk.CTkFrame(app, corner_radius=10)
input_frame.pack(pady=10, padx=20, fill="x")

# URL Entry
placeholder_text = "Paste video URL here..."
url_entry = ctk.CTkEntry(input_frame, font=("Arial", 14), placeholder_text=placeholder_text, height=40)
url_entry.pack(fill="x", padx=10, pady=(10, 5))

# Fetch Button
fetch_button = ctk.CTkButton(input_frame, text="🔍 Fetch Formats", corner_radius=10, 
                           fg_color="#ff6b35", hover_color="#e55a2b", height=35, command=fetch_formats)
fetch_button.pack(pady=(5, 10))

# Video info
title_label_info = ctk.CTkLabel(app, text="", font=("Arial", 12, "italic"), wraplength=600)
title_label_info.pack(pady=(5, 0))

# Format selection frame
format_frame = ctk.CTkFrame(app, corner_radius=10)
format_frame.pack(pady=10, padx=20, fill="x")

format_label = ctk.CTkLabel(format_frame, text="📋 Select Quality/Format:", font=("Arial", 14, "bold"))
format_label.pack(pady=(10, 5))

format_dropdown = ctk.CTkComboBox(format_frame, font=("Arial", 12), height=35, width=500,
                                values=["Fetch formats first"], state="readonly")
format_dropdown.set("Fetch formats first")
format_dropdown.pack(pady=(0, 10))

# Buttons Frame
buttons_frame = ctk.CTkFrame(app, corner_radius=10)
buttons_frame.pack(pady=10)

# Download Button
download_button = ctk.CTkButton(buttons_frame, text="📥 Download Video", corner_radius=10, 
                              fg_color="#1f6aa5", hover_color="#145c9e", width=180, height=40, 
                              command=start_download, state="disabled")
download_button.grid(row=0, column=0, padx=10, pady=10)

# Clear Button
clear_button = ctk.CTkButton(buttons_frame, text="🗑️ Clear", corner_radius=10, 
                           fg_color="#d9534f", hover_color="#c9302c", width=120, height=40, command=clear_all)
clear_button.grid(row=0, column=1, padx=10, pady=10)

# Status Label
status_label = ctk.CTkLabel(app, text="", font=("Arial", 13))
status_label.pack(pady=(5, 10))

# Progress Bar Frame
progress_frame = ctk.CTkFrame(app, corner_radius=10)
progress_frame.pack(pady=5, padx=20, fill='x')

progress_bar = ctk.CTkProgressBar(progress_frame, orientation='horizontal', height=20, progress_color="#00c853")
progress_bar.pack(side='left', fill='x', expand=True, padx=(10, 5), pady=10)
progress_bar.set(0)

percent_label = ctk.CTkLabel(progress_frame, text="", width=50)
percent_label.pack(side='left', padx=5)

# Speed label
speed_label = ctk.CTkLabel(progress_frame, text="", width=100)
speed_label.pack(side='left', padx=5)

# Terminate Button (hidden initially)
terminate_button = ctk.CTkButton(progress_frame, text="❌", width=40, height=32, corner_radius=10, 
                               fg_color="#d9534f", hover_color="#c9302c", command=terminate_download)
terminate_button.pack_forget()

# Open File Location Button (hidden initially)
open_button = ctk.CTkButton(app, text="📂 Open File Location", corner_radius=10, 
                          fg_color="#00b894", hover_color="#00a383", command=open_file_location)

# Main Loop
if __name__ == "__main__":
    app.mainloop()
