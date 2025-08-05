from flask import Flask, jsonify, request, send_from_directory
import threading, uuid, os, wave, pyaudio
import numpy as np
from faster_whisper import WhisperModel
import spacy
import re

# ----- Configs -----
app = Flask(__name__)
UPLOAD_FOLDER = "audio/"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

STATUS = "idle"
MINUTES = {}
RECORDING = False
current_id = None

# ----- Whisper & spaCy Init -----
model = WhisperModel("small", compute_type="int8")  # Use small for better accuracy
nlp = spacy.load("en_core_web_sm")

# ----- Audio Recording -----
FORMAT, CHANNELS, RATE = pyaudio.paInt16, 1, 16000
CHUNK, SILENCE_LIMIT = 1024, 30

def record_audio(output_filename="audio/output.wav"):
    global RECORDING
    RECORDING = True
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True, frames_per_buffer=CHUNK)
    print("🔴 Recording started...")
    frames, silent_seconds = [], 0

    while silent_seconds < SILENCE_LIMIT and RECORDING:
        data = stream.read(CHUNK)
        frames.append(data)
        if np.max(np.frombuffer(data, np.int16)) < 500:
            silent_seconds += CHUNK / RATE
        else:
            silent_seconds = 0

    print("🛑 Recording stopped.")
    stream.stop_stream(); stream.close(); audio.terminate()

    with wave.open(output_filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

# ----- Transcription + NLP -----
def transcribe_audio(audio_path):
    segments, _ = model.transcribe(audio_path)
    texts = []
    for idx, seg in enumerate(segments):
        print(f"Segment {idx}: [{seg.start:.2f}s - {seg.end:.2f}s] {repr(seg.text)}")
        texts.append(seg.text)
    return " ".join(texts)

def summarize_text(text):
    if not text.strip():
        return "(No text to summarize.)"
    doc = nlp(text)
    sents = list(doc.sents)
    if not sents:
        return text[:200] + "..." if len(text) > 200 else text
    return " ".join(str(s) for s in sents[:5])

def extract_action_items(text):
    return [
        s.strip() for s in re.split(r"[.!?]", text)
        if re.search(r"\b(will|need to|must|should|have to)\b", s, flags=re.I)
    ]

def extract_dates(text):
    return re.findall(
        r"\b(?:\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)|\d{1,2}/\d{1,2}(?:/\d{2,4})?)\b",
        text
    )

def process_audio_file(filepath):
    global STATUS, current_id
    STATUS = "processing"
    print(f"🔍 Processing file: {filepath}")
    text = transcribe_audio(filepath)
    print("📝 Transcription:", repr(text))
    summary = summarize_text(text)
    print("🧠 Summary:", repr(summary))
    actions = extract_action_items(text)
    print("✅ Actions:", actions)
    reminders = extract_dates(text)
    print("⏰ Reminders:", reminders)
    current_id = os.path.splitext(os.path.basename(filepath))[0]
    MINUTES[current_id] = {
        "summary": summary,
        "actions": actions,
        "reminders": reminders
    }
    STATUS = "idle"
    return jsonify({"status": "processed", "id": current_id})

# ----- Flask Endpoints -----
@app.route("/start", methods=["POST"])
def start():
    def run():
        global STATUS
        STATUS = "recording"
        filename = f"{UPLOAD_FOLDER}{uuid.uuid4()}.wav"
        record_audio(filename)
        process_audio_file(filename)
    threading.Thread(target=run).start()
    return jsonify({"status": "recording started"})

@app.route("/stop", methods=["POST"])
def stop():
    global RECORDING
    RECORDING = False
    return jsonify({"status": "stopping recording"})

@app.route("/upload", methods=["POST"])
def upload_audio():
    if 'file' not in request.files:
        return "No file uploaded", 400
    file = request.files['file']
    if file.filename == '':
        return "Empty filename", 400
    filename = f"{uuid.uuid4()}.wav"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    return process_audio_file(filepath)

@app.route("/status")
def status():
    return jsonify({"status": STATUS})

@app.route("/minutes/<id>")
def minutes(id):
    return jsonify(MINUTES.get(id, {}))

@app.route("/latest-id")
def latest_id():
    return jsonify({"id": current_id})

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

if __name__ == "__main__":
    app.run(debug=True)
