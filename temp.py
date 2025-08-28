from google.cloud import vision
from google.cloud import speech
from google.cloud import translate_v2 as translate
import subprocess
import os
import io
import sys
import tkinter as tk
import pyautogui
from PIL import Image
# import ffmpeg 
# #this was downloaded on my system so it may be different

# Should I fix the ones with ()?
LANGUAGE_CODES = {
    "Abkhaz": "ab",
    "Acehnese": "ace",
    "Acholi": "ach",
    "Afrikaans": "af",
    "Albanian": "sq",
    "Alur": "alz",
    "Amharic": "am",
    "Arabic": "ar",
    "Armenian": "hy",
    "Assamese": "as",
    "Awadhi": "awa",
    "Aymara": "ay",
    "Azerbaijani": "az",
    "Balinese": "ban",
    "Bambara": "bm",
    "Bashkir": "ba",
    "Basque": "eu",
    "Batak Karo": "btx",
    "Batak Simalungun": "bts",
    "Batak Toba": "bbc",
    "Belarusian": "be",
    "Bemba": "bem",
    "Bengali": "bn",
    "Betawi": "bew",
    "Bhojpuri": "bho",
    "Bikol": "bik",
    "Bosnian": "bs",
    "Breton": "br",
    "Bulgarian": "bg",
    "Buryat": "bua",
    "Cantonese": "yue",
    "Catalan": "ca",
    "Cebuano": "ceb",
    "Chichewa (Nyanja)": "ny",
    "Chinese (Simplified)": "zh-CN",  # or "zh"
    "Chinese (Traditional)": "zh-TW",
    "Chuvash": "cv",
    "Corsican": "co",
    "Crimean Tatar": "crh",
    "Croatian": "hr",
    "Czech": "cs",
    "Danish": "da",
    "Dinka": "din",
    "Divehi": "dv",
    "Dogri": "doi",
    "Dombe": "dov",
    "Dutch": "nl",
    "Dzongkha": "dz",
    "English": "en",
    "Esperanto": "eo",
    "Estonian": "et",
    "Ewe": "ee",
    "Fijian": "fj",
    "Filipino (Tagalog)": "fil",  # or "tl"
    "Finnish": "fi",
    "French": "fr",
    "French (French)": "fr-FR",
    "French (Canadian)": "fr-CA",
    "Frisian": "fy",
    "Fulfulde": "ff",
    "Ga": "gaa",
    "Galician": "gl",
    "Ganda (Luganda)": "lg",
    "Georgian": "ka",
    "German": "de",
    "Greek": "el",
    "Guarani": "gn",
    "Gujarati": "gu",
    "Haitian Creole": "ht",
    "Hakha Chin": "cnh",
    "Hausa": "ha",
    "Hawaiian": "haw",
    "Hebrew": "he",  # or "iw"
    "Hiligaynon": "hil",
    "Hindi": "hi",
    "Hmong": "hmn",
    "Hungarian": "hu",
    "Hunsrik": "hrx",
    "Icelandic": "is",
    "Igbo": "ig",
    "Iloko": "ilo",
    "Indonesian": "id",
    "Irish": "ga",
    "Italian": "it",
    "Japanese": "ja",
    "Javanese": "jv",  # or "jw"
    "Kannada": "kn",
    "Kapampangan": "pam",
    "Kazakh": "kk",
    "Khmer": "km",
    "Kiga": "cgg",
    "Kinyarwanda": "rw",
    "Kituba": "ktu",
    "Konkani": "gom",
    "Korean": "ko",
    "Krio": "kri",
    "Kurdish (Kurmanji)": "ku",
    "Kurdish (Sorani)": "ckb",
    "Kyrgyz": "ky",
    "Lao": "lo",
    "Latgalian": "ltg",
    "Latin": "la",
    "Latvian": "lv",
    "Ligurian": "lij",
    "Limburgan": "li",
    "Lingala": "ln",
    "Lithuanian": "lt",
    "Lombard": "lmo",
    "Luo": "luo",
    "Luxembourgish": "lb",
    "Macedonian": "mk",
    "Maithili": "mai",
    "Makassar": "mak",
    "Malagasy": "mg",
    "Malay": "ms",
    "Malay (Jawi)": "ms-Arab",
    "Malayalam": "ml",
    "Maltese": "mt",
    "Maori": "mi",
    "Marathi": "mr",
    "Meadow Mari": "chm",
    "Meiteilon (Manipuri)": "mni-Mtei",
    "Minang": "min",
    "Mizo": "lus",
    "Mongolian": "mn",
    "Myanmar (Burmese)": "my",
    "Ndebele (South)": "nr",
    "Nepalbhasa (Newari)": "new",
    "Nepali": "ne",
    "Northern Sotho (Sepedi)": "nso",
    "Norwegian": "no",
    "Nuer": "nus",
    "Occitan": "oc",
    "Odia (Oriya)": "or",
    "Oromo": "om",
    "Pangasinan": "pag",
    "Papiamento": "pap",
    "Pashto": "ps",
    "Persian": "fa",
    "Polish": "pl",
    "Portuguese": "pt",
    "Portuguese (Portugal)": "pt-PT",
    "Portuguese (Brazil)": "pt-BR",
    "Punjabi": "pa",
    "Punjabi (Shahmukhi)": "pa-Arab",
    "Quechua": "qu",
    "Romani": "rom",
    "Romanian": "ro",
    "Rundi": "rn",
    "Russian": "ru",
    "Samoan": "sm",
    "Sango": "sg",
    "Sanskrit": "sa",
    "Scots Gaelic": "gd",
    "Serbian": "sr",
    "Sesotho": "st",
    "Seychellois Creole": "crs",
    "Shan": "shn",
    "Shona": "sn",
    "Sicilian": "scn",
    "Silesian": "szl",
    "Sindhi": "sd",
    "Sinhala (Sinhalese)": "si",
    "Slovak": "sk",
    "Slovenian": "sl",
    "Somali": "so",
    "Spanish": "es",
    "Sundanese": "su",
    "Swahili": "sw",
    "Swati": "ss",
    "Swedish": "sv",
    "Tajik": "tg",
    "Tamil": "ta",
    "Tatar": "tt",
    "Telugu": "te",
    "Tetum": "tet",
    "Thai": "th",
    "Tigrinya": "ti",
    "Tsonga": "ts",
    "Tswana": "tn",
    "Turkish": "tr",
    "Turkmen": "tk",
    "Twi (Akan)": "ak",
    "Ukrainian": "uk",
    "Urdu": "ur",
    "Uyghur": "ug",
    "Uzbek": "uz",
    "Vietnamese": "vi",
    "Welsh": "cy",
    "Xhosa": "xh",
    "Yiddish": "yi",
    "Yoruba": "yo",
    "Yucatec Maya": "yua",
    "Zulu": "zu"
}


