#!/usr/bin/env python3
# ==============================================================================
# GitHub Repository & Volledige Instructies (README.md):
# https://github.com/leffuns/trends-in-ai-labo-4/labo4-multimodaleAI.py
#
# Snelstart:
# 1. pip install google-genai pydantic requests pillow python-dotenv edge-tts gTTS
# 2. Maak een .env bestand aan met: GEMINI_API_KEY=jouw_api_key
# 3. Genereer de MP3-vragen: python generate_audio_questions.py
# 4. Start het experiment:   python labo4-multimodaleAI.py
# ==============================================================================
"""
Trends in AI - Hoofdstuk 3 Lab: Multimodale AI voor Beeldbeschrijving & VQA
Bestandsnaam: labo4-multimodaleAI.py

Dit script vergelijkt een losgekoppelde (Cascaded) multimodale pijplijn met een
directe (Native End-to-End) multimodale architectuur op basis van de officiële
google-genai SDK en 5 vaste MS COCO 2017 validatie-experimenten.
"""

import io
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import APIError
from PIL import Image
from pydantic import BaseModel, Field

# ====================================================================
# CONFIGURATIE & CONSTANTEN
# ====================================================================

MODEL_FLASH = "gemini-2.5-flash"
MODEL_PRO = "gemini-2.5-pro"  # Wordt gebruikt in Module 4 met automatische fallback naar MODEL_FLASH
USE_PRO_FOR_NATIVE = True

SYSTEM_INSTRUCTION = (
    "Je bent een wetenschappelijke multimodale AI-assistent. "
    "Antwoord altijd in het Nederlands, wees feitelijk, analytisch en baseer "
    "visuele observaties uitsluitend op wat daadwerkelijk zichtbaar is."
)

EXPERIMENTS: List[Dict[str, str]] = [
    {
        "id": "exp1",
        "title": "Experiment 1: Baseline Objectdetectie & Tellen (Katten & Remotes)",
        "coco_id": "000000039769",
        "coco_url": "http://images.cocodataset.org/val2017/000000039769.jpg",
        "image_file": "experiments/exp1.jpg",
        "audio_file": "experiments/exp1.mp3",
        "focus": "Basisintegratie van spraakvraag en beeldbeschrijving onder ideale condities.",
    },
    {
        "id": "exp2",
        "title": "Experiment 2: Akoestische Stress-test /Ruis & Oriëntatie (Bruine Beer)",
        "coco_id": "000000000285",
        "coco_url": "http://images.cocodataset.org/val2017/000000000285.jpg",
        "image_file": "experiments/exp2.jpg",
        "audio_file": "experiments/exp2.mp3",
        "focus": "Impact van snelle/gemompelde spraak of achtergrondruis op spraakherkenning versus native audio-beeld begrip.",
    },
    {
        "id": "exp3",
        "title": "Experiment 3: Visuele Complexiteit & Occlusie (Drukke Woonkamer)",
        "coco_id": "000000000139",
        "coco_url": "http://images.cocodataset.org/val2017/000000000139.jpg",
        "image_file": "experiments/exp3.jpg",
        "audio_file": "experiments/exp3.mp3",
        "focus": "Beperkingen van beeldanalyse bij overlappende objecten, kleine details en exact tellen.",
    },
    {
        "id": "exp4",
        "title": "Experiment 4: Actie- en Interactieherkenning (Honkbalwedstrijd)",
        "coco_id": "000000000872",
        "coco_url": "http://images.cocodataset.org/val2017/000000000872.jpg",
        "image_file": "experiments/exp4.jpg",
        "audio_file": "experiments/exp4.mp3",
        "focus": "Dynamische relaties tussen personen, kleding en acties interpreteren op basis van een gesproken vraag.",
    },
    {
        "id": "exp5",
        "title": "Experiment 5: Hallucinatie- & Strikvraag-test (Teddyberen)",
        "coco_id": "000000000776",
        "coco_url": "http://images.cocodataset.org/val2017/000000000776.jpg",
        "image_file": "experiments/exp5.jpg",
        "audio_file": "experiments/exp5.mp3",
        "focus": "Onderzoeken of het model hallucineert wanneer de gesproken vraag verwijst naar een object dat niet in de afbeelding aanwezig is.",
    },
]

