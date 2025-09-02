from tkinter import ttk
import tkinter as tk
import pyautogui
import io
import threading
import wave
import pyaudio
import sys
from PIL import Image, ImageTk
from google.cloud import vision, speech
import base64
import signal
import vertexai
from vertexai.generative_models import GenerativeModel, Part
import google.cloud.texttospeech as tts
import simpleaudio as sa
import tempfile
import os
import base64
import time

PROJECT_ID = ""  # Replace with your actual project ID
LOCATION = "us-central1"

# Global variables for lazy initialization
_model = None
_initialized = False

# Global language setting (default to English US)
LANGUAGE = "en-US"

# Force quit helper
def force_quit(event=None):
    print("🛑 Force quitting...")
    os._exit(0)  # hard kill, bypass cleanup

# Translation dictionary for UI text (keeping your existing translations)
TRANSLATIONS = {
    "en-US": {
        "app_title": "Snip Tool",
        "take_snip": "Take Snip",
        "fraud_detection": "Scam/Fraud Detection",
        "record_audio": "Record Audio",
        "ask_question": "Ask Your Question",
        "record_instruction": "Record your question about the image:",
        "start_recording": "Start Recording",
        "stop_process": "Stop & Process",
        "cancel": "Cancel",
        "recording": "Recording...",
        "processing": "Processing...",
        "snip_instruction": "Click and drag to select area for {mode}. Press ESC to cancel.",
        "fraud_mode": "fraud detection",
        "qa_mode": "Q&A",
        "security_alert": "⚠️ SCAM/FRAUD DETECTED! ⚠️",
        "close_alert": "🛡️ CLOSE ALERT",
        "report_scam": "📢 REPORT SCAM",
        "selection_too_small": "Selection too small. Please try again.",
        "invalid_selection": "Invalid selection. Please try again.",
        "screenshot_error": "Error taking screenshot: {error}",
        "ocr_extracted": "OCR Extracted",
        "image_labels": "Image Labels",
        "no_text_found": "No text found",
        "no_labels_found": "No labels found",
        "your_question": "Your Question",
        "gemini_answer": "Gemini Answer",
        "no_speech_detected": "No speech detected. Please try again.",
        "recording_error": "An error occurred during recording.",
        "fraud_analysis": "Analyzing image for scam/fraud...",
        "fraud_result": "Fraud Detection Result",
        "no_fraud_detected": "No fraud detected - content appears safe",
        "analysis_complete": "Analysis complete. {result}",
        "error_fraud_detection": "Error during fraud detection: {error}",
        "error_processing_image": "Error processing image: {error}",
        "language_set": "Language set to: {language}",
        "unknown_language": "Unknown language '{language}', using default: {default}",
        "supported_languages": "Supported languages: en, es, fr, de, it, pt, ja, ko, zh",
        "default_language": "Using default language: {language}",
        "usage": "Usage: python script.py [language]",
        "example": "Example: python script.py es (for Spanish)"
    },
    # ... (keeping all other language translations as they are)
}

def get_text(key, **kwargs):
    """Get translated text for the current language"""
    lang_dict = TRANSLATIONS.get(LANGUAGE, TRANSLATIONS["en-US"])
    text = lang_dict.get(key, TRANSLATIONS["en-US"].get(key, key))
    
    if kwargs:
        try:
            return text.format(**kwargs)
        except:
            return text
    return text

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

