# Laboverslag Hoofdstuk 3: Multimodale AI voor Beeldbeschrijving & VQA

**Gegenereerd op:** 2026-10-14 15:14:39  
**SDK & Architectuur:** Officiële `google-genai` SDK (`gemini-2.5-flash` & `gemini-2.5-pro`)  
**Dataset:** MS COCO 2017 Validation Set (5 gecontroleerde experimenten)  

---

## 1. Samenvattende Vergelijkingstabel

| Exp ID | COCO ID | Audio Status | Verstaanbaarheid (Mod 2) | Tijd Mod 1 (Beeld) | Tijd Mod 2 (ASR) | Tijd Mod 3 (Cascaded) | Tijd Mod 4 (Native) | Totaal |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **exp1** | `000000039769` | Aanwezig (MP3) | Hoog | 5.89s | 2.40s | 4.78s | 10.88s | **24.71s** |
| **exp2** | `000000000285` | Aanwezig (MP3) | Hoog | 3.57s | 3.17s | 5.12s | 12.11s | **24.81s** |
| **exp3** | `000000000139` | Aanwezig (MP3) | Hoog | 11.67s | 3.16s | 4.53s | 12.23s | **32.61s** |
| **exp4** | `000000000872` | Aanwezig (MP3) | Hoog | 6.22s | 2.52s | 6.29s | 9.91s | **25.83s** |
| **exp5** | `000000000776` | Aanwezig (MP3) | Hoog | 7.09s | 2.69s | 3.91s | 8.44s | **22.75s** |

---

## 2. Gedetailleerde Analyse per Experiment

### Experiment 1: Baseline Objectdetectie & Tellen (Katten & Remotes)

