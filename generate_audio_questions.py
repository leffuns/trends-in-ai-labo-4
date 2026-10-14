#!/usr/bin/env python3
"""
Hulpscript: Automatische AI-Voice MP3 Generator voor Trends in AI (Hoofdstuk 3 Lab)
Bestandsnaam: generate_audio_questions.py

Dit script genereert automatisch de 5 Nederlandstalige/Vlaamse gesproken vragen
(exp1.mp3 t/m exp5.mp3) in de map 'experiments/' met behulp van Microsoft Neural
AI Voices (edge-tts), inclusief een automatische fallback naar Google TTS (gTTS).
Geen ffmpeg of externe systeembinary vereist!
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, List

try:
    import edge_tts

    HAS_EDGE_TTS = True
except ImportError:
    HAS_EDGE_TTS = False

try:
    from gtts import gTTS

    HAS_GTTS = True
except ImportError:
    HAS_GTTS = False


# Exact afgestemd op de 5 MS COCO 2017 afbeeldingen uit labo4-multimodaleAI.py
AUDIO_SPECS: List[Dict[str, str]] = [
    {
        "id": "exp1",
        "filename": "experiments/exp1.mp3",
        "coco_id": "000000039769",
        "voice": "nl-BE-DenaNeural",
        "rate": "+0%",
        "pitch": "+0Hz",
        "text": (
            "Hoeveel katten liggen er op de roze deken, "
            "en hoeveel afstandsbedieningen liggen er precies naast?"
        ),
        "doel": "Baseline: Helder ingesproken tel- en objectdetectievraag (2 katten, 2 remotes).",
    },
    {
        "id": "exp2",
        "filename": "experiments/exp2.mp3",
        "coco_id": "000000000285",
        "voice": "nl-NL-MaartenNeural",
        "rate": "+45%",
        "pitch": "-15Hz",
        "text": (
            "Eh... even heel snel kijken hoor, zit er nou een grote bruine peer of een bruine beer "
            "in het gras, en naar welke kant kijkt dit dier precies?"
        ),
        "doel": (
            "Akoestische stress-test: Hoog spreektempo (+45%), lagere toonhoogte en fonetische "
            "verwarring ('peer' vs 'beer') om het verschil tussen blinde ASR en visueel ondersteunde "
            "spraakherkenning aan te tonen."
        ),
    },
    {
        "id": "exp3",
        "filename": "experiments/exp3.mp3",
        "coco_id": "000000000139",
        "voice": "nl-BE-ArnaudNeural",
        "rate": "+0%",
        "pitch": "+0Hz",
        "text": (
            "Beschrijf deze drukke woonkamer. Hoeveel stoelen kun je in totaal tellen, "
            "en waar in de kamer staat de televisie?"
        ),
        "doel": "Visuele complexiteit & occlusie: Tellen van deels overlappende objecten in een drukke kamer.",
    },
    {
        "id": "exp4",
        "filename": "experiments/exp4.mp3",
        "coco_id": "000000000872",
        "voice": "nl-NL-FennaNeural",
        "rate": "+0%",
        "pitch": "+0Hz",
        "text": (
            "Welke sport spelen deze personen, welke actie voeren ze op dit moment uit "
            "en welke kleuren heeft hun sportkleding?"
        ),
        "doel": "Actie- en interactieherkenning: Dynamische relaties en kledingeigenschappen herkennen.",
    },
    {
        "id": "exp5",
        "filename": "experiments/exp5.mp3",
        "coco_id": "000000000776",
        "voice": "nl-BE-DenaNeural",
        "rate": "+0%",
        "pitch": "+0Hz",
        "text": (
            "Hoeveel teddyberen zitten er naast elkaar op de foto, "
            "en welke kleur heeft de voetbal die tussen de teddyberen in ligt?"
        ),
        "doel": (
            "Hallucinatie- & strikvraag-test: Vragen naar een niet-bestaand object (de voetbal) "
            "om te testen of het model hallucineert of de gebruiker corrigeert op basis van het beeld."
        ),
    },
]


async def generate_with_edge_tts(spec: Dict[str, str], output_path: Path) -> None:
    """Genereert een MP3-bestand met een Microsoft Neural AI stem via edge-tts."""
    communicate = edge_tts.Communicate(
        text=spec["text"],
        voice=spec["voice"],
        rate=spec["rate"],
        pitch=spec["pitch"],
    )
    await communicate.save(str(output_path))


def generate_with_gtts(spec: Dict[str, str], output_path: Path) -> None:
    """Fallback: Genereert een MP3-bestand met Google Text-to-Speech (gTTS)."""
    tts = gTTS(text=spec["text"], lang="nl", slow=False)
    tts.save(str(output_path))


async def main() -> None:
    print("=" * 72)
    print("START AI-VOICE MP3 GENERATOR VOOR labo4-multimodaleAI.py")
    print("=" * 72)

    if not HAS_EDGE_TTS and not HAS_GTTS:
        print(
            "[FOUT] Geen TTS-library gevonden! Installeer eerst edge-tts via:\n"
            "       pip install edge-tts gTTS",
            file=sys.stderr,
        )
        sys.exit(1)

    experiments_dir = Path("experiments")
    experiments_dir.mkdir(parents=True, exist_ok=True)

    for spec in AUDIO_SPECS:
        out_path = Path(spec["filename"])
        print(f"\n[INFO] [{spec['id']}] Genereren van: {out_path}")
        print(
            f"       Stem  : {spec['voice']} (Tempo: {spec['rate']}, Pitch: {spec['pitch']})"
        )
        print(f"       Vraag : \"{spec['text']}\"")
        print(f"       Focus : {spec['doel']}")

        if HAS_EDGE_TTS:
            try:
                await generate_with_edge_tts(spec, out_path)
                size_kb = out_path.stat().st_size / 1024
                print(
                    f"[OK]   Opgeslagen via Neural AI Voice (edge-tts): {out_path} ({size_kb:.1f} KB)"
                )
                continue
            except Exception as exc:
                print(
                    f"[WAARSCHUWING] edge-tts faalde ({exc}), probeert fallback gTTS..."
                )

        if HAS_GTTS:
            generate_with_gtts(spec, out_path)
            size_kb = out_path.stat().st_size / 1024
            print(
                f"[OK]   Opgeslagen via fallback (gTTS): {out_path} ({size_kb:.1f} KB)"
            )
        else:
            print(f"[FOUT] Kon {out_path} niet genereren.", file=sys.stderr)

    print("\n" + "=" * 72)
    print("[INFO] Alle 5 MP3-bestanden staan klaar in de map 'experiments/'!")
    print("[INFO] Je kunt nu direct 'python labo4-multimodaleAI.py' uitvoeren.")
    print("=" * 72)


if __name__ == "__main__":
    asyncio.run(main())
