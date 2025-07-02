 Enhanced Video Downloader GUI

A modern, user-friendly desktop application to download videos from YouTube, Instagram, and hundreds of other platforms—powered by [yt-dlp](https://github.com/yt-dlp/yt-dlp) and a beautiful [customtkinter](https://github.com/TomSchimansky/CustomTkinter) interface.

![screenshot](screenshot.png) <!-- Add a screenshot if you have one! -->



 ✨ Features

- Download videos from YouTube, Instagram, and many more sites
- Select video quality and format before downloading
- Progress bar and status updates
- Download location: your system's Downloads folder
- Support for cookies (for private or login-required videos)
- Modern, dark-themed GUI
- No console window—just a clean app!
- One-click open file location after download



 🚀 Installation

 1. Clone the repository
```sh
git clone https://github.com/yourusername/enhanced-video-downloader-gui.git
cd enhanced-video-downloader-gui
```

 2. Install dependencies
```sh
pip install -r requirements.txt
```
Main dependencies:
- `yt-dlp`
- `customtkinter`
- `tkinter` (usually included with Python)
- `ttk` (included with tkinter)

 3. (Optional) Build as an .exe
If you want a standalone Windows executable:
```sh
pip install pyinstaller
pyinstaller --onefile --noconsole --icon=youricon.ico VIDD.py
```
The `.exe` will be in the `dist` folder.



 🖥️ Usage

1. Run the app:
   ```sh
   python VIDD.py
   ```
   or double-click the `.exe` if you built one.

2. Paste a video URL (YouTube, Instagram Reel, etc.)  
3. Click “Fetch Formats” to see available qualities.
4. Select your desired format and click “Download Video”.
5. Find your video in your system’s Downloads folder!



 🔑 Downloading from Instagram or Private Sites

Some sites (like Instagram) require you to be logged in.  
To download from these sites:
1. Use a browser extension like [Get cookies.txt](https://chrome.google.com/webstore/detail/get-cookiestxt/) to export your browser cookies.
2. Place the exported `cookies.txt` file in the same folder as the app (`VIDD.py` or the `.exe`).
3. Restart the app if it was open.



 🛠️ Customization

- Change the app icon: Replace `youricon.ico` with your own icon file.
- Change the theme: Edit the `customtkinter` theme in the code.



 📦 Requirements

- Python 3.8+
- Windows, macOS, or Linux



 📸 Screenshot

<!-- Add a screenshot of your app here! -->
![App Screenshot](screenshot.png)



 🤝 Credits

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for the powerful video downloading engine
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) for the beautiful GUI framework



 📄 License

MIT License



 💡 Ideas & Contributions

Pull requests and suggestions are welcome!  
Feel free to open an issue for feature requests or bug reports.


