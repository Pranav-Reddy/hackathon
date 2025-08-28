import tkinter as tk
import pyautogui
import io
import threading
import wave
import pyaudio
from PIL import Image
from google.cloud import vision, speech
import vertexai
from vertexai.generative_models import GenerativeModel, Part
import google.cloud.texttospeech as tts
import simpleaudio as sa
import tempfile
import os
import base64

PROJECT_ID = "hack-team-eclipse"  # Replace with your actual project ID
LOCATION = "us-central1"

# Global variables for lazy initialization
_model = None
_initialized = False

def get_gemini_model():
    """Get or initialize the Gemini model (lazy initialization)"""
    global _model, _initialized
    
    if not _initialized:
        print("🚀 Initializing Vertex AI (first time only)...")
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        
        print("🤖 Creating Gemini model...")
        _model = GenerativeModel("gemini-2.5-flash")
        _initialized = True
    
    return _model

def text_to_audio(txt, lang="en-US"):
    """Convert text to speech and play it"""
    try:
        # Language mapping
        voice_map = {
            "en-US": "en-US-Standard-F",
            "en-GB": "en-GB-Standard-A", 
            "es-ES": "es-ES-Standard-A",
            "fr-FR": "fr-FR-Standard-A",
        }
        
        voice_name = voice_map.get(lang, "en-US-Standard-F")
        language_code = lang
        
        # Create TTS client and synthesize speech
        client = tts.TextToSpeechClient()
        
        text_input = tts.SynthesisInput(text=txt)
        voice_params = tts.VoiceSelectionParams(
            language_code=language_code,
            name=voice_name
        )
        audio_config = tts.AudioConfig(
            audio_encoding=tts.AudioEncoding.LINEAR16,
            speaking_rate=1.0,
            pitch=0.0
        )
        
        print("🔊 Converting response to speech...")
        response = client.synthesize_speech(
            input=text_input,
            voice=voice_params,
            audio_config=audio_config
        )
        
        print("🎵 Playing audio response...")
        play_obj = sa.play_buffer(
            response.audio_content,
            num_channels=1,
            bytes_per_sample=2,
            sample_rate=24000
        )
        play_obj.wait_done()
        print("✅ Audio playback completed!")
        return True
        
    except Exception as e:
        print(f"❌ TTS Error: {str(e)}")
        return False

def transcribe_speech(audio_path):
    """Transcribe audio using Google Cloud Speech-to-Text API."""
    client = speech.SpeechClient()
    
    with open(audio_path, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US"
    )

    response = client.recognize(config=config, audio=audio)
    transcript = " ".join([result.alternatives[0].transcript for result in response.results])
    return transcript

def generate_gemini_answer(labels, ocr_text, user_question, image_data=None):
    """Generate answer using Gemini 2.5 Flash model."""
    try:
        # Get the model (lazy initialization)
        model = get_gemini_model()
        
        # Prepare the prompt
        prompt = f"""
Based on the following information from a screenshot, please answer the user's question:

Image Labels: {labels}

OCR Text: {ocr_text}

User Question: {user_question}

Please provide a helpful and accurate answer based on the visual content and text extracted from the image.
"""
        
        # Generate content
        if image_data:
            # Convert image to base64 for Gemini
            image_part = Part.from_data(image_data, mime_type="image/png")
            response = model.generate_content([prompt, image_part])
        else:
            response = model.generate_content(prompt)
        
        return response.text
    
    except Exception as e:
        return f"Error generating response: {str(e)}"

