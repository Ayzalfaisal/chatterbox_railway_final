import asyncio
import edge_tts

async def list_voices():
    try:
        voices = await edge_tts.list_voices()
        with open("voices.txt", "w", encoding="utf-8") as f:
            for voice in voices:
                f.write(f"{voice['ShortName']} - {voice['Gender']} - {voice['Locale']}\n")
        print("✅ Voices saved in voices.txt")
    except Exception as e:
        print("❌ Error:", str(e))

asyncio.run(list_voices())
