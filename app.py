import gradio as gr
import asyncio
import edge_tts
import tempfile
import os
import datetime
from pydub import AudioSegment
from pydub.utils import mediainfo

# 🌍 Language and voice mappings (All Voices Restored)
language_voice_map = {
    "English US": [
        ("🧔 Guy", "en-US-GuyNeural"),
        ("🧔 Eric", "en-US-EricNeural"),
        ("🧔 Davis", "en-US-DavisNeural"),
        ("🧔 Christopher", "en-US-ChristopherNeural"),
        ("🧔 Andrew", "en-US-AndrewNeural"),
        ("🧔 Brian", "en-US-BrianNeural"),
        ("🧔 Roger", "en-US-RogerNeural"),
        ("🧔 Steffan", "en-US-SteffanNeural"),
        ("🧔 Tony", "en-US-TonyNeural"),
        ("🧔 Jacob", "en-US-JacobNeural"),
        ("🧔 Jason", "en-US-JasonNeural"),
        ("🧔 Henry", "en-US-HenryNeural"),
        ("🧔 Alan", "en-US-AlanNeural"),
        ("🧔 Walt", "en-US-WaltNeural"),
        ("🧔 Grant", "en-US-GrantNeural"),
        ("🧔 Brandon", "en-US-BrandonNeural"),
        ("🧔 Brandon Multi", "en-US-BrandonMultilingualNeural"),
        ("🧔 Andrew Multi", "en-US-AndrewMultilingualNeural"),
        ("🧔 Brian Multi", "en-US-BrianMultilingualNeural"),
        ("🧔 Tony Multi", "en-US-TonyMultilingualNeural")
    ],
    "English UK": [
        ("🧔 Ryan", "en-GB-RyanNeural"),
        ("👩 Sonia", "en-GB-SoniaNeural")
    ],
    "Urdu": [
        ("🧔 Asad", "ur-PK-AsadNeural"),
        ("👩 Uzma", "ur-PK-UzmaNeural")
    ],
    "Spanish": [
        ("🧔 Alvaro", "es-ES-AlvaroNeural"),
        ("👩 Elvira", "es-ES-ElviraNeural")
    ],
    "French": [
        ("🧔 Henri", "fr-FR-HenriNeural"),
        ("👩 Denise", "fr-FR-DeniseNeural")
    ],
    "German": [
        ("🧔 Conrad", "de-DE-ConradNeural"),
        ("👩 Katja", "de-DE-KatjaNeural")
    ],
    "Portuguese": [
        ("👩 Francisca", "pt-BR-FranciscaNeural"),
        ("👩 Raquel", "pt-PT-RaquelNeural"),
        ("🧔 Antonio", "pt-BR-AntonioNeural"),
        ("🧔 Duarte", "pt-PT-DuarteNeural")
    ]
}

# ✂️ Split text
def split_text(text, max_chars=4500):
    words = text.split()
    chunks, current = [], ""
    for w in words:
        if len(current) + len(w) + 1 <= max_chars:
            current += " " + w
        else:
            chunks.append(current.strip())
            current = w
    if current:
        chunks.append(current.strip())
    return chunks

# 🔊 Async TTS
async def generate_audio(text, voice_id):
    out_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
    try:
        communicate = edge_tts.Communicate(text, voice=voice_id)
        await communicate.save(out_file)
        return out_file
    except Exception as e:
        print("TTS Error:", str(e))
        return None

def update_voices(language):
    return gr.update(choices=[label for (label, _) in language_voice_map[language]], value=None)

async def play_sample(voice_label, language):
    voices = language_voice_map.get(language, [])
    voice_id = next((v for (label, v) in voices if label == voice_label), None)
    return await generate_audio("This is a voice sample", voice_id)

async def wrapped_generate(text, language, voice):
    voices = language_voice_map.get(language, [])
    voice_id = next((v for (label, v) in voices if label == voice), None)
    if not voice_id or not text:
        yield None, None, "❌ Voice or text missing."
        return

    chunks = split_text(text)
    temp_audio_files = []
    status_msgs = []

    for i, chunk in enumerate(chunks):
        status_msgs.append(f"🔄 Generating chunk {i+1}/{len(chunks)}...")
        yield None, None, "\n".join(status_msgs)
        output_path = await generate_audio(chunk, voice_id)
        await asyncio.sleep(0.1)
        if output_path:
            temp_audio_files.append(output_path)
        else:
            yield None, None, f"❌ Failed at chunk {i+1}"
            return

    final_audio = AudioSegment.empty()
    for file in temp_audio_files:
        final_audio += AudioSegment.from_file(file, format="mp3")

    merged_path = os.path.join(tempfile.gettempdir(), f"voice_output_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3")
    final_audio.export(merged_path, format="mp3")
    info = mediainfo(merged_path)
    duration_str = str(datetime.timedelta(seconds=int(float(info['duration']))))
    yield merged_path, merged_path, f"✅ Done! Total duration: {duration_str}"

# 🌈 Premium Gradient CSS
premium_css = """
body {
  background: linear-gradient(135deg, #0f0f0f, #1a1a1a);
  font-family: 'Poppins', sans-serif;
  color: #eaeaea;
}
h1 {
  font-size: 42px !important;
  font-weight: bold !important;
  background: linear-gradient(90deg, #f5d142, #c084fc, #9333ea);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-align: center;
  text-shadow: 0px 0px 15px rgba(192,132,252,0.3);
}
.gr-button {
  background: linear-gradient(90deg, #c084fc, #9333ea);
  border: none;
  color: white;
  font-weight: bold;
  border-radius: 12px;
  padding: 12px;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.gr-button:hover {
  transform: scale(1.05);
  box-shadow: 0px 4px 15px rgba(192,132,252,0.5);
}
textarea, input, select {
  background-color: #222 !important;
  color: #fff !important;
  border: 1px solid #555 !important;
  border-radius: 8px !important;
  padding: 10px !important;
}
"""

# 🖥️ Premium Layout
with gr.Blocks(css=premium_css, title="✨ Viddyx Premium Voice Generator") as app:
    gr.Markdown("# ✨ **Viddyx Premium Voice Generator**")

    with gr.Row():
        language = gr.Dropdown(label="🌍 Choose Language", choices=list(language_voice_map.keys()), value="English US")
        voice = gr.Dropdown(label="🧑‍🎤 Choose Voice")

    sample_audio = gr.Audio(label="🔊 Voice Preview", type="filepath")
    gr.Button("🎧 Preview Voice").click(fn=play_sample, inputs=[voice, language], outputs=sample_audio)

    text_input = gr.Textbox(label="📜 Enter your text", placeholder="Type or paste your script here...", lines=5)

    with gr.Row():
        generate_btn = gr.Button("▶️ Generate Audio")
        audio_output = gr.Audio(label="🔊 Output Audio", type="filepath")
        download_output = gr.File(label="⬇️ Download MP3")

    status = gr.Markdown("")

    generate_btn.click(
        fn=wrapped_generate,
        inputs=[text_input, language, voice],
        outputs=[audio_output, download_output, status]
    )

    language.change(fn=update_voices, inputs=language, outputs=voice)

# 🚀 Launch app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.launch(server_name="0.0.0.0", server_port=port, share=False)