# Standaard dry-run vragen voor wanneer een .mp3 bestand nog niet op schijf staat
DRY_RUN_FALLBACK_QUESTIONS: Dict[str, str] = {
    "exp1": "Hoeveel katten en hoeveel afstandsbedieningen zijn er zichtbaar op de roze deken?",
    "exp2": "In welke richting kijkt de bruine beer en wat bevindt zich op de achtergrond?",
    "exp3": "Hoeveel stoelen zijn er zichtbaar in deze woonkamer en staat er een televisie in de ruimte?",
    "exp4": "Welke actie voert de honkbalspeler uit en welke kledingkleuren dragen de spelers op het veld?",
    "exp5": "Welke kleur heeft de voetbal die tussen de drie teddyberen ligt?",
}


# ====================================================================
# PYDANTIC SCHEMAS VOOR STRUCTURED OUTPUTS
# ====================================================================


class ImageAnalysisResult(BaseModel):
    algemene_beschrijving: str = Field(
        description="Uitgebreide, objectieve Nederlandse beschrijving van de afbeelding."
    )
    gedetecteerde_objecten: List[str] = Field(
        description="Lijst van de belangrijkste zichtbare objecten (inclusief aantallen indien relevant)."
    )
    ruimtelijke_context: str = Field(
        description="Beschrijving van de setting, compositie en onderlinge positie van objecten."
    )


class AudioTranscriptionResult(BaseModel):
    letterlijke_transcriptie: str = Field(
        description="De exacte tekstuele transcriptie van de gesproken audio-opname."
    )
    geschatte_verstaanbaarheid: str = Field(
        description="Beoordeling van de audiokwaliteit, bijv. 'Hoog', 'Gemiddeld', of 'Laag - ruis/gemompel'."
    )
    akoestische_opmerkingen: str = Field(
        description="Opmerkingen over achtergrondgeluid, spreektempo, articulatie of ambiguïteit."
    )


class CascadedVQAResult(BaseModel):
    antwoord_op_vraag: str = Field(
        description="Het antwoord op de getranscribeerde vraag op basis van de afbeelding en beeldbeschrijving."
    )
    gebruikte_visuele_elementen: List[str] = Field(
        description="De specifieke visuele elementen uit de afbeelding die zijn gebruikt om het antwoord te vormen."
    )
    mogelijke_transcriptie_frictie: str = Field(
        description="Analyse of de getranscribeerde tekst onlogische, vervormde of niet-bestaande woorden bevat t.o.v. het beeld."
    )


class NativeAndEvaluationResult(BaseModel):
    native_gehoorde_vraag: str = Field(
        description="Wat het model hoort in de audio wanneer het tegelijkertijd de visuele context van de afbeelding meeneemt."
    )
    native_antwoord: str = Field(
        description="Het directe multimodale antwoord op basis van gelijktijdige verwerking van audio en beeld."
    )
    foutbron_analyse: str = Field(
        description="Expliciete analyse: ontstonden eventuele fouten of onduidelijkheden door de spraakherkenning of door de interpretatie van de afbeelding?"
    )
    vergelijking_cascaded_vs_native: str = Field(
        description="Vergelijking van de kwaliteit en nauwkeurigheid tussen de losgekoppelde keten (Module 1-3) en directe multimodale fusie (Module 4)."
    )
    beperkingen_en_verbeterpunten: str = Field(
        description="Concrete beperkingen bij dit experiment en hoe het systeem verbeterd kan worden."
    )


class GlobalSynthesisResult(BaseModel):
    vraag_1_nauwkeurigheid_beschrijvingen: str = Field(
        description="Antwoord op kernvraag 1: Zijn de gegenereerde beschrijvingen nauwkeurig en passend bij de afbeeldingen?"
    )
    vraag_2_integratie_beeld_en_taal: str = Field(
        description="Antwoord op kernvraag 2: Hoe goed werkt de integratie tussen het beeldmodel en het taalmodel?"
    )
    vraag_3_uitdagingen_modaliteiten: str = Field(
        description="Antwoord op kernvraag 3: Welke uitdagingen kwamen naar voren bij het combineren van verschillende modaliteiten?"
    )
    vraag_4_mogelijke_verbeteringen: str = Field(
        description="Antwoord op kernvraag 4: Zijn er verbeteringen mogelijk voor de gegenereerde beschrijvingen?"
    )
    vraag_5_meerwaarde_beeld_en_audio: str = Field(
        description="Antwoord op kernvraag 5: Welke meerwaarde biedt het combineren van afbeeldingen en audio?"
    )
    vraag_6_fouten_spraak_vs_beeld: str = Field(
        description="Antwoord op kernvraag 6: Welke fouten ontstaan door spraakherkenning en welke door de interpretatie van de afbeelding?"
    )


# ====================================================================
# MULTIMODALE LAB PIJPLIJN KLASSE
# ====================================================================


