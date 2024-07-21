import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image
import base64
import io
import threading
from queue import Queue
import os
def open_file_explorer():
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")])
    if file_path:
        global selected_file
        selected_file = file_path
        button3.config(text=f"Selected: {file_path}")
def convert_to_base64():
    if selected_file:
        file_size = os.path.getsize(selected_file)
        if file_size > 50 * 1024:
            text1.pack_forget()
            show_info_window()
        progressbar1['value'] = 0
        text1.config(state=tk.NORMAL)
        text1.delete(1.0, tk.END)
        text1.config(state=tk.DISABLED)
        global stop_encoding
        stop_encoding = False
        threading.Thread(target=convert_and_update, daemon=True).start()
    else:
        messagebox.showwarning("No file selected", "Please select an image file first.")
def show_info_window():
    info_window = tk.Toplevel(root)
    info_window.title("Information")
    info_window.geometry("600x100")
    info_window.configure(bg='#f0f0f0')
    label = tk.Label(info_window, text="File containing b64 image data will be placed where the code is located at.", bg='#f0f0f0', font=('Arial', 12))
    label.pack(pady=20)
    button_ok = tk.Button(info_window, text="OK", command=info_window.destroy, borderwidth=0, bg= ("grey70"))
    button_ok.pack()
def convert_and_update():
    try:
        image = Image.open(selected_file)
        image_stream = io.BytesIO()
        image.save(image_stream, format=image.format)
        image_data = image_stream.getvalue()
        chunk_size = 1024 * 1024
        num_chunks = len(image_data) // chunk_size + (1 if len(image_data) % chunk_size else 0)
        progressbar1['maximum'] = num_chunks
        encoded_chunks = []
        for i in range(0, len(image_data), chunk_size):
            if stop_encoding:
                break
            chunk = image_data[i:i + chunk_size]
            encoded_chunk = base64.b64encode(chunk).decode('utf-8')
            encoded_chunks.append(encoded_chunk)
            queue.put(('progress', 1))
            threading.Event().wait(0.1)
        encoded_data = ''.join(encoded_chunks)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_file = os.path.join(script_dir, 'output_base64.txt')
        with open(output_file, 'w') as f:
            f.write(encoded_data)
        queue.put(('progress', -1))
        queue.put(('file', output_file))
    except Exception as e:
        queue.put(('error', str(e)))
def update_gui():
    while not queue.empty():
        item = queue.get()
        if item[0] == 'progress':
            if item[1] == -1:
                text1.config(state=tk.NORMAL)
                text1.insert(tk.END, "\nConversion Completed!")
                text1.config(state=tk.DISABLED)
            else:
                progressbar1['value'] += item[1]
        elif item[0] == 'file':
            output_file = item[1]
            messagebox.showinfo("Conversion Completed", f"Base64 encoded data has been saved to {output_file}")
        elif item[0] == 'error':
            messagebox.showerror("Error", f"Failed to convert image to base64: {item[1]}")
    root.after(100, update_gui)
def copy_to_clipboard():
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_file = os.path.join(script_dir, 'output_base64.txt')
        with open(output_file, 'r') as f:
            base64_data = f.read()
        root.clipboard_clear()
        root.clipboard_append(base64_data)
        root.update()
        messagebox.showinfo("Copied to Clipboard", "Base64 encoded data has been copied to the clipboard.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to copy to clipboard: {str(e)}")
root = tk.Tk()
root.configure(background='#fbff42', cursor='plus', padx=10, pady=10)
root.geometry('770x400+400+200')
root.resizable(False, False)
root.title('Img2Bas64')
root.configure(highlightbackground='#fbff42', highlightcolor='#fbff42')
selected_file = None
queue = Queue()
stop_encoding = False
button1 = ttk.Button(root, text='Transform To Base 64', compound='left', style='Toolbutton', command=convert_to_base64)
button1.place(anchor='nw', bordermode='inside', relheight=0.05, relwidth=0.16, relx=0.84, rely=0.95, x=0, y=0)
button_copy = ttk.Button(root, text='Copy to Clipboard', style='Toolbutton', command=copy_to_clipboard)
button_copy.place(anchor='nw', bordermode='inside', relheight=0.05, relwidth=0.16, relx=0.67, rely=0.95, x=0, y=0)
progressbar1 = ttk.Progressbar(root, cursor='plus', orient='horizontal', mode='determinate')
progressbar1.place(anchor='nw', bordermode='inside', relheight=0.05, relwidth=0.66, rely=0.95, x=0, y=0)
button3 = ttk.Button(root, text='Select An Image to Transform', style='Toolbutton', cursor='arrow', command=open_file_explorer)
button3.place(anchor='nw', relwidth=1.0, relx=0.0, rely=0.87, x=0, y=0)
text1 = tk.Text(root, background='#fdffb7', height=10, width=50)
text1.config(state=tk.DISABLED)
text1.place(anchor='nw', relheight=0.84, relwidth=0.3, relx=0.69, x=0, y=0)
text2 = tk.Text(root, background='#feffd9', height=10, width=50, blockcursor=False, setgrid=False)
text2.insert(tk.END, '''Thank you for using my utility.
Originally made by:
Github profile:

Dear appreciation to Pygubu Designer for helping me with 
this GUI.

Instructions:
1) Press Select Image to Transform.
2) Press Transform To Base 64
3) Wait for the process to finish
4) Your output will be displayed on the text box at the right
of this one.

Done! Ready to copy.''')
text2.config(state=tk.DISABLED)
text2.place(anchor='nw', relheight=0.84, relwidth=0.68, relx=0.0, x=0, y=0)
root.after(10, update_gui)
root.mainloop()