def text_to_audio(txt, lang=None, save_to_file=True):
    """Convert text to speech, play it, and optionally save to WAV file"""
    if lang is None:
        lang = LANGUAGE
        
    try:
        voice_map = {
            "en-US": "en-US-Standard-F",
            "en-GB": "en-GB-Standard-A", 
            "es-ES": "es-ES-Standard-A",
            "fr-FR": "fr-FR-Standard-A",
            "de-DE": "de-DE-Standard-A",
            "it-IT": "it-IT-Standard-A",
            "pt-BR": "pt-BR-Standard-A",
            "ja-JP": "ja-JP-Standard-A",
            "ko-KR": "ko-KR-Standard-A",
            "zh-CN": "cmn-CN-Standard-A",
        }
        
        voice_name = voice_map.get(lang, "en-US-Standard-F")
        language_code = lang
        
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
        
        if save_to_file:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"tts_output_{timestamp}.wav"
            
            try:
                with open(filename, "wb") as audio_file:
                    audio_file.write(response.audio_content)
                print(f"💾 Audio saved to: {filename}")
            except Exception as save_error:
                print(f"⚠️ Could not save audio file: {save_error}")
        
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
        language_code=LANGUAGE
    )

    response = client.recognize(config=config, audio=audio)
    transcript = " ".join([result.alternatives[0].transcript for result in response.results])
    return transcript

def generate_gemini_answer(labels, ocr_text, user_question, image_data=None):
    """Generate answer using Gemini 2.5 Flash model."""
    try:
        model = get_gemini_model()
        
        prompt = f"""
Based on the following information from a screenshot, please answer the user's question:

Image Labels: {labels}

OCR Text: {ocr_text}

User Question: {user_question}

Please provide a helpful and accurate answer based on the visual content and text extracted from the image.
"""
        
        if image_data:
            image_part = Part.from_data(image_data, mime_type="image/png")
            response = model.generate_content([prompt, image_part])
        else:
            response = model.generate_content(prompt)
        
        return response.text
    
    except Exception as e:
        return f"Error generating response: {str(e)}"

def detect_scam_fraud(labels, ocr_text, image_data=None):
    """Detect scam/fraud using Gemini 2.5 Flash model."""
    try:
        model = get_gemini_model()
        
        prompt = f"""
Analyze this image for potential scams, fraud, phishing attempts, or malicious content. Look for:

1. Suspicious URLs or domains
2. Fake login pages
3. Phishing emails or messages
4. Fake security warnings
5. Too-good-to-be-true offers
6. Urgent action requests
7. Suspicious payment requests
8. Fake tech support messages
9. Romance scams
10. Investment/crypto scams

Image Labels: {labels}

OCR Text: {ocr_text}

Respond with either:
- "FRAUD DETECTED: [specific reason]" if you detect any scam/fraud indicators
- "SAFE: No fraud indicators detected" if the content appears legitimate

Be very thorough in your analysis and err on the side of caution.
"""
        
        if image_data:
            image_part = Part.from_data(image_data, mime_type="image/png")
            response = model.generate_content([prompt, image_part])
        else:
            response = model.generate_content(prompt)
        
        return response.text
    
    except Exception as e:
        return f"Error analyzing for fraud: {str(e)}"