- **MS COCO ID:** `000000039769`
- **Lokale Afbeelding:** `experiments/exp1.jpg`
- **COCO Bron-URL:** [http://images.cocodataset.org/val2017/000000039769.jpg](http://images.cocodataset.org/val2017/000000039769.jpg)
- **Audiobestand:** `experiments/exp1.mp3` (Fysiek MP3-bestand geladen)
- **Onderzoeksfocus:** *Basisintegratie van spraakvraag en beeldbeschrijving onder ideale condities.*

#### Resultaat Module 1: Geïsoleerde Beeldanalyse (`gemini-2.5-flash` — 5.89s)
- **Algemene beschrijving:** De afbeelding toont twee slapende gestreepte katten die languit liggen op een felroze deken. Beide katten hebben een vacht met bruine, grijze en zwarte strepen, kenmerkend voor een cyperse kat. De kat aan de linkerkant ligt op zijn rug of zij, met zijn kop naar de linkerbovenhoek gericht en zijn lichaam naar beneden uitgestrekt. Deze kat draagt een lichtgroene halsband. De kat aan de rechterkant ligt op zijn buik of zij, met zijn kop naar de rechteronderhoek gericht en zijn lichaam naar boven uitgestrekt. Tussen de katten in, en naast hun koppen, liggen twee lichtgekleurde afstandsbedieningen. De achtergrond bestaat uit een effen roze textiel, waarschijnlijk een deken of plaid, die een groot deel van het beeldvlak vult. Aan de bovenrand van de afbeelding is een donkerder rood oppervlak zichtbaar, wat mogelijk een deel van een bank of fauteuil is.
- **Gedetecteerde hoofdobjecten:** 2 gestreepte katten, 2 afstandsbedieningen, 1 roze deken/plaid, 1 lichtgroene halsband
- **Ruimtelijke context:** De twee katten liggen centraal in de afbeelding, elk aan een zijde van het beeldvlak, met een lichte scheiding in het midden. De linkerkat ligt diagonaal van linksboven naar linksonder, terwijl de rechterkat diagonaal van rechtsboven naar rechtsonder ligt, waardoor ze een spiegelbeeldige, maar niet perfect symmetrische, compositie vormen. De afstandsbedieningen liggen respectievelijk naast de kop van elke kat, dicht bij de bovenrand van de roze deken. De roze deken bedekt het grootste deel van het oppervlak, met een donkerrood meubelstuk dat zichtbaar is aan de bovenrand, wat suggereert dat de deken over een bank of stoel is gedrapeerd.

#### Resultaat Module 2: Geïsoleerde Audio-transcriptie / ASR (`gemini-2.5-flash` — 2.40s)
- **Letterlijke transcriptie:** *"Hoeveel katten liggen er op de roze deken en hoeveel afstandsbedieningen liggen er precies naast?"*
- **Geschatte verstaanbaarheid:** Hoog
- **Akoestische opmerkingen:** Geen achtergrondgeluid, duidelijk spreektempo en articulatie.

#### Resultaat Module 3: Gekoppelde / Cascaded Integratie (`gemini-2.5-flash` — 4.78s)
- **Antwoord op vraag (Tekst + Beeld):** Er liggen twee katten op de roze deken en er liggen twee afstandsbedieningen precies naast de katten.
- **Gebruikte visuele elementen:** De twee gestreepte katten, De roze deken, De twee lichtgekleurde afstandsbedieningen
- **Mogelijke transcriptie-frictie:** Er is geen frictie tussen de getranscribeerde tekst en wat er op de afbeelding te zien is. De vraag is duidelijk en de objecten waarnaar gevraagd wordt, zijn zichtbaar en telbaar in de afbeelding.

#### Resultaat Module 4: Native Multimodaal Antwoord & Evaluatie (`gemini-2.5-flash` — 10.88s)
- **Native gehoorde vraag (Audio + Beeld samen):** *"Hoeveel katten liggen er op de roze deken en hoeveel afstandsbedieningen liggen er precies naast?"*
- **Native multimodaal antwoord:** Er liggen twee katten op de roze deken en er liggen twee afstandsbedieningen precies naast.
- **Vergelijking Cascaded vs. Native:** In dit specifieke geval zijn de resultaten van de cascaded aanpak (Module 1-3) en de native end-to-end aanpak (Module 4) identiek en beide correct. Dit komt doordat zowel de audio als de visuele informatie van hoge kwaliteit en eenduidig waren. De native aanpak toont hier geen significant voordeel in nauwkeurigheid, maar bevestigt wel de robuustheid onder ideale omstandigheden, zonder de potentiële frictie die in een cascaded systeem kan ontstaan bij minder ideale input.

#### Foutanalyse (Spraakherkenning vs. Beeldinterpretatie)
- **Foutbron-analyse:** Er zijn geen fouten of onduidelijkheden ontstaan door de spraakherkenning, aangezien de audio zeer helder was en de vraag direct en eenduidig. Ook de interpretatie van de afbeelding was accuraat, omdat de twee katten en twee afstandsbedieningen duidelijk zichtbaar en telbaar zijn op de roze deken.
- **Beperkingen en verbeterpunten:** De beperking van dit experiment is dat het plaatsvond onder ideale omstandigheden: de audio was zeer duidelijk en de visuele objecten waren prominent en onbelemmerd zichtbaar. Dit test niet de robuustheid van het systeem bij akoestische ruis, complexe zinsbouw, of visuele ambiguïteit (bijv. occlusie, slechte belichting). Verbeterpunten omvatten het testen met meer uitdagende datasets die variaties in spraakkwaliteit en visuele complexiteit bevatten, en het evalueren van het vermogen van het systeem om complexere ruimtelijke relaties of attributen te begrijpen die verder gaan dan eenvoudige tellingen.

---

### Experiment 2: Akoestische Stress-test /Ruis & Oriëntatie (Bruine Beer)

- **MS COCO ID:** `000000000285`
- **Lokale Afbeelding:** `experiments/exp2.jpg`
- **COCO Bron-URL:** [http://images.cocodataset.org/val2017/000000000285.jpg](http://images.cocodataset.org/val2017/000000000285.jpg)
- **Audiobestand:** `experiments/exp2.mp3` (Fysiek MP3-bestand geladen)
- **Onderzoeksfocus:** *Impact van snelle/gemompelde spraak of achtergrondruis op spraakherkenning versus native audio-beeld begrip.*

#### Resultaat Module 1: Geïsoleerde Beeldanalyse (`gemini-2.5-flash` — 3.57s)
- **Algemene beschrijving:** De afbeelding toont een close-up portret van een bruine beer, waarbij het hoofd en een deel van de schouders zichtbaar zijn. De vacht van de beer is overwegend lichtbruin tot goudbruin van kleur, met donkerdere tinten rond de snuit en de onderkant van de nek. De ogen van de beer zijn donker en lijken direct in de camera te kijken. De neus is groot en zwart, en de mond is licht geopend, waardoor een deel van de tanden en de tong zichtbaar zijn. De oren zijn klein en rond, bedekt met dezelfde vachtkleur als de rest van het hoofd. De achtergrond bestaat uit groen gras met enkele donkerdere plekken aarde of schaduw.
- **Gedetecteerde hoofdobjecten:** 1 bruine beer, Gras
- **Ruimtelijke context:** De beer is prominent in het midden van de afbeelding geplaatst en vult het grootste deel van het kader, wat duidt op een close-up opname. Het hoofd van de beer is naar voren gericht, met de blik direct op de kijker. De schouders en een deel van de borst zijn zichtbaar aan de onderkant van de afbeelding. De achtergrond, bestaande uit groen gras, is enigszins onscherp, waardoor de focus volledig op de beer ligt. De compositie creëert een directe en intieme weergave van het dier.

#### Resultaat Module 2: Geïsoleerde Audio-transcriptie / ASR (`gemini-2.5-flash` — 3.17s)
- **Letterlijke transcriptie:** *"even heel snel kijken hoor. Zit er nou een grote bruine peer of een bruine beer in het gras? En naar welke kant kijkt het dier precies?"*
- **Geschatte verstaanbaarheid:** Hoog
- **Akoestische opmerkingen:** De spraak is helder en goed verstaanbaar. Er is geen merkbaar achtergrondgeluid.

#### Resultaat Module 3: Gekoppelde / Cascaded Integratie (`gemini-2.5-flash` — 5.12s)
- **Antwoord op vraag (Tekst + Beeld):** In het gras zit een bruine beer. Het dier kijkt direct naar voren, recht in de camera of naar de kijker.
- **Gebruikte visuele elementen:** De afbeelding toont een close-up portret van een bruine beer, Gedetecteerde objecten: 1 bruine beer, De achtergrond bestaat uit groen gras, De ogen van de beer zijn donker en lijken direct in de camera te kijken, Het hoofd van de beer is naar voren gericht, met de blik direct op de kijker
- **Mogelijke transcriptie-frictie:** Ja, er is frictie. De transcriptie bevat het woord "peer" (peer) in de vraag "Zit er nou een grote bruine peer of een bruine beer in het gras?". Op de afbeelding is duidelijk een bruine beer te zien en geen peer. Dit duidt op een mogelijke ASR-transcriptiefout of een strikvraag.

#### Resultaat Module 4: Native Multimodaal Antwoord & Evaluatie (`gemini-2.5-flash` — 12.11s)
- **Native gehoorde vraag (Audio + Beeld samen):** *"even heel snel kijken hoor. Zit er nou een grote bruine peer of een bruine beer in het gras? En naar welke kant kijkt het dier precies?"*
- **Native multimodaal antwoord:** In het gras zit een bruine beer. Het dier kijkt recht naar voren, direct naar de kijker.
- **Vergelijking Cascaded vs. Native:** De cascaded aanpak (Module 1-3) identificeerde correct de objecten in de afbeelding (bruine beer, gras) en transcribeerde de audio nauwkeurig, inclusief de keuze 'peer of een bruine beer'. De frictie-analyse in Module 3 merkte de 'peer' op als een mogelijke ASR-transcriptiefout of strikvraag, wat duidt op een sequentieel proces waarbij de tekstuele ambiguïteit eerst wordt vastgesteld voordat de visuele context wordt gebruikt voor resolutie. De native end-to-end aanpak (Module 4) verwerkte de audio en het beeld gelijktijdig. Hierdoor werd de vraag 'peer of een bruine beer' direct geïnterpreteerd als een keuze die door de visuele informatie (de aanwezigheid van een beer) kon worden beantwoord. Dit resulteerde in een vloeiendere en directere resolutie van de vraag, zonder de noodzaak om een 'mogelijke ASR-fout' te signaleren, omdat de visuele context de intentie van de vraag onmiddellijk duidelijk maakte.

#### Foutanalyse (Spraakherkenning vs. Beeldinterpretatie)
- **Foutbron-analyse:** Er ontstonden geen fouten of onduidelijkheden door de spraakherkenning of de beeldinterpretatie. De vraag bevatte expliciet de keuze tussen 'peer' en 'beer', wat door het multimodale model correct werd herkend. De visuele context van de afbeelding maakte direct duidelijk dat het om een bruine beer ging, waardoor de ambiguïteit in de vraagstelling onmiddellijk werd opgelost.
- **Beperkingen en verbeterpunten:** Een beperking van dit experiment is dat de akoestische stress-test (snelle/gemompelde spraak of achtergrondruis) niet sterk aanwezig was; de spraak was helder. De ambiguïteit tussen 'peer' en 'beer' was een expliciet gestelde keuze in de audio, geen gevolg van ruis of onduidelijke articulatie. Voor verbetering van het systeem zou het nuttig zijn om experimenten uit te voeren met daadwerkelijk gemompelde spraak of significante achtergrondruis, waarbij homofonen of near-homofonen ontstaan die alleen met sterke visuele context kunnen worden opgelost. Ook het testen met visueel minder eenduidige situaties of vragen die niet direct visueel te beantwoorden zijn, kan verdere inzichten bieden.

---

### Experiment 3: Visuele Complexiteit & Occlusie (Drukke Woonkamer)

- **MS COCO ID:** `000000000139`
- **Lokale Afbeelding:** `experiments/exp3.jpg`
- **COCO Bron-URL:** [http://images.cocodataset.org/val2017/000000000139.jpg](http://images.cocodataset.org/val2017/000000000139.jpg)
- **Audiobestand:** `experiments/exp3.mp3` (Fysiek MP3-bestand geladen)
- **Onderzoeksfocus:** *Beperkingen van beeldanalyse bij overlappende objecten, kleine details en exact tellen.*

#### Resultaat Module 1: Geïsoleerde Beeldanalyse (`gemini-2.5-flash` — 11.67s)
- **Algemene beschrijving:** De afbeelding toont een warm verlicht interieur van een woning, waarschijnlijk een open woon-, eet- en keukengedeelte. De muren zijn overwegend geel, wat bijdraagt aan de warme sfeer, versterkt door het zonlicht dat door de ramen valt. De vloer is van glanzend, donkerbruin hout. Er zijn diverse meubelstukken en decoraties zichtbaar, wat duidt op een bewoonde en functionele ruimte. De algehele indruk is die van een modern, doch gezellig interieur met een focus op natuurlijke lichtinval en een open indeling.
- **Gedetecteerde hoofdobjecten:** Televisie (1), TV-meubel (1), Wandkast (1), Radiator (1), Ramen (4, waarvan 3 grote en 1 kleinere in de keuken), Eettafel (1), Stoelen (4 zichtbaar bij de eettafel), Persoon (1, vrouw), Planten (2, op vensterbank en eettafel), Vazen (3, paars op TV-meubel, transparant met bloemen op eettafel, lichtgroen met bloem op salontafel), Hanglampen (2, een met 4 kappen boven de eettafel, een enkele in de keuken), Keukenmeubilair (diverse kasten, aanrecht), Koelkast (1, roestvrij staal), Open haard (1, ingebouwd), Vloerkleed (1, beige/grijs), Salontafel (1, rond, roze blad), Houten vloer, Wandklok (1, in de keuken), Huisdierenmand (1, onder de radiator), Houtblokken (in een mand naast de open haard)
- **Ruimtelijke context:** De ruimte is opgedeeld in verschillende functionele zones die naadloos in elkaar overlopen. Links op de voorgrond bevindt zich het woongedeelte met een grote flatscreen televisie op een laag TV-meubel en daarboven een horizontale wandkast. Een radiator is onder een van de ramen geplaatst. Centraal in de afbeelding is het eetgedeelte met een rechthoekige houten eettafel omringd door vier stoelen met houten rugleuningen en rode zittingen. Boven de eettafel hangt een lamp met vier kappen. Achter de eettafel, aan de rechterkant, staat een vrouw die zich buigt over een oppervlak, mogelijk een aanrecht of een deel van de eettafel, met de rug naar de kijker toe. Achter haar bevindt zich een open keuken met lichte kasten en een roestvrijstalen koelkast. Rechts in de afbeelding domineert een grote, ingebouwde open haard met een donkergrijze onderkant en een groen bovendeel. Een ronde salontafel met een roze blad en een lichtgroene vaas met een roze bloem staat op de voorgrond rechts, gedeeltelijk zichtbaar. De houten vloer verbindt de verschillende zones, terwijl een vloerkleed het woongedeelte markeert. De ramen aan de linkerkant laten veel daglicht binnen, wat de ruimte helder maakt.

#### Resultaat Module 2: Geïsoleerde Audio-transcriptie / ASR (`gemini-2.5-flash` — 3.16s)
- **Letterlijke transcriptie:** *"Beschrijf deze drukke woonkamer. Hoeveel stoelen kun je in totaal tellen en waar in de kamer staat de televisie?"*
- **Geschatte verstaanbaarheid:** Hoog
- **Akoestische opmerkingen:** Geen achtergrondgeluid, duidelijke articulatie en normaal spreektempo.

#### Resultaat Module 3: Gekoppelde / Cascaded Integratie (`gemini-2.5-flash` — 4.53s)
- **Antwoord op vraag (Tekst + Beeld):** In de afgebeelde woonkamer zijn in totaal vier stoelen te tellen, die allemaal rond de eettafel staan. De televisie bevindt zich links in de kamer, geplaatst op een laag TV-meubel tegen de muur.
- **Gebruikte visuele elementen:** Vier stoelen rond de eettafel, De eettafel, De televisie, Het TV-meubel, De linkerwand van de kamer
- **Mogelijke transcriptie-frictie:** De transcriptie is accuraat en er is geen duidelijke frictie tussen de getranscribeerde tekst en de visuele inhoud van de afbeelding. De term 'drukke woonkamer' is een subjectieve beschrijving, maar leidt niet tot onlogische of onbestaande elementen in relatie tot het beeld.

#### Resultaat Module 4: Native Multimodaal Antwoord & Evaluatie (`gemini-2.5-flash` — 12.23s)
- **Native gehoorde vraag (Audio + Beeld samen):** *"Beschrijf deze drukke woonkamer. Hoeveel stoelen kun je in totaal tellen en waar in de kamer staat de televisie?"*
- **Native multimodaal antwoord:** De afbeelding toont een open woonruimte met een eethoek en een deel van een keuken. De muren zijn geel en de vloer is van donkerbruin hout. Er is veel natuurlijk licht door de ramen. Links staat een grote televisie op een TV-meubel. In het midden staat een houten eettafel met vier stoelen eromheen. Rechts is een open haard en een deel van een keuken zichtbaar. Een persoon staat bij de eettafel. Ik tel vier stoelen in totaal, die allemaal rond de eettafel staan. De televisie bevindt zich links in de kamer, geplaatst op een laag, donker TV-meubel tegen de gele muur.
- **Vergelijking Cascaded vs. Native:** In dit specifieke geval is er geen significant kwaliteitsverschil of verschil in nauwkeurigheid tussen de cascaded en de native aanpak. Beide systemen leveren een correct en feitelijk antwoord op de gestelde vragen. De beschrijving van de kamer, het aantal getelde stoelen (vier) en de locatie van de televisie zijn identiek en accuraat in beide benaderingen. De visuele complexiteit en de mate van occlusie in de afbeelding waren niet zodanig dat ze tot verschillende tellingen of interpretaties leidden voor de gevraagde objecten.

#### Foutanalyse (Spraakherkenning vs. Beeldinterpretatie)
- **Foutbron-analyse:** De spraakherkenning was accuraat; de vraag is duidelijk verstaanbaar en correct getranscribeerd. De visuele interpretatie van de afbeelding is direct en feitelijk. Het tellen van de stoelen is gebaseerd op wat zichtbaar is, en de locatie van de televisie is correct geïdentificeerd. De term 'drukke woonkamer' is subjectief, maar de visuele elementen ondersteunen de indruk van een goed gevulde ruimte zonder dat dit tot fouten in de objectidentificatie of -telling leidt.
- **Beperkingen en verbeterpunten:** Een beperking van dit experiment is dat de vraag over het aantal stoelen relatief eenvoudig was, aangezien de stoelen duidelijk zichtbaar en gegroepeerd waren. Meer complexe scenario's met gedeeltelijk verborgen stoelen of stoelen in verschillende kamers zouden een grotere uitdaging vormen. De term 'drukke woonkamer' is subjectief en wordt door het model geïnterpreteerd als een ruimte met veel objecten, wat in dit geval klopt, maar de definitie van 'druk' kan variëren. Voor verbetering kan het systeem robuuster worden gemaakt in objectdetectie en -telling bij zware occlusie. Daarnaast kan de interpretatie van subjectieve termen worden verfijnd door een breder scala aan visuele kenmerken te overwegen.

---

### Experiment 4: Actie- en Interactieherkenning (Honkbalwedstrijd)

- **MS COCO ID:** `000000000872`
- **Lokale Afbeelding:** `experiments/exp4.jpg`
- **COCO Bron-URL:** [http://images.cocodataset.org/val2017/000000000872.jpg](http://images.cocodataset.org/val2017/000000000872.jpg)
- **Audiobestand:** `experiments/exp4.mp3` (Fysiek MP3-bestand geladen)
- **Onderzoeksfocus:** *Dynamische relaties tussen personen, kleding en acties interpreteren op basis van een gesproken vraag.*

#### Resultaat Module 1: Geïsoleerde Beeldanalyse (`gemini-2.5-flash` — 6.22s)
- **Algemene beschrijving:** De afbeelding toont twee mannen op een honkbalveld tijdens een zonnige dag. De man op de voorgrond, gekleed in een wit shirt, grijze honkbalbroek, donkerblauwe helm en zwarte handschoenen, rent van links naar rechts over het zanderige deel van het veld. Zijn lichaamshouding en de lichte bewegingsonscherpte van zijn benen duiden op actieve beweging. Achter hem en iets naar rechts staat een tweede man, gekleed in een groen T-shirt en een groene honkbalpet. Hij houdt een bruine honkbalhandschoen in zijn linkerhand, met zijn arm gebogen alsof hij een bal vasthoudt of net heeft gegooid. De achtergrond bestaat uit een strook groen gras, gevolgd door dichte begroeiing van bomen en struiken onder een heldere hemel.
- **Gedetecteerde hoofdobjecten:** 2 mannen, 1 honkbalhelm, 1 honkbalhandschoen, 1 honkbalpet, Groen gras, Bomen, Struiken, Zanderig honkbalveld
- **Ruimtelijke context:** De compositie plaatst de twee mannen centraal in het beeld, met de rennende speler op de voorgrond en de speler met de handschoen erachter. Het onderste deel van de afbeelding wordt ingenomen door het zanderige oppervlak van het honkbalveld, dat overgaat in een strook groen gras in het midden. De achtergrond wordt gedomineerd door weelderige groene bomen en struiken, wat een buitenomgeving suggereert. De speler op de voorgrond is scherper in beeld dan de speler op de achtergrond, wat diepte creëert. De lichtinval van bovenaf wijst op een zonnige dag.

#### Resultaat Module 2: Geïsoleerde Audio-transcriptie / ASR (`gemini-2.5-flash` — 2.52s)
- **Letterlijke transcriptie:** *"Welke sport spelen deze personen? Welke actie voeren ze op dit moment uit en welke kleuren heeft hun sportkleding?"*
- **Geschatte verstaanbaarheid:** Hoog
- **Akoestische opmerkingen:** Geen achtergrondgeluid, duidelijk spreektempo en articulatie.

#### Resultaat Module 3: Gekoppelde / Cascaded Integratie (`gemini-2.5-flash` — 6.29s)
- **Antwoord op vraag (Tekst + Beeld):** De personen spelen honkbal. De persoon op de voorgrond rent over het zanderige deel van het veld, terwijl de persoon op de achtergrond een honkbalhandschoen vasthoudt en zich voorbereidt op een worp of vangst. De rennende speler draagt een wit shirt, grijze honkbalbroek, een donkerblauwe helm en zwarte handschoenen. De andere speler draagt een groen T-shirt en een groene honkbalpet.
- **Gebruikte visuele elementen:** honkbalveld (zanderig deel en gras), twee mannen, man op de voorgrond gekleed in wit shirt, grijze honkbalbroek, donkerblauwe helm en zwarte handschoenen, man op de voorgrond die rent met lichte bewegingsonscherpte van zijn benen, man op de achtergrond gekleed in groen T-shirt en groene honkbalpet, man op de achtergrond die een bruine honkbalhandschoen vasthoudt met gebogen arm
- **Mogelijke transcriptie-frictie:** De getranscribeerde tekst is helder en logisch en komt volledig overeen met de visuele informatie in de afbeelding. Er is geen frictie.

#### Resultaat Module 4: Native Multimodaal Antwoord & Evaluatie (`gemini-2.5-flash` — 9.91s)
- **Native gehoorde vraag (Audio + Beeld samen):** *"Welke sport spelen deze personen? Welke actie voeren ze op dit moment uit en welke kleuren heeft hun sportkleding?"*
- **Native multimodaal antwoord:** De personen spelen honkbal. De speler op de voorgrond rent over het zanderige deel van het veld. De speler op de achtergrond houdt een honkbalhandschoen vast en lijkt zich voor te bereiden op een worp of vangst. De rennende speler draagt een wit shirt, een grijze broek, een donkerblauwe helm en zwarte handschoenen. De andere speler draagt een groen T-shirt en een groene honkbalpet.
- **Vergelijking Cascaded vs. Native:** In dit specifieke geval is er geen significant verschil in kwaliteit of nauwkeurigheid tussen de losgekoppelde (cascaded) aanpak en de directe multimodale fusie (native). Beide methoden leveren een correct en gedetailleerd antwoord op de gestelde vraag. Dit komt doordat zowel de audio als de visuele informatie van hoge kwaliteit waren en geen complexe disambiguatie vereisten.

#### Foutanalyse (Spraakherkenning vs. Beeldinterpretatie)
- **Foutbron-analyse:** Er zijn geen fouten of onduidelijkheden ontstaan door de spraakherkenning, aangezien de audio zeer helder was. Ook de interpretatie van de afbeelding was eenduidig en leverde geen fouten op.
- **Beperkingen en verbeterpunten:** Een beperking van dit experiment is dat de audio-input zeer duidelijk was en de visuele context eenduidig, waardoor de voordelen van native multimodale fusie ten opzichte van een cascaded aanpak niet volledig tot uiting komen. Voor verbetering van het systeem is het raadzaam om te testen met complexere scenario's, zoals audio met achtergrondgeluid of onduidelijke spraak, en visuele context die ambigu is of diepere inferentie vereist. Dit zou een betere indicatie geven van de meerwaarde van directe multimodale fusie.

---

### Experiment 5: Hallucinatie- & Strikvraag-test (Teddyberen)

- **MS COCO ID:** `000000000776`
- **Lokale Afbeelding:** `experiments/exp5.jpg`
- **COCO Bron-URL:** [http://images.cocodataset.org/val2017/000000000776.jpg](http://images.cocodataset.org/val2017/000000000776.jpg)
- **Audiobestand:** `experiments/exp5.mp3` (Fysiek MP3-bestand geladen)
- **Onderzoeksfocus:** *Onderzoeken of het model hallucineert wanneer de gesproken vraag verwijst naar een object dat niet in de afbeelding aanwezig is.*

#### Resultaat Module 1: Geïsoleerde Beeldanalyse (`gemini-2.5-flash` — 7.09s)
- **Algemene beschrijving:** De afbeelding toont een close-up van drie knuffelberen die dicht bij elkaar liggen. De beren variëren in tinten bruin en hebben verschillende texturen van pluche vacht. De belichting is zacht en creëert schaduwen die diepte toevoegen aan de compositie. De focus ligt op de hoofden en bovenlichamen van de beren, die de meeste ruimte in beslag nemen en een gevoel van knusheid uitstralen.
- **Gedetecteerde hoofdobjecten:** Drie knuffelberen (één lichtbruin, één goudbruin, één oranjebruin), Donkerbruine, gestreepte stof (achtergrond), Lichtblauwe stof (achtergrond)
- **Ruimtelijke context:** De drie knuffelberen zijn dicht op elkaar gepositioneerd, waardoor ze een overlappende en knusse compositie vormen. De lichtbruine beer bevindt zich in het midden-links van de afbeelding, met zijn hoofd naar voren gericht. De goudbruine beer ligt erboven en rechts van de lichtbruine beer, met zijn hoofd naar beneden gericht en zijn arm over de lichtbruine beer. De oranjebruine beer bevindt zich in de linkeronderhoek, met zijn hoofd schuin omhoog gericht en zijn lichaam deels bedekt door de andere beren. De achtergrond bestaat uit een donkere, gestreepte stof in de linkerbovenhoek en een effen lichtblauwe stof in de rechteronderhoek, die de beren omringen.

#### Resultaat Module 2: Geïsoleerde Audio-transcriptie / ASR (`gemini-2.5-flash` — 2.69s)
- **Letterlijke transcriptie:** *"Hoeveel teddyberen zitten er naast elkaar op de foto en welke kleur heeft de voetbal die tussen de teddyberen in ligt?"*
- **Geschatte verstaanbaarheid:** Hoog
- **Akoestische opmerkingen:** Geen achtergrondgeluid, duidelijk spreektempo en articulatie.

#### Resultaat Module 3: Gekoppelde / Cascaded Integratie (`gemini-2.5-flash` — 3.91s)
- **Antwoord op vraag (Tekst + Beeld):** Op de foto zijn drie teddyberen te zien. Er ligt geen voetbal tussen de teddyberen in.
- **Gebruikte visuele elementen:** De drie knuffelberen (één lichtbruin, één goudbruin, één oranjebruin) die dicht bij elkaar liggen., De afwezigheid van een voetbal tussen de beren of elders in de afbeelding.
- **Mogelijke transcriptie-frictie:** Er is frictie tussen de getranscribeerde vraag en de afbeelding. De vraag stelt naar de kleur van een voetbal die tussen de teddyberen in ligt, maar er is geen voetbal zichtbaar op de afbeelding. Dit betreft een strikvraag over een niet-bestaand object in het beeld.

#### Resultaat Module 4: Native Multimodaal Antwoord & Evaluatie (`gemini-2.5-flash` — 8.44s)
- **Native gehoorde vraag (Audio + Beeld samen):** *"Hoeveel teddyberen zitten er naast elkaar op de foto, en welke kleur heeft de voetbal die tussen de teddyberen in ligt?"*
- **Native multimodaal antwoord:** Op de foto zijn drie teddyberen zichtbaar. Er is geen voetbal te zien tussen de teddyberen.
- **Vergelijking Cascaded vs. Native:** Zowel de cascaded aanpak als de native end-to-end aanpak komen tot dezelfde conclusie. Beide systemen herkennen correct de vraag over het aantal teddyberen en identificeren dat er geen voetbal in de afbeelding aanwezig is. De kwaliteit en nauwkeurigheid zijn in dit geval vergelijkbaar, wat suggereert dat de cascaded ASR en VQA modules goed samenwerken om de strikvraag te beantwoorden. De native aanpak bevestigt de robuustheid van het antwoord.

#### Foutanalyse (Spraakherkenning vs. Beeldinterpretatie)
- **Foutbron-analyse:** De spraakherkenning van de vraag was accuraat. De vraag bevat een strikvraag over een object (een voetbal) dat niet in de afbeelding aanwezig is. Het model heeft correct vastgesteld dat er geen voetbal zichtbaar is, wat duidt op een correcte visuele interpretatie en het vermogen om niet-bestaande objecten te identificeren. Er zijn geen fouten of onduidelijkheden ontstaan door spraakherkenning of beeldinterpretatie in dit specifieke geval.
- **Beperkingen en verbeterpunten:** Een beperking van dit experiment is dat de audio zeer duidelijk was en de vraag over het niet-bestaande object eenduidig. Hierdoor was er weinig ruimte voor de native multimodale fusie om een significant voordeel te tonen ten opzichte van de cascaded aanpak op het gebied van ASR-foutreductie door visuele context. Een verbeterpunt zou zijn om audio te gebruiken met meer achtergrondruis of homofonen die alleen met visuele context correct geïnterpreteerd kunnen worden, om zo de kracht van native multimodale ASR beter te testen. Daarnaast kan het systeem verder worden getest met complexere strikvragen of vragen die subtiele visuele details vereisen.

---

## 3. Beantwoording Kernvragen voor Verkenning

Op basis van de kwantitatieve tijdsmetingen en kwalitatieve vergelijkingen uit de vijf bovenstaande MS COCO 2017 experimenten worden de zes kernvragen van het labo hieronder beantwoord.

### 1. Zijn de gegenereerde beschrijvingen nauwkeurig en passend bij de afbeeldingen?
De gegenereerde beschrijvingen zijn consistent nauwkeurig en passend bij de afbeeldingen. De algemene beschrijvingen en gedetecteerde objecten van Module 1 (beeld-alleen) zijn gedetailleerd en feitelijk correct voor alle experimenten (Exp 1-5). De antwoorden op de vragen in Module 3 (cascaded VQA) en Module 4 (native multimodale) zijn eveneens accuraat en reflecteren de visuele inhoud van de afbeeldingen. Zelfs in gevallen van potentiële linguïstische ambiguïteit (Exp 2: 'peer' versus 'beer') of vragen over niet-bestaande objecten (Exp 5: 'voetbal'), leveren de modellen correcte en feitelijke antwoorden gebaseerd op de visuele context, wat de hoge mate van nauwkeurigheid bevestigt.

### 2. Hoe goed werkt de integratie tussen het beeldmodel en het taalmodel?
De integratie tussen het beeldmodel en het taalmodel werkt zeer goed, wat resulteert in effectieve Visual Question Answering (VQA). In Experiment 1, 3 en 4, onder ideale omstandigheden met heldere audio en eenduidige visuele informatie, leveren zowel de cascaded als de native multimodale aanpak identieke en correcte resultaten. Dit toont een robuuste basisintegratie. Experiment 2 ('Akoestische Stress-test') illustreert de kracht van deze integratie; waar de cascaded aanpak een 'frictie' opmerkt door de homofoon 'peer' in de transcriptie, lost de native aanpak de ambiguïteit direct op door de gelijktijdige verwerking van visuele informatie (de aanwezigheid van een 'beer'). Dit duidt op een superieure, meer intrinsieke integratie in de native architectuur voor het disambigueren van linguïstische onduidelijkheden met behulp van visuele context. In Experiment 5 ('Hallucinatie- & Strikvraag-test') tonen beide benaderingen een succesvolle integratie door de afwezigheid van een niet-bestaand object ('voetbal') correct te identificeren, wat de effectiviteit van cross-modale verificatie benadrukt.

### 3. Welke uitdagingen kwamen naar voren bij het combineren van verschillende modaliteiten?
Verschillende uitdagingen kwamen naar voren bij het combineren van modaliteiten. De meest prominente is de potentiële linguïstische ambiguïteit en de impact van ASR-fouten, zoals geïllustreerd in Experiment 2 met de homofoon 'peer' versus 'beer'. Hoewel de spraak helder was, benadrukt dit de noodzaak van visuele context voor het oplossen van dergelijke onduidelijkheden. Visuele complexiteit en occlusie, getest in Experiment 3 ('Drukke Woonkamer'), vormen een uitdaging voor nauwkeurige objectdetectie en -telling in drukke scènes met veel overlappingen of kleine details, hoewel de modellen de specifieke vragen in dit experiment goed beantwoordden. Een andere uitdaging is het voorkomen van hallucinatie wanneer de gesproken vraag verwijst naar een object dat niet in de afbeelding aanwezig is, zoals getest in Experiment 5 ('Teddyberen'). De modellen toonden hierin robuustheid door correct de afwezigheid van het object te melden. Tot slot is de interpretatie van subjectieve termen, zoals 'drukke woonkamer' in Experiment 3, een inherente uitdaging voor AI-systemen.

### 4. Zijn er verbeteringen mogelijk voor de gegenereerde beschrijvingen?
Verbeteringen zijn mogelijk door de robuustheid van het systeem onder niet-ideale omstandigheden te vergroten. Dit omvat het testen en trainen met akoestische ruis en onduidelijke spraak (gesuggereerd in Exp 1, 2, 4, 5) om de ASR te verbeteren, vooral bij homofonen die visuele context vereisen. Daarnaast kan de objectdetectie en -telling worden verbeterd bij visuele ambiguïteit en zware occlusie (Exp 1, 3, 5), met name in complexe, drukke scènes of bij gedeeltelijk verborgen objecten. Het systeem kan verder worden verfijnd in het uitvoeren van complexere semantische en ruimtelijke inferentie, zoals het begrijpen van complexere relaties of attributen die verder gaan dan eenvoudige tellingen (Exp 1) en diepere inferentie voor acties en interacties in minder eenduidige visuele contexten (Exp 4). De interpretatie van subjectieve termen, zoals 'druk' (Exp 3), kan worden verfijnd door een breder scala aan visuele kenmerken en contextuele aanwijzingen te overwegen. Tot slot kan het systeem verder worden getest met complexere strikvragen of vragen die subtiele visuele details vereisen (Exp 5).

### 5. Welke meerwaarde biedt het combineren van afbeeldingen en audio?
Het combineren van afbeeldingen en audio biedt aanzienlijke meerwaarde. De meest significante is de contextuele disambiguatie, waarbij ambiguïteit in één modaliteit wordt opgelost met informatie uit de andere. Experiment 2 is hiervan een duidelijk voorbeeld, waar de visuele aanwezigheid van een 'beer' de linguïstische ambiguïteit met 'peer' oplost, waardoor potentiële ASR-fouten worden voorkomen en een correcter begrip van de vraag ontstaat. Ten tweede maakt het de verificatie van non-existentie mogelijk; Experiment 5 toont aan dat het systeem correct kan vaststellen dat een object ('voetbal') waarnaar in de audio wordt gevraagd, niet visueel aanwezig is, wat hallucinatie voorkomt en de betrouwbaarheid van het antwoord vergroot. Ten slotte leidt de integratie van beide modaliteiten tot rijkere, completere en contextueel relevantere antwoorden op vragen die uitsluitend met één modaliteit niet beantwoord kunnen worden, zoals blijkt uit de gedetailleerde VQA-antwoorden in alle experimenten. Dit verhoogt de algehele robuustheid van het systeem.

### 6. Welke fouten ontstaan door spraakherkenning en welke door de interpretatie van de afbeelding?
In de gepresenteerde experimenten zijn er geen daadwerkelijke fouten in de uiteindelijke antwoorden die direct terug te voeren zijn op spraakherkenning (ASR) of beeldinterpretatie die niet door de multimodale fusie konden worden gecorrigeerd. Echter, Experiment 2 ('Akoestische Stress-test') toont een potentiële ASR-frictie aan met de homofoon 'peer' versus 'beer'. De cascaded aanpak identificeerde dit als een mogelijke transcriptiefout of strikvraag, wat het risico van ASR-fouten bij homofonen zonder visuele disambiguatie illustreert. De native aanpak omzeilde dit door directe multimodale fusie, wat suggereert dat de visuele context een potentiële ASR-fout effectief heeft voorkomen of gecorrigeerd. Wat betreft fouten door beeldinterpretatie, waren de objectdetectie, telling en ruimtelijke contextbeschrijvingen (Module 1) consistent nauwkeurig in alle experimenten. Zelfs bij de strikvraag in Experiment 5 over een niet-bestaand object, heeft het beeldmodel correct vastgesteld dat de 'voetbal' afwezig was, wat duidt op een accurate interpretatie van de visuele inhoud (of het ontbreken daarvan). De 'beperkingen en verbeterpunten' in Module 4 van Experiment 3 suggereren dat zware occlusie een uitdaging kan zijn voor objectdetectie en -telling, maar in dit specifieke experiment leidde het niet tot een fout.
