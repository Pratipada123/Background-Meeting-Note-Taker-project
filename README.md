# MinuteMate – Background Meeting Note Taker 📝🎙️

MinuteMate is a Flask-based AI tool that records, transcribes, and summarizes your meetings in the background. It extracts action items and reminders using Whisper and spaCy — turning your spoken meetings into structured, actionable notes.

## 🚀 Features

- 🎤 **Voice Recording**: Starts/stops background audio recording.
- 🧠 **Transcription**: Converts speech to text using the `faster-whisper` model.
- ✍️ **Summarization**: Summarizes key points using spaCy NLP.
- ✅ **Action Items**: Extracts actionable tasks from transcribed text.
- ⏰ **Reminders**: Detects and highlights date/time expressions.
- 🌐 **API Endpoints**: Control everything via RESTful endpoints.

## 🧰 Tech Stack

- Python, Flask
- PyAudio, Wave
- Faster-Whisper (Speech-to-Text)
- spaCy (NLP)
- NumPy, Regex

## 📂 Project Structure

```
.
├── MinuteMate – Background Meeting Note Taker.py
├── audio/                   # Saved .wav files
└── static/index.html        # Optional frontend
```

## 📡 API Endpoints

| Endpoint         | Method | Description |
|------------------|--------|-------------|
| `/start`         | POST   | Starts live recording |
| `/stop`          | POST   | Stops recording |
| `/upload`        | POST   | Uploads a .wav file |
| `/status`        | GET    | Gets system status |
| `/minutes/<id>`  | GET    | Returns summary, actions, reminders |
| `/latest-id`     | GET    | Returns latest transcription ID |
| `/`              | GET    | Serves index.html (if available) |

## ⚙️ Setup Instructions

1. **Install dependencies**

```bash
pip install flask pyaudio numpy faster-whisper spacy
python -m spacy download en_core_web_sm
```

2. **Run the app**

```bash
python "MinuteMate – Background Meeting Note Taker.py"
```

3. **Use the endpoints**

You can use tools like Postman or cURL to interact with the API.

## 📌 Notes

- WhisperModel `"small"` is used with `"int8"` compute type for better accuracy and efficiency.
- Silence is automatically detected to stop recording.
- No frontend UI is bundled, but you can add one to `static/index.html`.

## 📄 License

MIT License

---

# 🧠 Prompt Log – MinuteMate AI Note Taker

## 🎯 Goal

To build an AI-powered tool that:
- Records meeting audio in the background.
- Transcribes speech to text using Whisper.
- Applies NLP for summarization and extracting tasks and reminders.
- Exposes the functionality through Flask API.

## ✅ Key Features Implemented

- Live audio recording with silence detection.
- Speech-to-text transcription via `faster-whisper`.
- Natural Language Processing (spaCy) to summarize and extract:
  - Key points
  - Action items (e.g., "We need to...", "I will...")
  - Dates/reminders (e.g., "5th Aug", "15/08/2025")

## 🧪 Development Notes

- Used `pyaudio` for low-latency recording.
- Transcription segments are joined into a single document.
- First 5 sentences used as a summary.
- Custom regex is used to identify action phrases and dates.
- Added Flask routes to control recording, uploading, and querying summaries.

## 🔄 Iterations

1. Basic Flask app with `/start` and `/stop`
2. Integrated WhisperModel for transcription
3. Added NLP-based summarizer and action extractor
4. Improved with unique IDs and session state
5. Extended API for `/upload`, `/minutes`, and `/latest-id`

## 🚀 Future Improvements

- Add speaker diarization
- Frontend dashboard for managing summaries
- Store data persistently (e.g., SQLite or MongoDB)
- Integrate with calendar/email APIs for reminders
