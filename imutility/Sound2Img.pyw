import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
from PIL import Image
import wave
import threading
import time
import os
from pydub import AudioSegment

# Function to choose audio file
def choose_file():
    filepath = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav;*.mp3")])
    if filepath:
        file_path.set(filepath)

# Function to convert sound to binary data
def sound_to_binary(filepath, progress_callback):
    # Convert MP3 to WAV if needed
    if filepath.lower().endswith('.mp3'):
        audio = AudioSegment.from_mp3(filepath)
        wav_path = filepath.replace('.mp3', '.wav')
        audio.export(wav_path, format="wav")
        filepath = wav_path

    with wave.open(filepath, 'rb') as wav_file:
        total_frames = wav_file.getnframes()
        frames = wav_file.readframes(total_frames)
        waveform = np.frombuffer(frames, dtype=np.int16)
        binary_data = ((waveform + 32768) // 256).astype(np.uint8)
        progress_callback(50)  # Update progress to 50% after reading and converting the audio file
        # Ensure binary_data has exactly 1,000,000 elements
        if binary_data.size < 1000000:
            binary_data = np.pad(binary_data, (0, 1000000 - binary_data.size), mode='constant', constant_values=0)
        elif binary_data.size > 1000000:
            binary_data = binary_data[:1000000]
        return binary_data

# Function to convert binary data to image
def binary_to_image(binary_data, save_path):
    image_array = binary_data.reshape((1000, 1000))
    image = Image.fromarray(image_array)
    image = image.convert('L')
    image.save(save_path)

# Function to process the chosen file
def process_file():
    def update_progress_bar(value):
        progress_bar['value'] = value
        root.update_idletasks()

    def run():
        filepath = file_path.get()
        if filepath:
            update_progress_bar(0)  # Start progress at 0%
            binary_data = sound_to_binary(filepath, update_progress_bar)
            save_path = os.path.join(os.path.dirname(__file__), "RecoveredImage.png")
            binary_to_image(binary_data, save_path)
            update_progress_bar(100)  # Finish progress at 100%
            messagebox.showinfo("Process Complete", f"Image saved at: {save_path}")

    threading.Thread(target=run).start()

# Setting up the GUI
root = tk.Tk()
root.configure(background='#6400a6')
root.geometry('613x288')
root.minsize(200, 200)
root.title("Audio to Image Converter")
root.resizable(False, False)

file_path = tk.StringVar()

progress_bar = ttk.Progressbar(root, orient='horizontal', mode='determinate', length=500)
progress_bar.place(anchor='nw', bordermode='ignore', relwidth=1, relx=0.0, rely=0.93, x=0, y=0)

text1 = tk.Text(root, background='#b442ff', borderwidth=0, cursor='based_arrow_down', exportselection=True, font='TkFixedFont', height=10, width=50, insertunfocussed='hollow')
text1.insert('1.0', "This utility can help you convert audio files to images.\nSelect an audio file to create an image from it.\n\nMade by:\nGithub Profile:\n\nDear appreciation to Pygubu for helping me with creating the GUI of this utility!")
text1.place(anchor='nw', relheight=0.61, relwidth=1, relx=0.0, rely=0.02, x=0, y=0)

button1 = ttk.Button(root, text="Choose File", command=choose_file)
button1.place(anchor='nw', relwidth=1.0, y=235)

button2 = ttk.Button(root, text="Play", command=process_file)
button2.place(anchor='nw', relx=0.445, rely=0.69, x=0, y=0)

root.mainloop()
