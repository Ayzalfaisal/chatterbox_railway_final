import gradio as gr
import asyncio
import edge_tts
import tempfile
import os
import datetime
from pydub import AudioSegment
from pydub.utils import mediainfo

# 🌍 Language and voice mappings
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

# ✂️ Split text into smaller chunks
def split_text(text, max_chars=4500):
    words = text.split()
    chunks = []
    current_chunk = ""
    for word in words:
        if len(current_chunk) + len(word) + 1 <= max_chars:
            current_chunk += " " + word
        else:
            chunks.append(current_chunk.strip())
            current_chunk = word
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

# 🔊 Async TTS generation
async def generate_audio(text, voice_id):
    output_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
    try:
        communicate = edge_tts.Communicate(text, voice=voice_id)
        await communicate.save(output_file)
        return output_file
    except Exception as e:
        print("Edge TTS Error:", str(e))
        return None

# 📋 Update voices by language
def update_voices(language):
    return gr.update(choices=[label for (label, _) in language_voice_map[language]], value=None)

# 🔉 Play voice sample
async def play_sample(voice_label, language):
    voices = language_voice_map.get(language, [])
    voice_id = next((v for (label, v) in voices if label == voice_label), None)
    return await generate_audio("This is a voice sample", voice_id)

# 🔁 Full generation with chunking and merge
async def wrapped_generate(text, language, voice):
    voices = language_voice_map.get(language, [])
    voice_id = next((v for (label, v) in voices if label == voice), None)
    if not voice_id or not text:
        yield None, None, "❌ Voice or text missing."
        return

    chunks = split_text(text)
    total_chunks = len(chunks)
    temp_audio_files = []
    status_messages = []

    for i, chunk in enumerate(chunks):
        try:
            status_messages.append(f"🔄 Generating chunk {i+1}/{total_chunks}...")
            status_str = "\n".join(status_messages)
            yield None, None, status_str

            output_path = await generate_audio(chunk, voice_id)
            await asyncio.sleep(0.1)  # brief delay to prevent overload
            if output_path:
                temp_audio_files.append(output_path)
            else:
                yield None, None, f"❌ Failed at chunk {i+1}"
                return
        except Exception as e:
            yield None, None, f"❌ Error in chunk {i+1}: {str(e)}"
            return

    final_audio = AudioSegment.empty()
    for file in temp_audio_files:
        final_audio += AudioSegment.from_file(file, format="mp3")

    merged_path = os.path.join(tempfile.gettempdir(), f"voice_output_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3")
    final_audio.export(merged_path, format="mp3")

    info = mediainfo(merged_path)
    duration_sec = float(info['duration'])
    duration_str = str(datetime.timedelta(seconds=int(duration_sec)))
    final_status = f"✅ Done! Total duration: {duration_str}"

    yield merged_path, merged_path, final_status

# 💻 Premium UI with gradient heading
custom_css = """
body { background-color: #0e0e12; color: #fff; font-family: 'Segoe UI', sans-serif; }
h1 {
    font-size: 38px !important;
    font-weight: bold !important;
    text-align: center;
    background: linear-gradient(to right, #fbbf24, #a855f7, #ec4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
label, .block-title { font-weight: bold !important; color: #e5e5e5 !important; }
textarea, input, select {
    background-color: #1a1a1f !important;
    color: #fff !important;
    border: 1px solid #444 !important;
    border-radius: 6px !important;
}
.gr-button {
    background: linear-gradient(to right, #a855f7, #ec4899);
    color: #fff !important;
    font-weight: bold;
    border-radius: 8px !important;
}
"""

with gr.Blocks(css=custom_css, title="✨ Viddyx Premium Voice Generator") as app:
    gr.Markdown("# ✨ Viddyx Premium Voice Generator")

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

    with gr.Row():
        status = gr.Markdown("")

    generate_btn.click(
        fn=wrapped_generate,
        inputs=[text_input, language, voice],
        outputs=[audio_output, download_output, status]
    )

    language.change(fn=update_voices, inputs=language, outputs=voice)

# 🚀 Launch app
port = int(os.environ.get("PORT", 7860))
app.launch(server_name="0.0.0.0", server_port=port, share=True)
