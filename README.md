![Autosplitter](https://i.imgur.com/q78sAp2.png)
# Auto YT Splitter

Auto YT Splitter is a Python application designed to download YouTube videos and split them into parts of specified lengths. It features a GUI built with Tkinter, allowing users to easily manage and process their videos. 

## Features
- Download YouTube videos using `yt-dlp`.
- Split videos into segments of customizable length.
- Save configurations for repeated use.
- User-friendly graphical interface with progress updates.

## Requirements

This application requires the following Python libraries:

- `tkinter` (usually comes with Python)
- `moviepy`
- `yt-dlp`
- `json` (usually comes with Python)
- `re` (usually comes with Python)
- `threading` (usually comes with Python)
- `queue` (usually comes with Python)
- `logging` (usually comes with Python)

To install the required libraries, run:

```bash
pip install moviepy yt-dlp
```
## Getting Started

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/hil2630/YT_AutoSplitter.git
   cd YT_AutoSplitter


2. **Install Dependencies:**

   Make sure you have Python and [https://ffmpeg.org/download.html#build-windows](FFMPEG) installed. Then install the necessary libraries:

   ```bash
   pip install moviepy yt-dlp

3. **Run the Application:**
   Simply run YT_AutoSplitter.bat

## Usage

1. **Launch the Application:**
   The GUI window will open, allowing you to interact with the app.

2. **Configure Settings:**
   - **YouTube URL:** Enter the URL of the YouTube video you wish to download.
   - **Output Folder:** Select the folder where the video parts will be saved.
   - **Part Length (seconds):** Specify the length of each video segment in seconds.

3. **Start Processing:**
   Click the "Download & Split Video" button to begin downloading and processing the video.

4. **View Progress:**
   The progress bar will update as the video is being split into parts.

## Error Handling

If an error occurs during the process, it will be logged in `app.log`. You can view the error logs by opening this file in any text editor. Typical errors include issues with downloading the video or invalid configurations.

   ## Configuration

The application saves the configuration to `config.json`. This includes the last used output folder and part length, allowing you to quickly resume from where you left off.

### Save Configuration

The current settings are saved automatically when you start processing a video. You can also manually save the configuration from the GUI.

### Load Configuration

The application automatically loads the saved configuration on startup, so you don’t need to re-enter your settings each time.

## Error Logs

Logs are saved in `app.log`. This file contains information about the application's operation and any errors that occur. Check this file if you encounter unexpected behavior.

## Troubleshooting

If you encounter any issues or have suggestions, please open an issue on the [GitHub repository](https://github.com/hil2630/YT_AutoSplitter/issues).

