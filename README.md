# Multimodale AI voor Beeldbeschrijving & VQA (MS COCO 2017)

**Vak:** Trends in AI — Hoofdstuk 3 Lab  
**Onderwerp:** Multimodale AI-agent voor beeldanalyse, spraakherkenning (ASR) en Visual Question Answering (VQA)  
**SDK & Modellen:** Officiële `google-genai` SDK (`gemini-2.5-flash` & `gemini-2.5-pro`), `Pydantic` (Structured Outputs), `edge-tts` (Neural AI Voices)  

---

## 📌 Overzicht van het Project

Deze applicatie onderzoekt de mogelijkheden, meerwaarde en beperkingen van multimodale AI door **5 gecontroleerde experimenten** uit te voeren op de **MS COCO 2017 validatiedataset**. 

Om de onderzoeksvragen uit het labo wetenschappelijk te beantwoorden, vergelijkt dit project twee multimodale architecturen met elkaar:
1. **Gekoppelde / Cascaded Pijplijn (Modulaire keten):**
   * **Module 1 (`analyze_image_only`):** Analyseert uitsluitend de afbeelding en genereert een objectieve Nederlandse beschrijving en objectenlijst.
   * **Module 2 (`transcribe_audio_only`):** Transcribeert uitsluitend het `.mp3` audiobestand naar tekst (Speech-to-Text) zonder visuele voorkennis.
   * **Module 3 (`run_cascaded_vqa`):** Combineert de afbeelding met de tekstuele transcriptie uit Module 2 en de beschrijving uit Module 1 om de vraag te beantwoorden.
2. **Native End-to-End Multimodale Pijplijn (Directe fusie):**
   * **Module 4 (`run_native_multimodal_and_evaluate`):** Verwerkt de MS COCO-afbeelding én de ruwe `.mp3` audio-bytes **gelijktijdig** in één multimodale prompt. Vervolgens evalueert het model of eventuele fouten zijn ontstaan door de spraakherkenning (ASR) of door de visuele beeldinterpretatie.

---

## 🧪 De 5 MS COCO 2017 Experimenten

Het script downloadt automatisch de 5 bijbehorende MS COCO-afbeeldingen en koppelt deze aan 5 gesproken Nederlandstalige/Vlaamse `.mp3`-vragen:

| Exp ID | MS COCO ID | Onderwerp | Gesproken Vraag (`.mp3`) | Onderzoeksfocus |
| :--- | :--- | :--- | :--- | :--- |
| **`exp1`** | `000000039769` | Katten & Remotes | *"Hoeveel katten liggen er op de roze deken, en hoeveel afstandsbedieningen liggen er precies naast?"* | **Baseline:** Objectdetectie en exact tellen onder ideale condities. |
| **`exp2`** | `000000000285` | Bruine Beer | *"Eh... even heel snel kijken hoor, zit er nou een grote bruine peer of een bruine beer in het gras, en naar welke kant kijkt dit dier precies?"* | **Akoestische Stress-test:** Hoog spreektempo (+45%) en klankverwarring (*peer* vs. *beer*) om blinde ASR te vergelijken met visueel ondersteunde spraakherkenning. |
| **`exp3`** | `000000000139` | Drukke Woonkamer | *"Beschrijf deze drukke woonkamer. Hoeveel stoelen kun je in totaal tellen, en waar in de kamer staat de televisie?"* | **Visuele Complexiteit & Occlusie:** Beperkingen van beeldanalyse bij overlappende objecten en kleine details. |
| **`exp4`** | `000000000872` | Honkbalwedstrijd | *"Welke sport spelen deze personen, welke actie voeren ze op dit moment uit en welke kleuren heeft hun sportkleding?"* | **Actie- & Interactieherkenning:** Dynamische relaties tussen personen, kleding en acties interpreteren. |
| **`exp5`** | `000000000776` | Drie Teddyberen | *"Hoeveel teddyberen zitten er naast elkaar op de foto, en welke kleur heeft de voetbal die tussen de teddyberen in ligt?"* | **Hallucinatie- & Strikvraag-test:** Testen of het model hallucineert wanneer de vraag verwijst naar een object (*voetbal*) dat niet op de foto staat. |

