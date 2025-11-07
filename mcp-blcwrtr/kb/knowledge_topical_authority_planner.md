# Topical Authority Planner

## Översikt

Topical Authority bygger trovärdighet genom att täcka ett ämne heltäckande. Denna guide hjälper planera innehållskluster som etablerar domänexpertis och stödjer länkbyggnad.

## Kärnconcept

### Definition av Topical Authority
- **Bredd**: Täcker alla aspekter av ett ämne
- **Djup**: Detaljerad information på varje nivå  
- **Kopplingar**: Tydliga relationer mellan innehåll
- **Uppdatering**: Aktuell och underhållen information

### Hierarkisk struktur
```
[Pillar Page]
    ├── [Cluster Topic 1]
    │   ├── [Subtopic 1.1]
    │   └── [Subtopic 1.2]
    ├── [Cluster Topic 2]
    │   ├── [Subtopic 2.1]
    │   └── [Subtopic 2.2]
    └── [Cluster Topic 3]
        ├── [Subtopic 3.1]
        └── [Subtopic 3.2]
```

## Planeringsprocess

### Steg 1: Ämnesanalys

#### Identifiera kärnämne
```markdown
Exempel: "Släktforskning i Sverige"

Huvudfrågor att besvara:
- Vad är släktforskning?
- Hur börjar man?
- Vilka källor finns?
- Vilka verktyg används?
- Vanliga utmaningar?
- Avancerade tekniker?
```

#### Konkurrentanalys
1. Identifiera top 10 rankande sidor
2. Analysera deras innehållstäckning
3. Hitta luckor och möjligheter
4. Identifiera unika vinklar

### Steg 2: Klusteruppbyggnad

#### Pillar Content (Huvudsida)
```markdown
Titel: "Komplett guide till släktforskning i Sverige 2024"
Längd: 3000-5000 ord
Syfte: Övergripande resurs som länkar till alla kluster

Struktur:
1. Introduktion till släktforskning
2. Översikt av alla delämnen (med länkar)
3. Quick-start guide
4. Resurslista
5. Nästa steg
```

#### Cluster Topics (Stödinnehåll)
```markdown
Cluster 1: "Källor för släktforskning"
- Kyrkoböcker och församlingsarkiv
- Folkräkningar och mantalslängder  
- Militära rullor
- Emigrantregister
- DNA-databaser

Cluster 2: "Verktyg och metoder"
- Digitala arkivtjänster
- Släktforskningsprogram
- DNA-testtjänster
- Organisationsmetoder
- Källkritik

Cluster 3: "Specialområden"
- Adelsforskning
- Soldatforskning
- Emigrantforskning
- Samisk släktforskning
- Judisk genealogi
```

### Steg 3: Innehållsmappning

#### Content Gap Analysis
```markdown
Vårt innehåll vs Konkurrenter:

[✓] Grundläggande guide
[✓] Kyrkoböcker
[✗] DNA-forskning (SAKNAS)
[✗] Kostnadsguide (SAKNAS)
[~] Internationell forskning (BRISTFÄLLIG)
```

#### Prioriteringsmatris
```
            Hög sökning | Låg sökning
Låg konkurrens    [A]        [B]
Hög konkurrens    [C]        [D]

A: Prioritet 1 - Quick wins
B: Prioritet 2 - Nischinnehåll
C: Prioritet 3 - Kräver högkvalitet
D: Prioritet 4 - Överväg relevans
```

## Branschspecifika klusterexempel

### Genealogi-kluster

#### Pillar: "Släktforskning Online"
```yaml
cluster_1_sources:
  - title: "Riksarkivets digitala samlingar"
  - title: "Arkiv Digital - komplett guide"
  - title: "SVAR vs ArkivDigital jämförelse"
  - title: "Gratis källor för släktforskning"

cluster_2_geography:
  - title: "Släktforska i Skåne"
  - title: "Norrländsk släktforskning"
  - title: "Stockholms stadsarkiv guide"
  - title: "Gotländska källor"

cluster_3_periods:
  - title: "Forskning före 1750"
  - title: "1800-talets källor"  
  - title: "Modern släktforskning 1900+"
  - title: "Medeltida källor"
```

### Casino-kluster

#### Pillar: "Online Casino Sverige 2024"
```yaml
cluster_1_games:
  - title: "Slots - komplett guide"
  - title: "Live casino för nybörjare"
  - title: "Bordsspel online"
  - title: "Progressiva jackpottar"

cluster_2_strategy:
  - title: "Bankroll management"
  - title: "Bonusstrategi guide"
  - title: "RTP och volatilitet"
  - title: "Ansvarfullt spelande"

cluster_3_providers:
  - title: "NetEnt spel guide"
  - title: "Evolution Gaming live casino"
  - title: "Play'n GO slots"
  - title: "Pragmatic Play nyheter"
```

## Länkstruktur inom kluster