class ScamDetectedPopup:
    """Red malware-style popup for scam detection"""
    def __init__(self, detection_result):
        self.popup = tk.Toplevel()  # Changed from Tk() to Toplevel()
        self.popup.bind_all("<Control-q>", force_quit)
        self.popup.bind_all("<Escape>", self.close_popup)
        self.popup.title("⚠️ SECURITY ALERT")
        self.popup.geometry("450x300")
        self.popup.resizable(False, False)
        self.popup.configure(bg="#8B0000")
        
        self.popup.attributes('-topmost', True)
        self.popup.overrideredirect(True)
        
        self.popup.update_idletasks()
        x = (self.popup.winfo_screenwidth() // 2) - (450 // 2)
        y = (self.popup.winfo_screenheight() // 2) - (300 // 2)
        self.popup.geometry(f"450x300+{x}+{y}")
        
        main_frame = tk.Frame(self.popup, bg="#FF0000", relief="raised", bd=3)
        main_frame.pack(fill="both", expand=True, padx=3, pady=3)
        
        inner_frame = tk.Frame(main_frame, bg="#8B0000")
        inner_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        title_frame = tk.Frame(inner_frame, bg="#8B0000")
        title_frame.pack(fill="x", pady=(10, 5))
        
        warning_label = tk.Label(
            title_frame,
            text=get_text("security_alert"),
            font=("Arial", 18, "bold"),
            bg="#8B0000",
            fg="#FFFF00",
        )
        warning_label.pack()
        
        def blink():
            if self.popup.winfo_exists():
                current_color = warning_label.cget("fg")
                new_color = "#FFFF00" if current_color == "#FF0000" else "#FF0000"
                warning_label.config(fg=new_color)
                self.popup.after(500, blink)
        
        blink()
        
        result_frame = tk.Frame(inner_frame, bg="#8B0000")
        result_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        result_text = tk.Text(
            result_frame,
            font=("Arial", 11),
            bg="#FFE4E1",
            fg="#8B0000",
            wrap="word",
            relief="solid",
            bd=2,
            height=8
        )
        result_text.pack(fill="both", expand=True)
        result_text.insert("1.0", detection_result)
        result_text.config(state="disabled")
        
        button_frame = tk.Frame(inner_frame, bg="#8B0000")
        button_frame.pack(fill="x", pady=(10, 10))
        
        close_btn = tk.Button(
            button_frame,
            text=get_text("close_alert"),
            command=self.close_popup,
            font=("Arial", 12, "bold"),
            bg="#FF4500",
            fg="white",
            relief="raised",
            bd=3,
            cursor="hand2"
        )
        close_btn.pack(side="right", padx=10)
        
        report_btn = tk.Button(
            button_frame,
            text=get_text("report_scam"),
            command=self.report_scam,
            font=("Arial", 12, "bold"),
            bg="#DC143C",
            fg="white",
            relief="raised",
            bd=3,
            cursor="hand2"
        )
        report_btn.pack(side="left", padx=10)
        
        def start_move(event):
            self.popup.x = event.x
            self.popup.y = event.y

        def stop_move(event):
            self.popup.x = None
            self.popup.y = None

        def do_move(event):
            if hasattr(self.popup, 'x') and self.popup.x is not None and self.popup.y is not None:
                deltax = event.x - self.popup.x
                deltay = event.y - self.popup.y
                x = self.popup.winfo_x() + deltax
                y = self.popup.winfo_y() + deltay
                self.popup.geometry(f"+{x}+{y}")

        title_frame.bind("<Button-1>", start_move)
        title_frame.bind("<ButtonRelease-1>", stop_move)
        title_frame.bind("<B1-Motion>", do_move)
    
    def close_popup(self, event=None):
        """Close the popup"""
        self.popup.destroy()
    
    def report_scam(self):
        """Placeholder for reporting functionality"""
        print("Report scam functionality - could integrate with authorities or security services")

class ModernButton:
    """Custom modern button class"""
    def __init__(self, parent, text, command, bg_color, hover_color, icon="", width=280, height=50):
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        
        self.frame = tk.Frame(parent, bg=bg_color, height=height, width=width)
        self.frame.pack_propagate(False)
        self.frame.pack(pady=8, padx=20, fill='x')
        
        self.label = tk.Label(
            self.frame,
            text=f"{icon} {text}",
            bg=bg_color,
            fg="white",
            font=("Segoe UI", 12, "bold"),
            cursor="hand2"
        )
        self.label.pack(expand=True, fill='both')
        
        self.label.bind("<Button-1>", lambda e: self.command())
        self.label.bind("<Enter>", self.on_enter)
        self.label.bind("<Leave>", self.on_leave)
        self.frame.bind("<Button-1>", lambda e: self.command())
        self.frame.bind("<Enter>", self.on_enter)
        self.frame.bind("<Leave>", self.on_leave)
    
    def on_enter(self, event):
        """Handle mouse enter"""
        self.frame.config(bg=self.hover_color)
        self.label.config(bg=self.hover_color)
    
    def on_leave(self, event):
        """Handle mouse leave"""
        self.frame.config(bg=self.bg_color)
        self.label.config(bg=self.bg_color)

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
        self.mode = "normal"
        self.root = None  # Track the snipping window
        self.popup = None  # Track the main popup
        self.rec_popup = None  # Track the recording popup
        self.init_popup()

    def init_popup(self):
        """Initialize the modern main popup window."""
        # Clean up any existing windows
        self.cleanup_windows()
        
        self.popup = tk.Tk()
        self.popup.title(get_text("app_title"))
        self.popup.geometry("320x250")
        self.popup.resizable(False, False)
        self.popup.configure(bg="#f8f9fa")
        
        self.popup.overrideredirect(True)
        
        self.popup.update_idletasks()
        x = (self.popup.winfo_screenwidth() // 2) - (320 // 2)
        y = (self.popup.winfo_screenheight() // 2) - (250 // 2)
        self.popup.geometry(f"320x250+{x}+{y}")
        
        main_frame = tk.Frame(self.popup, bg="white", relief="raised", bd=1)
        main_frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        title_frame = tk.Frame(main_frame, bg="white", height=40)
        title_frame.pack(fill="x", padx=0, pady=0)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame, 
            text=get_text("app_title"), 
            font=("Segoe UI", 14, "bold"), 
            bg="white", 
            fg="#2c3e50"
        )
        title_label.pack(side="left", padx=15, pady=10)
        
        close_btn = tk.Label(
            title_frame, 
            text="✕", 
            font=("Segoe UI", 16), 
            bg="white", 
            fg="#7f8c8d",
            cursor="hand2"
        )
        close_btn.pack(side="right", padx=15, pady=10)
        close_btn.bind("<Button-1>", lambda e: self.quit_app())
        close_btn.bind("<Enter>", lambda e: close_btn.config(fg="#e74c3c"))
        close_btn.bind("<Leave>", lambda e: close_btn.config(fg="#7f8c8d"))
        
        content_frame = tk.Frame(main_frame, bg="white")
        content_frame.pack(fill="both", expand=True, padx=0, pady=(0, 20))
        
        ModernButton(
            content_frame,
            get_text("take_snip"),
            self.start_normal_snipping,
            "#007bff",
            "#0056b3",
            "📷",
            width=280,
            height=50
        )
        
        ModernButton(
            content_frame,
            get_text("fraud_detection"), 
            self.start_fraud_detection,
            "#dc3545",
            "#c82333",
            "🛡️",
            width=280,
            height=50
        )
        
        ModernButton(
            content_frame,
            get_text("record_audio"),
            self.record_audio_only,
            "#6c757d",
            "#545b62",
            "🎙️",
            width=280,
            height=50
        )
        
        def start_move(event):
            self.popup.x = event.x
            self.popup.y = event.y

        def stop_move(event):
            self.popup.x = None
            self.popup.y = None

        def do_move(event):
            if hasattr(self.popup, 'x') and self.popup.x is not None and self.popup.y is not None:
                deltax = event.x - self.popup.x
                deltay = event.y - self.popup.y
                x = self.popup.winfo_x() + deltax
                y = self.popup.winfo_y() + deltay
                self.popup.geometry(f"+{x}+{y}")

        title_frame.bind("<Button-1>", start_move)
        title_frame.bind("<ButtonRelease-1>", stop_move)
        title_frame.bind("<B1-Motion>", do_move)
        title_label.bind("<Button-1>", start_move)
        title_label.bind("<ButtonRelease-1>", stop_move)
        title_label.bind("<B1-Motion>", do_move)

        self.popup.mainloop()

    def cleanup_windows(self):
        """Clean up any existing windows"""
        try:
            if self.root and hasattr(self.root, 'winfo_exists') and self.root.winfo_exists():
                self.root.destroy()
        except:
            pass
        
        try:
            if self.popup and hasattr(self.popup, 'winfo_exists') and self.popup.winfo_exists():
                self.popup.destroy()
        except:
            pass
            
        try:
            if self.rec_popup and hasattr(self.rec_popup, 'winfo_exists') and self.rec_popup.winfo_exists():
                self.rec_popup.destroy()
        except:
            pass

    def quit_app(self):
        """Properly quit the application"""
        self.cleanup_windows()
        sys.exit(0)

    def start_normal_snipping(self):
        """Start normal snipping mode with Q&A"""
        self.mode = "normal"
        self.start_snipping()
    
    def start_fraud_detection(self):
        """Start fraud detection mode"""
        self.mode = "fraud_detection"
        self.start_snipping()
    
    def record_audio_only(self):
        """Placeholder for audio-only functionality"""
        print("Audio-only functionality not implemented yet")

    def start_snipping(self):
        """Start the screen snipping process."""
        if self.popup:
            self.popup.withdraw()  # Hide instead of destroy
            
        time.sleep(0.2)  # Small delay to ensure window is hidden
        
        self.root = tk.Toplevel() if self.popup else tk.Tk()
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-alpha', 0.3)
        self.root.configure(background='black')
        self.root.attributes('-topmost', True)

        self.canvas = tk.Canvas(self.root, cursor='cross', bg='gray', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.root.bind("<Escape>", self.cancel_snipping)
        
        mode_text = get_text("fraud_mode") if self.mode == "fraud_detection" else get_text("qa_mode")
        instruction = tk.Label(
            self.root,
            text=get_text("snip_instruction", mode=mode_text),
            font=("Segoe UI", 16),
            bg="black",
            fg="white"
        )
        instruction.pack(pady=10)

    def cancel_snipping(self, event):
        """Cancel snipping and return to main menu"""
        if self.root:
            self.root.destroy()
            self.root = None
        
        if self.popup:
            self.popup.deiconify()  # Show the hidden popup
        else:
            self.init_popup()

    def on_mouse_down(self, event):
        """Handle mouse down event for selection."""
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        
        if self.rect:
            self.canvas.delete(self.rect)
            
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline='red', width=3
        )

    def on_mouse_drag(self, event):
        """Handle mouse drag event for selection."""
        if self.start_x is not None and self.start_y is not None and self.rect:
            cur_x = self.canvas.canvasx(event.x)
            cur_y = self.canvas.canvasy(event.y)
            self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_mouse_up(self, event):
        """Handle mouse up event to complete selection."""
        if self.start_x is None or self.start_y is None:
            print(get_text("invalid_selection"))
            self.cancel_snipping(None)
            return
            
        end_x = self.canvas.canvasx(event.x)
        end_y = self.canvas.canvasy(event.y)
        
        if self.root:
            self.root.destroy()
            self.root = None

        x1 = int(min(self.start_x, end_x))
        y1 = int(min(self.start_y, end_y))
        x2 = int(max(self.start_x, end_x))
        y2 = int(max(self.start_y, end_y))

        if abs(x2 - x1) < 10 or abs(y2 - y1) < 10:
            print(get_text("selection_too_small"))
            if self.popup:
                self.popup.deiconify()
            else:
                self.init_popup()
            return

        try:
            self.screenshot = pyautogui.screenshot(region=(x1, y1, x2 - x1, y2 - y1))
            self.process_image()
        except Exception as e:
            print(get_text("screenshot_error", error=str(e)))
            if self.popup:
                self.popup.deiconify()
            else:
                self.init_popup()

    def process_image(self):
        """Process the screenshot with OCR and image labeling."""
        try:
            img_byte_arr = io.BytesIO()
            self.screenshot.save(img_byte_arr, format='PNG')
            self.screenshot_data = img_byte_arr.getvalue()

            client = vision.ImageAnnotatorClient()
            image = vision.Image(content=self.screenshot_data)

            response = client.document_text_detection(image=image)
            label_response = client.label_detection(image=image)

            if response.error.message:
                raise Exception(f"OCR Error: {response.error.message}")

            self.ocr_text = response.full_text_annotation.text.strip() if response.full_text_annotation else get_text("no_text_found")
            self.labels = ", ".join([label.description for label in label_response.label_annotations[:10]]) or get_text("no_labels_found")

            print(f"\n=== {get_text('ocr_extracted')} ===")
            print(self.ocr_text if self.ocr_text else get_text("no_text_found"))
            print(f"\n=== {get_text('image_labels')} ===")
            print(self.labels if self.labels else get_text("no_labels_found"))

            if self.mode == "fraud_detection":
                self.process_fraud_detection()
            else:
                self.init_record_popup()

        except Exception as e:
            print(get_text("error_processing_image", error=str(e)))
            if self.popup:
                self.popup.deiconify()
            else:
                self.init_popup()

    def process_fraud_detection(self):
        """Process image for fraud detection"""
        try:
            print(f"\n🛡️ {get_text('fraud_analysis')}")
            
            detection_result = detect_scam_fraud(
                self.labels,
                self.ocr_text,
                self.screenshot_data
            )
            
            print(f"\n=== {get_text('fraud_result')} ===\n{detection_result}")
            
            if "FRAUD DETECTED" in detection_result.upper():
                ScamDetectedPopup(detection_result)
                # After popup closes, return to main menu
                if self.popup:
                    self.popup.deiconify()
                else:
                    self.init_popup()
            else:
                safe_message = get_text("analysis_complete", result=detection_result)
                text_to_audio(safe_message)
                print(f"✅ {get_text('no_fraud_detected')}")
                # Return to main menu
                if self.popup:
                    self.popup.deiconify()
                else:
                    self.init_popup()
                
        except Exception as e:
            error_msg = get_text("error_fraud_detection", error=str(e))
            print(error_msg)
            text_to_audio(get_text("recording_error"))
            if self.popup:
                self.popup.deiconify()
            else:
                self.init_popup()

    def init_record_popup(self):
        """Initialize the modern recording popup window."""
        self.rec_popup = tk.Toplevel() if self.popup else tk.Tk()
        self.rec_popup.title(get_text("ask_question"))
        self.rec_popup.geometry("350x280")
        self.rec_popup.resizable(False, False)
        self.rec_popup.configure(bg="#f8f9fa")
        
        self.rec_popup.overrideredirect(True)
        
        self.rec_popup.update_idletasks()
        x = (self.rec_popup.winfo_screenwidth() // 2) - (350 // 2)
        y = (self.rec_popup.winfo_screenheight() // 2) - (280 // 2)
        self.rec_popup.geometry(f"350x280+{x}+{y}")
        
        # Add window shadow effect with border
        main_frame = tk.Frame(self.rec_popup, bg="white", relief="raised", bd=1)
        main_frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Title bar
        title_frame = tk.Frame(main_frame, bg="white", height=40)
        title_frame.pack(fill="x", padx=0, pady=0)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame, 
            text=get_text("ask_question"), 
            font=("Segoe UI", 14, "bold"), 
            bg="white", 
            fg="#2c3e50"
        )
        title_label.pack(side="left", padx=15, pady=10)
        
        close_btn = tk.Label(
            title_frame, 
            text="✕", 
            font=("Segoe UI", 16), 
            bg="white", 
            fg="#7f8c8d",
            cursor="hand2"
        )
        close_btn.pack(side="right", padx=15, pady=10)
        close_btn.bind("<Button-1>", lambda e: self.rec_popup.quit())
        close_btn.bind("<Enter>", lambda e: close_btn.config(fg="#e74c3c"))
        close_btn.bind("<Leave>", lambda e: close_btn.config(fg="#7f8c8d"))
        
        # Content frame
        content_frame = tk.Frame(main_frame, bg="white")
        content_frame.pack(fill="both", expand=True, padx=0, pady=(0, 20))
        
        # Instruction label
        tk.Label(
            content_frame, 
            text=get_text("record_instruction"), 
            font=("Segoe UI", 11), 
            bg="white", 
            fg="#6c757d"
        ).pack(pady=(15, 20))
        
        # Record button
        self.record_button_widget = ModernButton(
            content_frame,
            get_text("start_recording"),
            self.start_recording,
            "#28a745",  # Green
            "#1e7e34",  # Darker green on hover
            "🎤",
            width=300,
            height=50
        )
        
        # Stop button
        self.stop_button_widget = ModernButton(
            content_frame,
            get_text("stop_process"),
            self.stop_recording,
            "#ffc107",  # Yellow
            "#e0a800",  # Darker yellow on hover
            "⏹️",
            width=300,
            height=50
        )
        
        # Initially disable stop button
        self.stop_button_widget.frame.pack_forget()
        
        # Cancel button
        ModernButton(
            content_frame,
            get_text("cancel"),
            self.rec_popup.quit,
            "#dc3545",  # Red
            "#c82333",  # Darker red on hover
            "❌",
            width=300,
            height=45
        )
        
        # Make window draggable
        def start_move(event):
            self.rec_popup.x = event.x
            self.rec_popup.y = event.y

        def stop_move(event):
            self.rec_popup.x = None
            self.rec_popup.y = None

        def do_move(event):
            if self.rec_popup.x is not None and self.rec_popup.y is not None:
                deltax = event.x - self.rec_popup.x
                deltay = event.y - self.rec_popup.y
                x = self.rec_popup.winfo_x() + deltax
                y = self.rec_popup.winfo_y() + deltay
                self.rec_popup.geometry(f"+{x}+{y}")

        title_frame.bind("<Button-1>", start_move)
        title_frame.bind("<ButtonRelease-1>", stop_move)
        title_frame.bind("<B1-Motion>", do_move)
        title_label.bind("<Button-1>", start_move)
        title_label.bind("<ButtonRelease-1>", stop_move)
        title_label.bind("<B1-Motion>", do_move)

        self.rec_popup.mainloop()

    def start_recording(self):
        """Start audio recording."""
        self.recording = True
        
        # Hide record button and show stop button
        self.record_button_widget.frame.pack_forget()
        self.stop_button_widget.frame.pack(pady=8, padx=20, fill='x')
        
        # Update stop button to show recording status
        self.stop_button_widget.label.config(text=f"🔴 {get_text('recording')}")
        
        threading.Thread(target=self.record_audio, daemon=True).start()

    def stop_recording(self):
        """Stop audio recording and process the question."""
        self.recording = False
        self.stop_button_widget.label.config(text=get_text("processing"))
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
            print(f"\n=== {get_text('your_question')} ===\n{transcript}")

            if transcript.strip():
                response = generate_gemini_answer(
                    self.labels,
                    self.ocr_text,
                    transcript,
                    self.screenshot_data
                )
                print(f"\n=== {get_text('gemini_answer')} ===\n{response}")
                
                # Convert response to speech and play it
                text_to_audio(response)
                
            else:
                print(get_text("no_speech_detected"))
                # Play error message
                text_to_audio(get_text("no_speech_detected"))

            # Clean up
            try:
                os.unlink(self.audio_path)
            except:
                pass

        except Exception as e:
            print(get_text("error_processing_image", error=str(e)))
            # Play error message
            text_to_audio(get_text("recording_error"))

def parse_language_argument():
    """Parse language argument from command line"""
    global LANGUAGE
    
    if len(sys.argv) > 1:
        lang_arg = sys.argv[1].lower()
        
        # Language mapping
        lang_mapping = {
            "en": "en-US",
            "en-us": "en-US",
            "en-gb": "en-GB",
            "es": "es-ES",
            "fr": "fr-FR",
            "de": "de-DE",
            "it": "it-IT",
            "pt": "pt-BR",
            "ja": "ja-JP",
            "ko": "ko-KR",
            "zh": "zh-CN",
            "chinese": "zh-CN",
            "spanish": "es-ES",
            "french": "fr-FR",
            "german": "de-DE",
            "italian": "it-IT",
            "portuguese": "pt-BR",
            "japanese": "ja-JP",
            "korean": "ko-KR"
        }
        
        if lang_arg in lang_mapping:
            LANGUAGE = lang_mapping[lang_arg]
            print(get_text("language_set", language=LANGUAGE))
        else:
            print(get_text("unknown_language", language=lang_arg, default=LANGUAGE))
            print(get_text("supported_languages"))
    else:
        print(get_text("default_language", language=LANGUAGE))
        print(get_text("usage"))
        print(get_text("example"))

if __name__ == "__main__":
    print("🚀 Starting Modern Snipping Tool OCR + QnA with Fraud Detection...")
    print("Make sure you have set up Google Cloud credentials!")
    
    # Parse language argument
    parse_language_argument()
    
    # Start the application
    SnippingToolOCR()