---

## 📂 Projectstructuur

```text
.
├── labo4-multimodaleAI.py        # Hoofdscript: voert de 4 modules en evaluaties uit
├── generate_audio_questions.py   # Hulpscript: genereert exp1.mp3 t/m exp5.mp3 met AI-stemmen
├── .env                          # Bevat de geheime GEMINI_API_KEY (niet mee-committen!)
├── README.md                     # Documentatie en instructies
├── experiments/                  # Wordt automatisch aangemaakt
│   ├── exp1.jpg t/m exp5.jpg     # Automatisch gedownloade MS COCO 2017 foto's
│   └── exp1.mp3 t/m exp5.mp3     # Gesproken audiovragen
├── resultaten_data.json          # Automatisch gegenereerde ruwe JSON-data & tijdsmetingen
└── resultaten_bespreking.md      # Automatisch gegenereerd eindverslag voor Digitap
```

---

## 🚀 Installatie & Uitvoering (Stappenplan)

### Stap 1: Repository clonen en Virtual Environment activeren
Open een terminal in VS Code en voer uit:

```bash
git clone https://github.com/leffuns/trends-in-ai-labo-4.git
cd multimodal-coco-lab

# Maak een virtual environment aan en activeer deze
python -m venv .venv

# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# macOS / Linux:
source .venv/bin/activate
```

### Stap 2: Vereiste Python-packages installeren
Installeer de officiële `google-genai` SDK en de ondersteunende libraries:

```bash
pip install google-genai pydantic requests pillow python-dotenv edge-tts gTTS
```

### Stap 3: API-sleutel instellen in `.env`
Maak in de hoofdmap van het project een bestand aan met de naam `.env` en voeg je Google Gemini API-sleutel toe:

```env
GEMINI_API_KEY=AIzaSyJouwEchteGeminiApiKeyHier
```

### Stap 4: De 5 MP3-audiovragen automatisch genereren
Voer het hulpscript uit om `exp1.mp3` t/m `exp5.mp3` met Vlaamse en Nederlandse Neural AI-stemmen aan te maken in de map `experiments/`:

```bash
python generate_audio_questions.py
```

*(Opmerking: Je kunt ook je eigen ingesproken `.mp3`-bestanden in de map `experiments/` plaatsen. Als een `.mp3`-bestand ontbreekt, crasht het hoofdscript niet maar voert het automatisch een veilige dry-run uit.)*

### Stap 5: De multimodale lab-pijplijn starten
Draai het hoofdscript om de MS COCO-afbeeldingen te downloaden, alle 4 de modules per experiment uit te voeren en de rapportages te genereren:

```bash
python labo4-multimodaleAI.py
```

---

## 📊 Gegenereerde Output (Deliverables)

Na afloop van `python labo4-multimodaleAI.py` worden twee bestanden automatisch opgeslagen in de hoofdmap:

1. **`resultaten_bespreking.md`**: Een volledig opgemaakt Nederlandstalig Markdown-verslag, direct klaar voor inlevering op Digitap. Bevat:
   * Een samenvattende vergelijkingstabel met uitvoeringsduur (latency) per module en verstaanbaarheid.
   * Per experiment (1 t/m 5) de gedetailleerde resultaten van Module 1, Module 2, Module 3 en Module 4 inclusief foutbron-analyse (spraakherkenning vs. beeldinterpretatie).
   * Een overkoepelende beantwoording van alle **6 kernvragen** uit het labo.
2. **`resultaten_data.json`**: Alle gestructureerde Pydantic-outputs en exacte tijdsmetingen (`time.perf_counter()`) in JSON-formaat voor verdere data-analyse.