# Internal Linking Playbook

## Översikt

Internlänkning stärker webbplatsens struktur och hjälper både användare och sökmotorer navigera innehållet. Denna playbook definierar när och hur internlänkar ska implementeras i backlink-content.

## När internlänkning är tillåtet

### Grön zon - Alltid tillåtet
- Publicistens egen webbplats
- Innehåll som naturligt relaterar
- Stödjande artiklar/guider
- Kategori/tagg-sidor

### Gul zon - Kräver bedömning
- Produktsidor (om relevant)
- Kampanjsidor (om aktuella)
- Externa microsites (om samma ägare)

### Röd zon - Aldrig tillåtet
- Konkurrenters interna sidor
- Trasiga/redirectade sidor
- Duplikat/thin content
- Under konstruktion-sidor

## Strategiska mönster

### 1. Hub & Spoke
```
    [Huvudguide]
    /    |    \
[Del 1] [Del 2] [Del 3]
```

**Användning**: När huvudartikel länkar till fördjupningar
**Exempel**: "Komplett guide till släktforskning" → "Kyrkoböcker", "DNA-test", "Arkivbesök"

### 2. Syskonlänkning
```
[Artikel A] ←→ [Artikel B] ←→ [Artikel C]
```

**Användning**: Relaterade ämnen på samma nivå
**Exempel**: "Forskningsmetoder" ↔ "Vanliga misstag" ↔ "Digitala verktyg"

### 3. Hierarkisk länkning
```
[Kategori] → [Subkategori] → [Artikel]
     ↑              ↑             ↓
     └──────────────└─────────────┘
```

**Användning**: Tydlig navigationsstruktur
**Exempel**: "Casino" → "Slots" → "Progressiva jackpottar"

### 4. Kontextuell stöttning
```
[Huvudartikel] → [Definition] → [Tillbaka]
```

**Användning**: Förklara komplexa termer
**Exempel**: "...använd husförhörslängder¹..." → Förklaring → Tillbaka

## Ankartext-strategier för internlänkar

### Primära typer

1. **Exakt match** (20% max)
   ```
   Läs mer om [[släktforskning online]]
   ```

2. **Partial match** (40% rekommenderat)
   ```
   Upptäck [[de bästa metoderna för släktforskning]]
   ```

3. **Branded** (20% för viktiga sidor)
   ```
   Se vår [[Genline Academy]] för kurser
   ```

4. **Natural/Contextual** (20% minimum)
   ```
   [[Här finns fler exempel]] på lyckade sökningar
   ```

### Variation är nyckeln
```markdown
Första länken: "genealogisk forskning"
Andra länken: "utforska dina anor"  
Tredje länken: "läs guiden här"
Fjärde länken: "släktforskningsmetoder"
```

## Optimal länktäthet

### Riktlinjer per artikellängd
- 300-500 ord: 1-2 internlänkar
- 500-800 ord: 2-3 internlänkar
- 800-1200 ord: 3-5 internlänkar
- 1200+ ord: 5-7 internlänkar

### Fördelning i texten
```
[Introduktion] - 0-1 länk (om kritisk)
[Huvudinnehåll] - 60% av länkarna
[Sidospår/Stöd] - 30% av länkarna
[Slutsats/CTA] - 10% av länkarna
```

## Värdeöverföring

### PageRank Sculpting (modern approach)
```markdown
Högvärde-sidor (länka ofta till):
- Huvudkategorier
- Pillar content
- Konverteringssidor
- Nya viktiga artiklar

Lågvärde-sidor (länka sparsamt till):
- Arkivsidor
- Taggsidor
- Författarsidor
- Datumbaserade arkiv
```

### Tematisk relevans
Starkast värdeöverföring när:
- Samma övergripande ämne
- Kompletterande information
- Naturlig användarresa
- Semantisk närhet

## Teknisk implementation

### HTML-struktur
```html
<!-- Optimal -->
<a href="/guide/slaktforskning-online" title="Komplett guide till digital släktforskning">
  släktforskning online
</a>

<!-- Undvik -->
<a href="/guide/slaktforskning-online" target="_blank" rel="nofollow">
  Klicka här!!!
</a>
```