### Intern länkstrategi
```
Pillar → Alla cluster topics (1 gång vardera)
Cluster topic → Pillar (2-3 gånger)
Cluster topic → Relaterade topics (1-2 gånger)
Subtopics → Parent cluster (1-2 gånger)
```

### Ankartextvariation
```markdown
Från Pillar → Cluster:
- "läs mer om kyrkoböcker"
- "komplett guide till DNA-tester"
- "allt om digitala arkiv"

Från Cluster → Pillar:
- "tillbaka till huvudguiden"
- "se översikten"
- "släktforskningsguiden"
```

## Innehållskalender

### Fas 1: Foundation (Månad 1-2)
- [ ] Pillar page publicerad
- [ ] 3-5 huvudkluster klara
- [ ] Grundläggande interlinking

### Fas 2: Expansion (Månad 3-4)
- [ ] Alla kluster kompletta
- [ ] Subtopics påbörjade
- [ ] FAQ/Schema implementation

### Fas 3: Optimization (Månad 5-6)
- [ ] Content gaps fyllda
- [ ] Uppdateringar baserat på data
- [ ] Avancerade topics tillagda

## Kvalitetssäkring

### Checklistor per content-typ

#### Pillar Page
- [ ] Minst 3000 ord
- [ ] Innehållsförteckning
- [ ] Länkar till alla clusters
- [ ] Uppdaterat datum synligt
- [ ] Schema markup

#### Cluster Content  
- [ ] 1500-2500 ord
- [ ] Länkar tillbaka till pillar
- [ ] Unik vinkel/värde
- [ ] Optimerad för long-tail
- [ ] Call-to-action

#### Supporting Content
- [ ] 800-1500 ord
- [ ] Specifikt fokus
- [ ] Praktiskt användbart
- [ ] Länkar till parent  
- [ ] Delningsbar

## Mätning och optimering

### KPIs för Topical Authority
```yaml
organic_metrics:
  - total_keywords_ranking: 500+
  - featured_snippets: 10+
  - avg_position_improvement: 15+
  
engagement_metrics:
  - time_on_site: 5+ min
  - pages_per_session: 3+
  - return_visitors: 30%+
  
authority_signals:
  - brand_searches: ökning 50%
  - natural_backlinks: 20+/månad
  - social_shares: 100+/innehåll
```

### Optimeringsloop
1. **Månadsvis analys**
   - Vilka sidor rankar bäst?
   - Var tappar vi besökare?
   - Vilka ämnen saknas?

2. **Kvartalsvis revidering**
   - Uppdatera pillar content
   - Expandera framgångsrika clusters
   - Konsolidera svaga sidor

3. **Årlig översyn**
   - Total restructuring om nödvändigt
   - Nya pillar topics
   - Arkivera outdated content

## Avancerade strategier

### Entity-baserad optimering
```markdown
Entiteter att etablera:
- [Varumärke] + släktforskning
- [Varumärke] + expert
- [Författare] + genealogi
- [Webbplats] + auktoritet
```

### Semantic triples
```
Subject - Predicate - Object
"Genline" - "är expert på" - "svensk släktforskning"
"DNA-test" - "används för" - "släktforskning"
"Kyrkoböcker" - "finns på" - "Riksarkivet"
```

## Skalning över domäner

### Multi-site strategi
```yaml
huvuddomän.se:
  - Pillar content
  - Huvudkluster
  
subdomain.huvuddomän.se:
  - Djupa guides
  - Verktyg
  
systersite.se:
  - Nischinnehåll
  - Lokalt fokus
```

### Cross-domain linking
- Endast mellan ägda properties
- Max 1-2 länkar per artikel
- Olika ankare varje gång
- Trackbar med UTM

## Content refresh strategi

### Uppdateringsschema
```markdown
Pillar pages: Var 3:e månad
- Nya statistik/data
- Expandera sektioner
- Uppdatera länkar

Cluster content: Var 6:e månad  
- Faktakontroll
- Nya exempel
- Bättre interlinking

Supporting pages: Årligen
- Relevankontroll
- Konsolidering om needed
- Arkivering om outdated
```

## Mall för ny topical cluster

```yaml
cluster_name: "Ditt ämne här"
pillar_page:
  title: "Ultimate guide till [ämne]"
  url: "/guide/[ämne]"
  target_length: 4000
  
cluster_topics:
  - name: "Grundläggande [ämne]"
    subtopics: 
      - "Vad är..."
      - "Hur fungerar..."
      - "Vanliga misstag"
      
  - name: "Avancerat [ämne]"
    subtopics:
      - "Experttekniker"
      - "Fallstudier"
      - "Framtiden"
      
content_calendar:
  month_1: [pillar, 2 clusters]
  month_2: [3 clusters, 5 subtopics]
  month_3: [optimization, gaps]
```

Denna planner uppdateras kontinuerligt baserat på algoritmförändringar och branschens best practices.