class SnippingToolOCR:
    def __init__(self):
        self.start_x = None
        self.start_y = None
        self.rect = None
        self.screenshot = None
        self.screenshot_data = None
        self.ocr_text = ""
        self.labels = ""
        self.audio_path = tempfile.mktemp(suffix=".wav")
        self.recording = False
        self.init_popup()

    def init_popup(self):
        """Initialize the main popup window."""
        self.popup = tk.Tk()
        self.popup.title("Snipping OCR + QnA Tool")
        self.popup.geometry("300x150")
        self.popup.resizable(False, False)

        tk.Label(self.popup, text="Choose an action:", font=("Arial", 14)).pack(pady=10)

        tk.Button(
            self.popup,
            text="🖼️ Snip + Ask Question",
            command=self.start_snipping,
            width=25,
            font=("Arial", 12),
            bg="#4CAF50",
            fg="white"
        ).pack(pady=5)
        
        tk.Button(
            self.popup,
            text="❌ Cancel",
            command=self.popup.quit,
            width=25,
            font=("Arial", 12),
            bg="#f44336",
            fg="white"
        ).pack(pady=5)

        self.popup.mainloop()

    def start_snipping(self):
        """Start the screen snipping process."""
        self.popup.destroy()
        self.root = tk.Tk()
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-alpha', 0.3)
        self.root.configure(background='black')

        self.canvas = tk.Canvas(self.root, cursor='cross', bg='gray', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.canvas.bind("<Escape>", lambda e: self.root.destroy())

        # Add instruction label
        instruction = tk.Label(
            self.root,
            text="Click and drag to select area. Press ESC to cancel.",
            font=("Arial", 16),
            bg="black",
            fg="white"
        )
        instruction.pack(pady=10)

        self.root.mainloop()

    def on_mouse_down(self, event):
        """Handle mouse down event for selection."""
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline='red', width=3
        )

    def on_mouse_drag(self, event):
        """Handle mouse drag event for selection."""
        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_mouse_up(self, event):
        """Handle mouse up event to complete selection."""
        end_x = self.canvas.canvasx(event.x)
        end_y = self.canvas.canvasy(event.y)
        self.root.destroy()

        x1 = int(min(self.start_x, end_x))
        y1 = int(min(self.start_y, end_y))
        x2 = int(max(self.start_x, end_x))
        y2 = int(max(self.start_y, end_y))

        # Ensure minimum selection size
        if abs(x2 - x1) < 10 or abs(y2 - y1) < 10:
            print("Selection too small. Please try again.")
            self.__init__()
            return

        self.screenshot = pyautogui.screenshot(region=(x1, y1, x2 - x1, y2 - y1))
        self.process_image()

    def process_image(self):
        """Process the screenshot with OCR and image labeling."""
        try:
            # Convert PIL image to bytes
            img_byte_arr = io.BytesIO()
            self.screenshot.save(img_byte_arr, format='PNG')
            self.screenshot_data = img_byte_arr.getvalue()

            client = vision.ImageAnnotatorClient()
            image = vision.Image(content=self.screenshot_data)

            # Perform OCR
            response = client.document_text_detection(image=image)
            
            # Perform label detection
            label_response = client.label_detection(image=image)

            if response.error.message:
                raise Exception(f"OCR Error: {response.error.message}")

            # Extract text and labels
            self.ocr_text = response.full_text_annotation.text.strip() if response.full_text_annotation else "No text detected"
            self.labels = ", ".join([label.description for label in label_response.label_annotations[:10]])  # Limit to top 10 labels

            print("\n=== OCR Extracted ===")
            print(self.ocr_text if self.ocr_text else "No text found")
            print("\n=== Image Labels ===")
            print(self.labels if self.labels else "No labels found")

            self.init_record_popup()

        except Exception as e:
            print(f"Error processing image: {str(e)}")
            self.__init__()

    def init_record_popup(self):
        """Initialize the recording popup window."""
        self.rec_popup = tk.Tk()
        self.rec_popup.title("Ask Your Question")
        self.rec_popup.geometry("300x200")
        self.rec_popup.resizable(False, False)

        tk.Label(self.rec_popup, text="Record your question:", font=("Arial", 12)).pack(pady=10)

        self.record_button = tk.Button(
            self.rec_popup,
            text="🎤 Start Recording",
            command=self.start_recording,
            font=("Arial", 12),
            bg="#2196F3",
            fg="white",
            width=20
        )
        self.record_button.pack(pady=5)

        self.stop_button = tk.Button(
            self.rec_popup,
            text="⏹️ Stop & Process",
            command=self.stop_recording,
            font=("Arial", 12),
            bg="#FF9800",
            fg="white",
            width=20,
            state="disabled"
        )
        self.stop_button.pack(pady=5)

        tk.Button(
            self.rec_popup,
            text="❌ Cancel",
            command=self.rec_popup.quit,
            font=("Arial", 12),
            bg="#f44336",
            fg="white",
            width=20
        ).pack(pady=5)

        self.rec_popup.mainloop()

    def start_recording(self):
        """Start audio recording."""
        self.recording = True
        self.record_button.config(state="disabled", text="🔴 Recording...")
        self.stop_button.config(state="normal")
        threading.Thread(target=self.record_audio, daemon=True).start()

    def stop_recording(self):
        """Stop audio recording and process the question."""
        self.recording = False
        self.stop_button.config(text="Processing...", state="disabled")
        self.rec_popup.after(1000, self.rec_popup.quit)  # Close popup after 1 second

    def record_audio(self):
        """Record audio from microphone."""
        try:
            p = pyaudio.PyAudio()
            stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=1024
            )
            frames = []

            print("Recording... Speak your question now.")

            while self.recording:
                data = stream.read(1024, exception_on_overflow=False)
                frames.append(data)

            stream.stop_stream()
            stream.close()
            p.terminate()

            # Save audio file
            with wave.open(self.audio_path, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
                wf.setframerate(16000)
                wf.writeframes(b''.join(frames))

            print("Recording stopped. Processing...")

            # Transcribe and get answer
            transcript = transcribe_speech(self.audio_path)
            print(f"\n=== Your Question ===\n{transcript}")

            if transcript.strip():
                response = generate_gemini_answer(
                    self.labels,
                    self.ocr_text,
                    transcript,
                    self.screenshot_data
                )
                print(f"\n=== Gemini Answer ===\n{response}")
                
                # NEW: Convert response to speech and play it
                text_to_audio(response)
                
            else:
                print("No speech detected. Please try again.")
                # Play error message
                text_to_audio("No speech detected. Please try again.")

            # Clean up
            try:
                os.unlink(self.audio_path)
            except:
                pass

        except Exception as e:
            print(f"Error during recording: {str(e)}")
            # Play error message
            text_to_audio("An error occurred during recording.")

if __name__ == "__main__":
    print("Starting Snipping Tool OCR + QnA with Audio Response...")
    print("Make sure you have set up Google Cloud credentials!")
    SnippingToolOCR()
