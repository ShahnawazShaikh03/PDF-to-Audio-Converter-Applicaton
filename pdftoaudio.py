import PyPDF2
import pytesseract
from tkinter import Tk, filedialog, Button, Label, StringVar, Canvas, Toplevel, Entry
from PIL import Image, ImageTk
from pdf2image import convert_from_path
from gtts import gTTS
import os
import subprocess


pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  

audio_file = ""

def prompt_for_password():
    """Prompts the user to enter a PDF password."""
    password_window = Toplevel(root)
    password_window.title("Enter PDF Password")
    password_window.geometry("300x150")

    Label(password_window, text="Enter PDF Password:", font=("Helvetica", 12)).pack(pady=10)
    pwd_var = StringVar()
    pwd_entry = Entry(password_window, textvariable=pwd_var, show="*", font=("Helvetica", 12))
    pwd_entry.pack(pady=5)
    pwd_entry.focus()

    result = {'password': None}

    def submit_password():
        result['password'] = pwd_var.get()
        password_window.destroy()

    Button(password_window, text="Submit", command=submit_password, font=("Helvetica", 12)).pack(pady=10)
    password_window.wait_window()
    return result['password']


def extract_text_from_pdf(file_path):
    """Extracts text from a PDF file, using OCR if needed."""
    full_text = ""

    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)

            if reader.is_encrypted:
                print("PDF is encrypted. Attempting to decrypt...")
                try:
                    result = reader.decrypt("")  
                    if result == 0:
                        password = prompt_for_password()
                        result = reader.decrypt(password)
                        if result == 0:
                            return "Error: Incorrect password or decryption failed."
                except Exception as e:
                    return f"Error decrypting PDF: {str(e)}"

            total_pages = len(reader.pages)
            print(f"Processing {total_pages} pages...")

            for page_num in range(total_pages):
                try:
                    text = reader.pages[page_num].extract_text()
                    if text:
                        full_text += text + "\n"
                except Exception as e:
                    print(f"Text extraction failed for page {page_num}: {str(e)}")

            if not full_text.strip():
                print("No text found, performing OCR...")
                images = convert_from_path(file_path)
                for img in images:
                    full_text += pytesseract.image_to_string(img) + "\n"

        return full_text.strip() if full_text.strip() else "Error: No text could be extracted."

    except Exception as e:
        return f"Error reading PDF: {str(e)}"


def convert_text_to_speech(text, output_filename):
    """Converts extracted text to speech and saves as an MP3 file."""
    try:
        tts = gTTS(text=text, lang='en')
        tts.save(output_filename)
        return True
    except Exception as e:
        print(f"Error generating speech: {e}")
        return False

def play_audio():
    """Plays the generated audio file using the default media player."""
    if not audio_file:
        status_var.set("No audio file available.")
        return
    try:
        subprocess.run(["start", "", audio_file], shell=True)  
    except Exception as e:
        status_var.set(f"Error playing audio: {str(e)}")

def select_pdf():
    """Handles file selection, extraction, and text-to-speech conversion."""
    global audio_file
    file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    if not file_path:
        status_var.set("No file selected.")
        return

    status_var.set("Extracting text, please wait...")
    root.update()

    extracted_text = extract_text_from_pdf(file_path)

    if "Error:" in extracted_text:
        status_var.set(extracted_text)
        return

    output_filename = os.path.splitext(os.path.basename(file_path))[0] + "_audio.mp3"
    success = convert_text_to_speech(extracted_text, output_filename)

    if success:
        audio_file = output_filename
        status_var.set(f"Audio saved as {output_filename}. Click 'Play Audio' to listen.")
        play_button.config(state="normal")
    else:
        status_var.set("Error converting text to speech.")

def show_about():
    """Displays developer details in a pop-up window."""
    about_window = Toplevel(root)
    about_window.title("About")
    about_window.geometry("400x200")

    about_text = """
    Developers: Pranav Raut
                Shahnawaz Shaikh
                Sumedh Gaikwad
                Varad Vaidya 
      Mentor  : Mr V.K.Sambhar
      College : MMCOE Karvenagar
    Description: A simple PDF to speech converter using Python.
    """

    label = Label(about_window, text=about_text, font=("Helvetica", 12), padx=20, pady=20)
    label.pack()

    close_button = Button(about_window, text="Close", font=("Helvetica", 12), command=about_window.destroy)
    close_button.pack(pady=10)


root = Tk()
root.title("PDF to Speech Converter")
root.geometry("1200x675")
root.configure(bg="#f0f0f0")  


icon_path = "favicon.ico"  
if os.path.exists(icon_path):
    root.iconbitmap(icon_path)

status_var = StringVar()
status_var.set("")

image_path = "background.png"  
if os.path.exists(image_path):
    bg_image = Image.open(image_path)
    bg_image = bg_image.resize((1200, 675), Image.LANCZOS)
    bg_image = ImageTk.PhotoImage(bg_image)
    canvas = Canvas(root, width=1200, height=675)
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, image=bg_image, anchor="nw")

    canvas.create_text(600, 50, text="Select a PDF file to convert to speech", font=("Helvetica", 24), fill="black")
    select_button = Button(root, text="Select PDF", font=("Helvetica", 18), command=select_pdf, bg="#4CAF50", fg="white")
    play_button = Button(root, text="Play Audio", font=("Helvetica", 19), command=play_audio, state="disabled", bg="#008CBA", fg="white")
    status_label = Label(root, textvariable=status_var, font=("Helvetica", 12), fg="blue", bg="#f0f0f0")
    about_button = Button(root, text="About", font=("Helvetica", 12), command=show_about, bg="#FF9800", fg="white")

    canvas.create_window(500, 250, anchor="nw", window=select_button)
    canvas.create_window(500, 400, anchor="nw", window=play_button)
    canvas.create_window(500, 500, anchor="nw", window=status_label)
    canvas.create_window(1050, 20, anchor="nw", window=about_button)

root.mainloop()
