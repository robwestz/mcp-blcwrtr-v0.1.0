# LSI Entities and Lemmatization Policy

## Översikt

LSI (Latent Semantic Indexing) termer är semantiskt relaterade ord som stärker relevansen mellan innehåll och länkad sida. Denna policy definierar krav för LSI-implementation i backlink-content.

## Grundläggande krav

### Kvantitet
- **Minimum**: 6 unika lemman inom länkfönstret
- **Maximum**: 10 unika lemman inom länkfönstret
- **Optimal**: 7-8 lemman för naturlig distribution

### Placering
- **Radius**: ±2 meningar från ankarlänken
- **Distribution**: Jämnt fördelade före och efter länken
- **Densitet**: Max 2 LSI-termer per mening

### Repetition
- **Max upprepning**: 2 gånger per lemma
- **Variation**: Använd synonymer vid behov av fler omnämnanden

## Lemmatisering

### Svenska lemman
Reducera ord till grundform:
- "forskade", "forskar", "forskning" → lemma: "forsk"
- "digitala", "digitalt", "digitalisering" → lemma: "digital"
- "spela", "spel", "spelande" → lemma: "spel"

### Undantag
Behåll distinktion för:
- Substantiv vs verb med olika betydelse
- Sammansatta ord med unik betydelse
- Varumärkesnamn och egennamn

## LSI-kategorier

### 1. Process-termer
Beskriver handlingar och metoder:
- forskning, analys, undersökning, granskning
- planering, strategi, metod, tillvägagångssätt
- utveckling, process, arbete, genomförande

### 2. Mått-termer
Kvantifierar och mäter:
- resultat, effekt, påverkan, utfall
- kvalitet, värde, nivå, grad
- statistik, data, siffror, mätning

### 3. Felkällor-termer
Identifierar problem och utmaningar:
- misstag, fel, brist, problem
- utmaning, svårighet, hinder, risk
- fallgrop, varning, fara, hot

### 4. Verktyg-termer
Resurser och hjälpmedel:
- verktyg, resurs, hjälpmedel, instrument
- plattform, system, tjänst, lösning
- källa, databas, arkiv, register

### 5. Tids-termer
Temporala referenser:
- modern, traditionell, historisk, framtida
- nu, då, sedan, tidigare
- utveckling, trend, förändring, evolution

## Branschspecifika LSI-listor

### Genealogi/Släktforskning
```
Kärntermer: släkt, anor, genealogi, arkiv
Process: forskning, sökning, spårning, kartläggning
Verktyg: kyrkobok, register, databas, DNA-test
Felkällor: felstavning, namnbyte, dublett, lucka
Resultat: släktträd, härstamning, koppling, fynd
```

### Casino/Gambling
```
Kärntermer: spel, casino, gambling, betting
Process: spela, satsa, vinna, riskera
Verktyg: plattform, bonus, odds, system
Felkällor: förlust, risk, beroende, problem
Resultat: vinst, jackpot, utbetalning, avkastning
```

### Digital marknadsföring
```
Kärntermer: digital, online, webb, internet
Process: optimering, marknadsföring, analys, mätning
Verktyg: SEO, analytics, verktyg, plattform
Felkällor: bounce, spam, filter, straff
Resultat: trafik, konvertering, ranking, ROI
```

## Implementation

### Steg 1: Identifiera länkposition
```python
# Pseudo-kod
link_position = find_link_in_text(article, anchor_text)
window_start = link_position - 2_sentences
window_end = link_position + 2_sentences
```

### Steg 2: Välj LSI-termer
1. Analysera ämnesdomäner (källa och mål)
2. Välj 2-3 termer från varje relevant kategori
3. Prioritera naturlig passform

### Steg 3: Distribuera termer
```
Mening -2: [1-2 LSI-termer]
Mening -1: [1-2 LSI-termer]
LÄNKMENING: [1 LSI-term + ankarlänk]
Mening +1: [1-2 LSI-termer]
Mening +2: [1-2 LSI-termer]
```

### Steg 4: Validera
- Räkna unika lemman (6-10)
- Kontrollera max repetition (≤2)
- Verifiera naturligt flöde

## Exempel på korrekt implementation

### Exempel 1: Släktforskning → Casino
```
Text:
"Släktforskning kräver metodisk analys och noggrann granskning av källor.
Efter timmar av intensivt arbete med arkivmaterial kan det vara skönt med en paus.
För vissa är [[casino online]] en form av digital avkoppling som ger mental vila.
Denna typ av underhållning erbjuder en annan sorts spänning än forskningsarbetet.
Många uppskattar möjligheten att växla mellan olika typer av aktiviteter online."

LSI-analys:
- analys, granskning, källor (process/verktyg)
- arbete, arkiv (verktyg)
- digital, online (2st) (kategori)
- underhållning, spänning (resultat)
- aktivitet (process)
Totalt: 9 unika lemman ✓
```

### Exempel 2: Överanvändning (FEL)
```
"Online online digital digital webb internet plattform [[casino]].
Digital online plattform system webb internet cyber virtuell."

Problem:
- Onaturlig upprepning
- Överdriven densitet
- Saknar semantisk mening
```

## Kvalitetskontroll

### Automatiska kontroller
1. Lemma-räknare inom fönster
2. Repetitionsdetektor
3. Densitetsanalys per mening
4. Kategoribalans

### Manuella kontroller
1. Läsbarhet och flöde
2. Semantisk relevans
3. Naturlig integration
4. Värde för läsaren

## Felsökning

### Problem: För få LSI-termer
Lösning:
1. Expandera till närliggande kategorier
2. Använd synonymer
3. Lägg till förklarande meningar

### Problem: För många repetitioner
Lösning:
1. Byt till synonymer
2. Omformulera meningar
3. Använd pronomen

### Problem: Onaturligt flöde
Lösning:
1. Integrera termer i naturliga fraser
2. Använd övergångsord
3. Fokusera på läsvärde

## Avancerade tekniker

### Semantisk brygga
Använd LSI-termer som gradvis övergår från käll-domän till mål-domän:
```
forskning → analys → metod → strategi → spel → underhållning
```

### Kontextuell förstärkning
Placera starkaste LSI-termer närmast länken:
```
Svag ← [generella termer] [specifika termer] [[LÄNK]] [specifika termer] [generella termer] → Svag
```

### Multi-domain coverage
Inkludera termer från både käll- och måldomän:
- 40% källdomän
- 40% måldomän  
- 20% brygtermer

## Uppdateringar

Denna policy revideras kvartalsvis baserat på:
- Algoritmförändringar
- Branschutveckling
- Resultatdata
- Nya forskningsrön

Senast uppdaterad: [Aktuellt datum]