### URL-struktur bevarande
```markdown
Bra: /kategori/artikel-namn
Bra: /2024/01/artikel-namn
Dåligt: /?p=123
Dåligt: /node/456
```

## Användarupplevelse

### Länkplacering för klickbarhet
1. **I meningsflödet** (Bäst)
   ```
   "Genom att använda [[digitala arkiv]] kan du spara mycket tid"
   ```

2. **Som naturlig fortsättning**
   ```
   "...vilket förklaras mer ingående i [[denna guide]]."
   ```

3. **Som resurslista** (för flera länkar)
   ```
   Relaterade guider:
   - [[Kyrkoarkiv för nybörjare]]
   - [[DNA-test inom släktforskning]]
   ```

### Undvik länkblindhet
```markdown
❌ FEL: "Klicka [[här]], [[här]] och [[här]]"
✅ RÄTT: "Läs om [[kyrkoböcker]], [[bouppteckningar]] och [[domböcker]]"
```

## Mätning och optimering

### KPIs att följa
- Click-through rate på internlänkar
- Bounce rate efter länkklick
- Pages per session
- Time on site
- Conversion paths

### A/B-testing möjligheter
1. Ankartext-variationer
2. Länkplacering
3. Antal länkar
4. Visuell styling
5. Kontextuell text runt länk

## Säsongsbaserad internlänkning

### Exempel: Släktforskning
```markdown
Januari: Länka till "Nyårslöfte: Börja släktforska"
April: Länka till "Påsklov-projekt med familjen"
Juli: Länka till "Sommarsemester på arkivet"
December: Länka till "Släktträdet som julklapp"
```

### Automatisering möjlig via:
- Datumbaserade regler
- Taggbaserad matchning
- Kategorirelationer
- Populäritet/trender

## Vanliga misstag

### 1. Överlänkning
**Problem**: Varje annat ord är en länk
**Lösning**: Max 1 länk per 100 ord

### 2. Irrelevanta länkar
**Problem**: Länka för länkandets skull
**Lösning**: Endast värdeadderande länkar

### 3. Samma ankartext
**Problem**: "Släktforskning" 10 gånger
**Lösning**: Varierat, naturligt språk

### 4. Döda länkar
**Problem**: 404-errors skadar UX
**Lösning**: Regelbunden länkkontroll

## Branschspecifika exempel

### Genealogi-sajt
```markdown
"När du hittat en intressant anfader i [[kyrkoböckerna]], 
kan det vara värt att kolla om personen finns i 
[[bouppteckningar]] eller [[domstolsprotokoll]]. 
Vår [[sökguide]] hjälper dig komma igång."
```

### Casino-affiliate
```markdown
"Förutom klassiska [[slots]] erbjuder moderna casinon 
även [[live casino]] och [[sportbetting]]. Läs vår 
[[nybörjarguide]] för att välja rätt speltyp."
```

### E-handel
```markdown
"Detta [[ekologiska kaffe]] passar perfekt till vår 
[[espressomaskin]]. Se även våra [[kundrecensioner]] 
och [[bryggguiden]] för bästa resultat."
```

## Verktyg och automation

### Rekommenderade verktyg
- Screaming Frog (länkkontroll)
- Ahrefs (internlänk-analys)
- Google Search Console (klickdata)

### Automation-möjligheter
```python
# Pseudo-kod för smart internlänkning
def suggest_internal_links(article):
    keywords = extract_keywords(article)
    related_content = find_related(keywords)
    return prioritize_by_value(related_content)
```

## Uppdatering och underhåll

### Månadsvis
- Kontrollera trasiga länkar
- Uppdatera säsongsbaserade länkar
- Analysera klickdata

### Kvartalsvis
- Revidera länkstrategi
- Uppdatera högvärdes-sidor
- A/B-test nya mönster

### Årsvis
- Total internlänk-audit
- Strategiutvärdering
- Konkurrenanalys

Denna playbook uppdateras kontinuerligt baserat på best practices och algoritmförändringar.
