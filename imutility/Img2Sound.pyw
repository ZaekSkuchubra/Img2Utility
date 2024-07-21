import tkinter as tk
from tkinter import ttk, filedialog
import numpy as np
from PIL import Image
import wave
import pyaudio
import threading
import time
def choose_file():
    filepath = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
    if filepath:
        image_path.set(filepath)
def image_to_binary(filepath):
    image = Image.open(filepath)
    image = image.convert('L')
    image = image.resize((1000, 1000))
    binary_data = np.array(image).flatten()
    return binary_data
def play_sound(binary_data):
    sample_rate = 44100
    duration = 10
    amplitude = 32767
    num_samples = sample_rate * duration
    if len(binary_data) < num_samples:
        repeated_data = np.tile(binary_data, int(np.ceil(num_samples / len(binary_data))))
        waveform = np.array([int(amplitude * (x / 255.0)) for x in repeated_data[:num_samples]], dtype=np.int16)
    else:
        waveform = np.array([int(amplitude * (x / 255.0)) for x in binary_data[:num_samples]], dtype=np.int16)
    with wave.open("Sound4RomImg.wav", 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(waveform.tobytes())
    def play_audio():
        wf = wave.open("Sound4RomImg.wav", 'rb')
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=wf.getframerate(), output=True)
        data = wf.readframes(1024)
        while data:
            stream.write(data)
            data = wf.readframes(1024)
        stream.stop_stream()
        stream.close()
        p.terminate()
    threading.Thread(target=play_audio).start()
def process_image():
    def update_progress_bar():
        total_steps = 100
        for step in range(total_steps):
            progress_bar['value'] = step + 1
            root.update_idletasks()
            time.sleep(0.05)
    def run():
        progress_bar.start()
        filepath = image_path.get()
        if filepath:
            threading.Thread(target=update_progress_bar).start()
            binary_data = image_to_binary(filepath)
            progress_bar.stop()
            play_sound(binary_data)
    threading.Thread(target=run).start()
root = tk.Tk()
root.configure(background='#6400a6')
root.geometry('613x288')
root.minsize(200, 200)
root.title("Img2Sound")
root.resizable(False, False)
image_path = tk.StringVar()
progress_bar = ttk.Progressbar(root, orient='horizontal', mode='determinate', length=500)
progress_bar.place(anchor='nw', bordermode='ignore', relwidth=1, relx=0.0, rely=0.93, x=0, y=0)
text1 = tk.Text(root, background='#b442ff', borderwidth=0, cursor='based_arrow_down', exportselection=True, font='TkFixedFont', height=10, width=50, insertunfocussed='hollow')
text1.insert('1.0', "This utility can help you convert images\nto sound. It works by transforming the image to binary and playing it as a sound as 0 and 1 are two different frequencies.\n\nMade by:\nGithub Profile:\n\nDear appreciation to Pygubu for helping me with creating the GUI of this utility!")
text1.place(anchor='nw', relheight=0.61, relwidth=1, relx=0.0, rely=0.02, x=0, y=0)
button1 = ttk.Button(root,text="Select Image", command=choose_file)
button1.place(anchor='nw', relwidth=1.0, y=235)
button3 = ttk.Button(root, text="Play", command=process_image)
button3.place(anchor='nw', relx=0.445, rely=0.69, x=0, y=0)
root.mainloop()