class MultimodalLabPipeline:
    """Beheert het downloaden van data en het uitvoeren van de 4 multimodale modules."""

    def __init__(self) -> None:
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print(
                "[FOUT] GEMINI_API_KEY niet gevonden! Maak een .env bestand aan met GEMINI_API_KEY=jouw_sleutel",
                file=sys.stderr,
            )
            sys.exit(1)

        # Initialiseer de officiële google-genai Client
        self.client = genai.Client()
        self.experiments_dir = Path("experiments")
        self.experiments_dir.mkdir(parents=True, exist_ok=True)
        print(
            "[INFO] MultimodalLabPipeline succesvol geïnitialiseerd met google-genai SDK."
        )

    def ensure_image_downloaded(self, exp: Dict[str, str]) -> Image.Image:
        """Controleert of de MS COCO afbeelding lokaal staat en downloadt deze indien nodig."""
        image_path = Path(exp["image_file"])
        image_path.parent.mkdir(parents=True, exist_ok=True)

        if not image_path.exists():
            print(
                f"[INFO] Downloaden van MS COCO afbeelding ({exp['coco_id']}) via {exp['coco_url']} ..."
            )
            try:
                response = requests.get(exp["coco_url"], timeout=15)
                response.raise_for_status()
                image_path.write_bytes(response.content)
                print(f"[INFO] Afbeelding opgeslagen als: {image_path}")
            except requests.RequestException as exc:
                raise RuntimeError(
                    f"Kan afbeelding voor {exp['id']} niet downloaden van {exp['coco_url']}: {exc}"
                ) from exc
        else:
            print(f"[INFO] Afbeelding al aanwezig op schijf: {image_path}")

        # Open en converteer naar RGB zodat PIL Image altijd consistent is
        with Image.open(image_path) as img:
            return img.convert("RGB")

    def load_audio_bytes(self, exp: Dict[str, str]) -> Optional[bytes]:
        """Leest het .mp3 bestand in als ruwe bytes of geeft None terug met een duidelijke waarschuwing."""
        audio_path = Path(exp["audio_file"])
        if not audio_path.exists():
            print(
                f"[WAARSCHUWING] Audiobestand '{audio_path}' ontbreekt in 'experiments/'! "
                f"Experiment '{exp['id']}' wordt in DRY-RUN modus uitgevoerd voor het audiogedeelte."
            )
            return None

        audio_bytes = open(audio_path, "rb").read()
        if len(audio_bytes) == 0:
            print(
                f"[WAARSCHUWING] Audiobestand '{audio_path}' is leeg (0 bytes)! "
                f"Experiment '{exp['id']}' schakelt over naar DRY-RUN modus."
            )
            return None

        print(f"[INFO] Audiobestand geladen: {audio_path} ({len(audio_bytes)} bytes)")
        return audio_bytes

    def _parse_structured_response(self, response: Any, schema_cls: Any) -> Any:
        """Haalt veilig het geparsede Pydantic-object op uit de Gemini SDK response."""
        if getattr(response, "parsed", None) is not None:
            return response.parsed
        if getattr(response, "text", None):
            return schema_cls.model_validate_json(response.text)
        raise RuntimeError(f"Kon response niet parsen naar {schema_cls.__name__}.")

    # ----------------------------------------------------------------
    # MODULE 1: Geïsoleerde Beeldanalyse
    # ----------------------------------------------------------------
    def analyze_image_only(
        self, image: Image.Image, exp: Dict[str, str]
    ) -> Tuple[ImageAnalysisResult, float]:
        """Module 1: Analyseert uitsluitend de MS COCO afbeelding zonder audiocontext."""
        print(
            f"[INFO] [{exp['id']}] Start Module 1: Geïsoleerde Beeldanalyse ({MODEL_FLASH})..."
        )
        prompt = (
            "Analyseer deze afbeelding uiterst nauwkeurig zonder enige voorkennis van een vraag. "
            "Geef een gedetailleerde objectieve beschrijving in het Nederlands, een lijst van alle "
            "gedetecteerde hoofdobjecten (inclusief aantallen) en beschrijf de ruimtelijke context."
        )

        t0 = time.perf_counter()
        response = self.client.models.generate_content(
            model=MODEL_FLASH,
            contents=[image, prompt],
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                response_mime_type="application/json",
                response_schema=ImageAnalysisResult,
                temperature=0.1,
            ),
        )
        elapsed = time.perf_counter() - t0
        parsed_result: ImageAnalysisResult = self._parse_structured_response(
            response, ImageAnalysisResult
        )
        print(f"[INFO] [{exp['id']}] Module 1 voltooid in {elapsed:.2f}s.")
        return parsed_result, elapsed

    # ----------------------------------------------------------------
    # MODULE 2: Geïsoleerde Spraakherkenning (ASR)
    # ----------------------------------------------------------------
    def transcribe_audio_only(
        self, audio_bytes: Optional[bytes], exp: Dict[str, str]
    ) -> Tuple[AudioTranscriptionResult, float]:
        """Module 2: Transcribeert uitsluitend de .mp3 bytes zonder de afbeelding mee te sturen."""
        print(
            f"[INFO] [{exp['id']}] Start Module 2: Geïsoleerde Spraakherkenning / ASR ({MODEL_FLASH})..."
        )

        if audio_bytes is None:
            t0 = time.perf_counter()
            fallback_q = DRY_RUN_FALLBACK_QUESTIONS.get(
                exp["id"], "Beschrijf wat er op deze afbeelding te zien is."
            )
            dry_run_result = AudioTranscriptionResult(
                letterlijke_transcriptie=fallback_q,
                geschatte_verstaanbaarheid="Dry-Run (Geen MP3 aanwezig)",
                akoestische_opmerkingen=(
                    f"Bestand {exp['audio_file']} ontbrak tijdens uitvoering. "
                    "Deze standaard onderzoeksvraag is automatisch ingezet zodat de beeld- en evaluatiepijplijn volledig getest kan worden."
                ),
            )
            elapsed = time.perf_counter() - t0
            print(
                f"[INFO] [{exp['id']}] Module 2 (Dry-Run) voltooid in {elapsed:.4f}s."
            )
            return dry_run_result, elapsed

        audio_part = types.Part.from_bytes(data=audio_bytes, mime_type="audio/mp3")
        prompt = (
            "Luister naar dit audiobestand en fungeer puur als akoestische Speech-to-Text transcriber. "
            "Je hebt GEEN visuele context. Transcribeer letterlijk wat er wordt gezegd, beoordeel de "
            "verstaanbaarheid en noteer eventuele akoestische bijzonderheden zoals ruis, gemompel of versprekingen."
        )

        t0 = time.perf_counter()
        response = self.client.models.generate_content(
            model=MODEL_FLASH,
            contents=[audio_part, prompt],
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                response_mime_type="application/json",
                response_schema=AudioTranscriptionResult,
                temperature=0.1,
            ),
        )
        elapsed = time.perf_counter() - t0
        parsed_result: AudioTranscriptionResult = self._parse_structured_response(
            response, AudioTranscriptionResult
        )
        print(f"[INFO] [{exp['id']}] Module 2 voltooid in {elapsed:.2f}s.")
        return parsed_result, elapsed

    # ----------------------------------------------------------------
    # MODULE 3: Gekoppelde / Cascaded Multimodale Integratie
    # ----------------------------------------------------------------
    def run_cascaded_vqa(
        self,
        image: Image.Image,
        img_res: ImageAnalysisResult,
        aud_res: AudioTranscriptionResult,
        exp: Dict[str, str],
    ) -> Tuple[CascadedVQAResult, float]:
        """Module 3: Combineert de afbeelding met de tekstuele output van Module 1 en Module 2."""
        print(
            f"[INFO] [{exp['id']}] Start Module 3: Cascaded Multimodale Integratie ({MODEL_FLASH})..."
        )

        prompt = (
            f"Je voert een gekoppelde (cascaded) multimodale analyse uit voor '{exp['title']}'.\n\n"
            f"1. Eerdere geïsoleerde beeldbeschrijving (Module 1):\n"
            f"- Algemene beschrijving: {img_res.algemene_beschrijving}\n"
            f"- Gedetecteerde objecten: {', '.join(img_res.gedetecteerde_objecten)}\n"
            f"- Ruimtelijke context: {img_res.ruimtelijke_context}\n\n"
            f"2. Geïsoleerde tekstuele audiotranscriptie (Module 2):\n"
            f'- Letterlijke transcriptie: "{aud_res.letterlijke_transcriptie}"\n'
            f"- Geschatte verstaanbaarheid: {aud_res.geschatte_verstaanbaarheid}\n\n"
            "Opdracht:\n"
            "- Beantwoord de getranscribeerde vraag zo nauwkeurig mogelijk op basis van de afbeelding en de beschrijving.\n"
            "- Geef aan welke visuele elementen je hiervoor hebt gebruikt.\n"
            "- Analyseer of er frictie zit tussen de tekstuele transcriptie en wat er daadwerkelijk op de afbeelding te zien is "
            "(bijvoorbeeld door een ASR-transcriptiefout of een strikvraag over een niet-bestaand object)."
        )

        t0 = time.perf_counter()
        response = self.client.models.generate_content(
            model=MODEL_FLASH,
            contents=[image, prompt],
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                response_mime_type="application/json",
                response_schema=CascadedVQAResult,
                temperature=0.1,
            ),
        )
        elapsed = time.perf_counter() - t0
        parsed_result: CascadedVQAResult = self._parse_structured_response(
            response, CascadedVQAResult
        )
        print(f"[INFO] [{exp['id']}] Module 3 voltooid in {elapsed:.2f}s.")
        return parsed_result, elapsed

    # ----------------------------------------------------------------
    # MODULE 4: Native End-to-End Multimodale Integratie & Evaluatie
    # ----------------------------------------------------------------
    def run_native_multimodal_and_evaluate(
        self,
        image: Image.Image,
        audio_bytes: Optional[bytes],
        img_res: ImageAnalysisResult,
        aud_res: AudioTranscriptionResult,
        cas_res: CascadedVQAResult,
        exp: Dict[str, str],
    ) -> Tuple[NativeAndEvaluationResult, float, str]:
        """
        Module 4: Verwerkt afbeelding EN ruwe audio tegelijk in één multimodale prompt
        en evalueert het verschil tussen Cascaded en Native verwerking.
        """
        target_model = MODEL_PRO if USE_PRO_FOR_NATIVE else MODEL_FLASH
        print(
            f"[INFO] [{exp['id']}] Start Module 4: Native End-to-End Multimodale Fusie & Evaluatie ({target_model})..."
        )

        comparison_context = (
            f"Experiment: {exp['title']}\n"
            f"Onderzoeksfocus: {exp['focus']}\n\n"
            "Ter vergelijking zijn hier de resultaten uit de losgekoppelde (Cascaded) pijplijn:\n"
            f"- Module 1 (Alleen Beeld): {img_res.algemene_beschrijving} | Objecten: {', '.join(img_res.gedetecteerde_objecten)}\n"
            f'- Module 2 (Alleen Audio ASR): Transcriptie="{aud_res.letterlijke_transcriptie}" '
            f"(Verstaanbaarheid: {aud_res.geschatte_verstaanbaarheid}, Opmerkingen: {aud_res.akoestische_opmerkingen})\n"
            f"- Module 3 (Cascaded Antwoord): {cas_res.antwoord_op_vraag} "
            f"(Frictie-analyse: {cas_res.mogelijke_transcriptie_frictie})\n\n"
        )

        if audio_bytes is not None:
            audio_part = types.Part.from_bytes(data=audio_bytes, mime_type="audio/mp3")
            prompt = (
                comparison_context
                + "Opdracht voor Native End-to-End Multimodale Analyse:\n"
                "1. Beluister de bijgevoegde ruwe audio TERWIJL je direct naar de afbeelding kijkt. "
                "Formuleer wat de werkelijke gesproken vraag is wanneer je visuele context gebruikt om eventuele akoestische ruis of homofonen op te lossen.\n"
                "2. Geef het directe multimodale antwoord op de vraag op basis van het beeld.\n"
                "3. Voer een foutbron-analyse uit: ontstonden eventuele fouten of onduidelijkheden door de spraakherkenning (ASR) of door de visuele beeldinterpretatie?\n"
                "4. Vergelijk de Cascaded aanpak (Module 1-3) met deze Native End-to-End aanpak (Module 4).\n"
                "5. Benoem de specifieke beperkingen en verbeterpunten voor dit experiment."
            )
            contents_payload: List[Any] = [image, audio_part, prompt]
        else:
            prompt = (
                comparison_context
                + "LET OP: Het fysieke MP3-bestand ontbrak op schijf (Dry-Run modus). "
                f'Ga voor deze evaluatie uit van de gesimuleerde vraag: "{aud_res.letterlijke_transcriptie}".\n'
                "1. Beschrijf hoe een Native End-to-End model deze vraag samen met de afbeelding verwerkt.\n"
                "2. Geef het directe antwoord op de vraag op basis van de afbeelding.\n"
                "3. Analyseer welke foutbronnen (spraakherkenning vs. beeldinterpretatie) bij dit type experiment en focus optreden.\n"
                "4. Vergelijk de theoretische en praktische werking van de Cascaded pijplijn met Native multimodale verwerking.\n"
                "5. Benoem de beperkingen en verbeterpunten voor dit experiment."
            )
            contents_payload = [image, prompt]

        t0 = time.perf_counter()
        used_model = target_model
        try:
            response = self.client.models.generate_content(
                model=target_model,
                contents=contents_payload,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    response_mime_type="application/json",
                    response_schema=NativeAndEvaluationResult,
                    temperature=0.1,
                ),
            )
        except APIError as api_err:
            if target_model != MODEL_FLASH:
                print(
                    f"[WAARSCHUWING] [{exp['id']}] API-fout bij {target_model} ({api_err}). "
                    f"Schakelt automatisch over naar fallback model {MODEL_FLASH}..."
                )
                used_model = MODEL_FLASH
                response = self.client.models.generate_content(
                    model=MODEL_FLASH,
                    contents=contents_payload,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                        response_mime_type="application/json",
                        response_schema=NativeAndEvaluationResult,
                        temperature=0.1,
                    ),
                )
            else:
                raise

        elapsed = time.perf_counter() - t0
        parsed_result: NativeAndEvaluationResult = self._parse_structured_response(
            response, NativeAndEvaluationResult
        )
        print(
            f"[INFO] [{exp['id']}] Module 4 voltooid in {elapsed:.2f}s (Model: {used_model})."
        )
        return parsed_result, elapsed, used_model

    # ----------------------------------------------------------------
    # OVERKOEPELENDE SYNTHESE VOOR DE 6 KERNVRAGEN
    # ----------------------------------------------------------------
    def generate_global_synthesis(
        self, all_results: List[Dict[str, Any]]
    ) -> GlobalSynthesisResult:
        """Genereert op basis van alle 5 experimenten een wetenschappelijke synthese voor de 6 kernvragen."""
        print(
            "[INFO] Genereren van overkoepelende synthese voor de 6 kernvragen van het labo..."
        )

        compact_summary = json.dumps(all_results, ensure_ascii=False, indent=2)
        prompt = (
            "Hieronder staan de volledige experimentele resultaten van 5 MS COCO 2017 experimenten "
            "waarin geïsoleerde beeldanalyse, geïsoleerde ASR, een Cascaded multimodale pijplijn en een "
            "Native End-to-End multimodale architectuur met elkaar zijn vergeleken:\n\n"
            f"{compact_summary}\n\n"
            "Schrijf een diepgaande, wetenschappelijk onderbouwde synthese voor het laboverslag die elk van de "
            "6 kernvragen uitvoerig beantwoordt met directe verwijzingen naar de bevindingen uit Experiment 1 t/m 5."
        )

        response = self.client.models.generate_content(
            model=MODEL_FLASH,
            contents=[prompt],
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                response_mime_type="application/json",
                response_schema=GlobalSynthesisResult,
                temperature=0.1,
            ),
        )
        parsed_synthesis: GlobalSynthesisResult = self._parse_structured_response(
            response, GlobalSynthesisResult
        )
        print("[INFO] Overkoepelende synthese succesvol gegenereerd.")
        return parsed_synthesis