# Vision
class SnippingToolOCR:
    def __init__(self):
        self.start_x = None
        self.start_y = None
        self.rect = None

        self.init_popup()

    def init_popup(self):
        self.popup = tk.Tk()
        self.popup.title("Snipping OCR Tool")

        tk.Label(self.popup, text="Choose an action:", font=("Arial", 14)).pack(pady=10)

        tk.Button(self.popup, text="🖼️ Snip Screen", command=self.start_snipping, width=20, font=("Arial", 12)).pack(pady=5)
        tk.Button(self.popup, text="❌ Cancel", command=self.popup.quit, width=20, font=("Arial", 12)).pack(pady=5)

        self.popup.mainloop()

    def start_snipping(self):
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

        self.root.mainloop()

    def on_mouse_down(self, event):
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline='red', width=2
        )

    def on_mouse_drag(self, event):
        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_mouse_up(self, event):
        end_x = self.canvas.canvasx(event.x)
        end_y = self.canvas.canvasy(event.y)
        self.root.destroy()

        x1 = int(min(self.start_x, end_x))
        y1 = int(min(self.start_y, end_y))
        x2 = int(max(self.start_x, end_x))
        y2 = int(max(self.start_y, end_y))

        screenshot = pyautogui.screenshot(region=(x1, y1, x2 - x1, y2 - y1))
        self.extract_text_from_image(screenshot)

    def extract_text_from_image(self, pil_image):
        img_byte_arr = io.BytesIO()
        pil_image.save(img_byte_arr, format='PNG')
        content = img_byte_arr.getvalue()

        client = vision.ImageAnnotatorClient()
        image = vision.Image(content=content)
        response = client.document_text_detection(image=image)

        if response.error.message:
            raise Exception(f"API error: {response.error.message}")

        print("\n=== Extracted Text ===\n")
        print(response.full_text_annotation.text.strip())

# Speech to Text
def translate_text(text, target_language="es"):
    translate_client = translate.Client()
    result = translate_client.translate(text, target_language=target_language)
    return result["translatedText"]

def convert_to_mono_16k(input_path):
    output_path = "converted_temp.wav"
    subprocess.run([
        "ffmpeg", "-y", "-i", input_path,
        "-ac", "1", "-ar", "16000",
        output_path
    ], check=True)
    return output_path

def transcribe_speech(audio_path):
    # Convert to mono 16kHz if necessary
    converted_path = convert_to_mono_16k(audio_path)

    client = speech.SpeechClient()

    with io.open(converted_path, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        language_code="en-US",
    )

    response = client.recognize(config=config, audio=audio)
    os.remove(converted_path)  # Clean up

    print("=== Transcription ===")
    for result in response.results:
        print(result.alternatives[0].transcript)

# Speech to Text Translation
# Translation helper
def translate_text(text, target_language_name="Spanish"):
    # Convert name like "Japanese" to code like "ja"
    target_language_code = LANGUAGE_CODES.get(target_language_name, "es")
    translate_client = translate.Client()
    result = translate_client.translate(text, target_language=target_language_code)
    return result["translatedText"]


# Speech-to-Text + Translation
def transcribe_and_translate(audio_path, target_language_name="Spanish"):
    converted_path = convert_to_mono_16k(audio_path)
    client = speech.SpeechClient()
    with io.open(converted_path, "rb") as audio_file:
        content = audio_file.read()
    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        language_code="en-US",
    )
    response = client.recognize(config=config, audio=audio)
    os.remove(converted_path)

    # Translate each transcript segment
    print(f"=== Transcription & Translation ({target_language_name}) ===")
    for result in response.results:
        transcript = result.alternatives[0].transcript
        translation = translate_text(transcript, target_language_name)
        print(f"Original: {transcript}")
        print(f"Translated: {translation}")

# Main
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python script.py [vision|speech|speech-translate] input_file [target_language]")
        print("Example: python script.py speech-translate my_audio.wav Japanese")
        sys.exit(1)

    model = sys.argv[1].lower()
    file_path = sys.argv[2]
    target_language_name = sys.argv[3] if len(sys.argv) > 3 else "Spanish"

    if model == "vision":
        SnippingToolOCR()
    elif model == "speech":
        transcribe_speech(file_path)
    elif model == "speech-translate":
        transcribe_and_translate(file_path, target_language_name)
    else:
        print(f"Unknown model: {model}. Choose from: vision, speech, speech-translate")
        sys.exit(1)