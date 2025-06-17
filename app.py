import gradio as gr
import asyncio
import edge_tts
import tempfile
import os

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
    ]
}

# 🔊 Async TTS
async def generate_audio(text, voice_id):
    output_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
    try:
        communicate = edge_tts.Communicate(text, voice=voice_id)
        await communicate.save(output_file)
        return output_file
    except Exception as e:
        print("Edge TTS Error:", str(e))
        return None

# 🎨 Custom CSS
custom_css = """
body { background-color: #000; color: #fff; font-family: 'Segoe UI', sans-serif; }
h1 { font-size: 36px !important; font-weight: bold !important; color: #c084fc !important; text-align: center; }
label, .block-title { font-weight: bold !important; color: #ffffff !important; }
textarea, input, select { background-color: #111 !important; color: #fff !important; border: 1px solid #444 !important; }
.gr-button { background-color: #c084fc !important; color: black !important; font-weight: bold; }
"""

# 💻 Interface
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
        return None, None, "❌ Voice or text missing."
    audio_path = await generate_audio(text, voice_id)
    if audio_path:
        return audio_path, audio_path, "✅ Done!"
    else:
        return None, None, "❌ Failed to generate audio."

with gr.Blocks(css=custom_css, title="💠 Viddyx Official Voice Generator") as app:
    gr.Markdown("# 💠 Viddyx Official Voice Generator")

    with gr.Row():
        language = gr.Dropdown(label="🌍 Choose Language", choices=list(language_voice_map.keys()), value="English US")
        voice = gr.Dropdown(label="🧑‍🎤 Choose Voice")

    sample_audio = gr.Audio(label="🔉 Voice Preview", type="filepath")
    gr.Button("🎧 Preview Voice").click(fn=play_sample, inputs=[voice, language], outputs=sample_audio)

    text_input = gr.Textbox(label="📝 Enter your text", placeholder="Type anything you want...", lines=5)

    with gr.Row():
        generate_btn = gr.Button("▶️ Generate")
        audio_output = gr.Audio(label="🔊 Output Audio", type="filepath")
        download_output = gr.File(label="⬇️ Download")

    with gr.Row():
        status = gr.Markdown("")  # Output status

    generate_btn.click(
        fn=wrapped_generate,
        inputs=[text_input, language, voice],
        outputs=[audio_output, download_output, status]
    )

    language.change(fn=update_voices, inputs=language, outputs=voice)

# 🔗 Launch
port = int(os.environ.get("PORT", 7860))
app.launch(server_name="0.0.0.0", server_port=port)