# ====================================================================
# RAPPORTAGE GENERATOR (JSON & MARKDOWN)
# ====================================================================


def build_markdown_report(
    results: List[Dict[str, Any]], synthesis: GlobalSynthesisResult
) -> str:
    """Bouwt het volledige Nederlandstalige Markdown-verslag op voor inlevering op Digitap."""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines: List[str] = [
        "# Laboverslag Hoofdstuk 3: Multimodale AI voor Beeldbeschrijving & VQA",
        "",
        f"**Gegenereerd op:** {now_str}  ",
        "**SDK & Architectuur:** Officiële `google-genai` SDK (`gemini-2.5-flash` & `gemini-2.5-pro`)  ",
        "**Dataset:** MS COCO 2017 Validation Set (5 gecontroleerde experimenten)  ",
        "",
        "---",
        "",
        "## 1. Samenvattende Vergelijkingstabel",
        "",
        "| Exp ID | COCO ID | Audio Status | Verstaanbaarheid (Mod 2) | Tijd Mod 1 (Beeld) | Tijd Mod 2 (ASR) | Tijd Mod 3 (Cascaded) | Tijd Mod 4 (Native) | Totaal |",
        "| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |",
    ]

    for item in results:
        t1 = item["timings_seconds"]["module_1_image_only"]
        t2 = item["timings_seconds"]["module_2_audio_only"]
        t3 = item["timings_seconds"]["module_3_cascaded_vqa"]
        t4 = item["timings_seconds"]["module_4_native_multimodal"]
        t_tot = item["timings_seconds"]["total_experiment"]
        audio_status = (
            "Aanwezig (MP3)" if item["audio_present"] else "Dry-Run (Simulatie)"
        )
        verstaanbaarheid = item["module_2_audio_only"]["geschatte_verstaanbaarheid"]

        lines.append(
            f"| **{item['id']}** | `{item['coco_id']}` | {audio_status} | {verstaanbaarheid} | "
            f"{t1:.2f}s | {t2:.2f}s | {t3:.2f}s | {t4:.2f}s | **{t_tot:.2f}s** |"
        )

    lines.extend(["", "---", "", "## 2. Gedetailleerde Analyse per Experiment", ""])

    for item in results:
        m1 = item["module_1_image_only"]
        m2 = item["module_2_audio_only"]
        m3 = item["module_3_cascaded_vqa"]
        m4 = item["module_4_native_multimodal"]
        t = item["timings_seconds"]

        objecten_str = ", ".join(m1["gedetecteerde_objecten"])
        visuele_elem_str = ", ".join(m3["gebruikte_visuele_elementen"])

        lines.extend(
            [
                f"### {item['title']}",
                "",
                f"- **MS COCO ID:** `{item['coco_id']}`",
                f"- **Lokale Afbeelding:** `{item['image_file']}`",
                f"- **COCO Bron-URL:** [{item['coco_url']}]({item['coco_url']})",
                f"- **Audiobestand:** `{item['audio_file']}` ({'Fysiek MP3-bestand geladen' if item['audio_present'] else 'Dry-Run fallback gebruikt'})",
                f"- **Onderzoeksfocus:** *{item['focus']}*",
                "",
                f"#### Resultaat Module 1: Geïsoleerde Beeldanalyse (`{MODEL_FLASH}` — {t['module_1_image_only']:.2f}s)",
                f"- **Algemene beschrijving:** {m1['algemene_beschrijving']}",
                f"- **Gedetecteerde hoofdobjecten:** {objecten_str}",
                f"- **Ruimtelijke context:** {m1['ruimtelijke_context']}",
                "",
                f"#### Resultaat Module 2: Geïsoleerde Audio-transcriptie / ASR (`{MODEL_FLASH}` — {t['module_2_audio_only']:.2f}s)",
                f"- **Letterlijke transcriptie:** *\"{m2['letterlijke_transcriptie']}\"*",
                f"- **Geschatte verstaanbaarheid:** {m2['geschatte_verstaanbaarheid']}",
                f"- **Akoestische opmerkingen:** {m2['akoestische_opmerkingen']}",
                "",
                f"#### Resultaat Module 3: Gekoppelde / Cascaded Integratie (`{MODEL_FLASH}` — {t['module_3_cascaded_vqa']:.2f}s)",
                f"- **Antwoord op vraag (Tekst + Beeld):** {m3['antwoord_op_vraag']}",
                f"- **Gebruikte visuele elementen:** {visuele_elem_str}",
                f"- **Mogelijke transcriptie-frictie:** {m3['mogelijke_transcriptie_frictie']}",
                "",
                f"#### Resultaat Module 4: Native Multimodaal Antwoord & Evaluatie (`{item['module_4_model_used']}` — {t['module_4_native_multimodal']:.2f}s)",
                f"- **Native gehoorde vraag (Audio + Beeld samen):** *\"{m4['native_gehoorde_vraag']}\"*",
                f"- **Native multimodaal antwoord:** {m4['native_antwoord']}",
                f"- **Vergelijking Cascaded vs. Native:** {m4['vergelijking_cascaded_vs_native']}",
                "",
                "#### Foutanalyse (Spraakherkenning vs. Beeldinterpretatie)",
                f"- **Foutbron-analyse:** {m4['foutbron_analyse']}",
                f"- **Beperkingen en verbeterpunten:** {m4['beperkingen_en_verbeterpunten']}",
                "",
                "---",
                "",
            ]
        )

    lines.extend(
        [
            "## 3. Beantwoording Kernvragen voor Verkenning",
            "",
            "Op basis van de kwantitatieve tijdsmetingen en kwalitatieve vergelijkingen uit de vijf bovenstaande "
            "MS COCO 2017 experimenten worden de zes kernvragen van het labo hieronder beantwoord.",
            "",
            "### 1. Zijn de gegenereerde beschrijvingen nauwkeurig en passend bij de afbeeldingen?",
            synthesis.vraag_1_nauwkeurigheid_beschrijvingen,
            "",
            "### 2. Hoe goed werkt de integratie tussen het beeldmodel en het taalmodel?",
            synthesis.vraag_2_integratie_beeld_en_taal,
            "",
            "### 3. Welke uitdagingen kwamen naar voren bij het combineren van verschillende modaliteiten?",
            synthesis.vraag_3_uitdagingen_modaliteiten,
            "",
            "### 4. Zijn er verbeteringen mogelijk voor de gegenereerde beschrijvingen?",
            synthesis.vraag_4_mogelijke_verbeteringen,
            "",
            "### 5. Welke meerwaarde biedt het combineren van afbeeldingen en audio?",
            synthesis.vraag_5_meerwaarde_beeld_en_audio,
            "",
            "### 6. Welke fouten ontstaan door spraakherkenning en welke door de interpretatie van de afbeelding?",
            synthesis.vraag_6_fouten_spraak_vs_beeld,
            "",
        ]
    )

    return "\n".join(lines)


# ====================================================================
# HOOFDPROGRAMMA (ENTRYPOINT)
# ====================================================================


def main() -> None:
    print("=" * 72)
    print("START MULTIMODAL COCO LAB PIJPLIJN (TRENDS IN AI - HOOFDSTUK 3)")
    print("=" * 72)

    pipeline = MultimodalLabPipeline()
    all_experiment_results: List[Dict[str, Any]] = []

    for exp in EXPERIMENTS:
        print("\n" + "-" * 72)
        print(f"[INFO] Start verwerking van {exp['title']} (COCO ID: {exp['coco_id']})")
        print("-" * 72)

        exp_start = time.perf_counter()

        # 1. Afbeelding controleren / downloaden en audio inladen
        pil_image = pipeline.ensure_image_downloaded(exp)
        audio_bytes = pipeline.load_audio_bytes(exp)

        # 2. Module 1: Geïsoleerde Beeldanalyse
        mod1_res, t_mod1 = pipeline.analyze_image_only(pil_image, exp)

        # 3. Module 2: Geïsoleerde Spraakherkenning (ASR)
        mod2_res, t_mod2 = pipeline.transcribe_audio_only(audio_bytes, exp)

        # 4. Module 3: Cascaded Multimodale Integratie
        mod3_res, t_mod3 = pipeline.run_cascaded_vqa(pil_image, mod1_res, mod2_res, exp)

        # 5. Module 4: Native End-to-End Multimodale Integratie & Evaluatie
        mod4_res, t_mod4, mod4_model = pipeline.run_native_multimodal_and_evaluate(
            pil_image, audio_bytes, mod1_res, mod2_res, mod3_res, exp
        )

        exp_total_time = time.perf_counter() - exp_start

        experiment_record: Dict[str, Any] = {
            "id": exp["id"],
            "title": exp["title"],
            "coco_id": exp["coco_id"],
            "coco_url": exp["coco_url"],
            "image_file": exp["image_file"],
            "audio_file": exp["audio_file"],
            "focus": exp["focus"],
            "audio_present": audio_bytes is not None,
            "module_4_model_used": mod4_model,
            "timings_seconds": {
                "module_1_image_only": round(t_mod1, 4),
                "module_2_audio_only": round(t_mod2, 4),
                "module_3_cascaded_vqa": round(t_mod3, 4),
                "module_4_native_multimodal": round(t_mod4, 4),
                "total_experiment": round(exp_total_time, 4),
            },
            "module_1_image_only": mod1_res.model_dump(),
            "module_2_audio_only": mod2_res.model_dump(),
            "module_3_cascaded_vqa": mod3_res.model_dump(),
            "module_4_native_multimodal": mod4_res.model_dump(),
        }
        all_experiment_results.append(experiment_record)

    # Genereer overkoepelende synthese voor de 6 kernvragen
    print("\n" + "-" * 72)
    synthesis_res = pipeline.generate_global_synthesis(all_experiment_results)

    # 1. Opslaan van resultaten_data.json
    json_output_path = Path("resultaten_data.json")
    full_json_payload = {
        "generated_at": datetime.now().isoformat(),
        "sdk": "google-genai",
        "experiments": all_experiment_results,
        "global_synthesis": synthesis_res.model_dump(),
    }
    json_output_path.write_text(
        json.dumps(full_json_payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(
        f"[INFO] Ruwe gestructureerde data opgeslagen in: {json_output_path.resolve()}"
    )

    # 2. Opslaan van resultaten_bespreking.md
    md_output_path = Path("resultaten_bespreking.md")
    markdown_content = build_markdown_report(all_experiment_results, synthesis_res)
    md_output_path.write_text(markdown_content, encoding="utf-8")
    print(f"[INFO] Volledig Markdown-verslag opgeslagen in: {md_output_path.resolve()}")

    print("=" * 72)
    print("[INFO] ALLE 5 EXPERIMENTEN EN RAPPORTAGES ZIJN SUCCESVOL AFGEROND!")
    print("=" * 72)


if __name__ == "__main__":
    main()
