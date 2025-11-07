# Publisher Profiling Guide

## Översikt

Denna guide beskriver processen för att profilera publicister och anpassa innehåll efter deras unika röst, stil och policyer. Korrekt profilering säkerställer högre acceptansgrad och bättre innehållskvalitet.

## Profilkomponenter

### 1. Voice (Röst)

#### Tone (Ton)
- **formal**: Akademisk, professionell, distanserad
- **conversational**: Personlig, varm, direkt tilltal
- **academic**: Forskningsbaserad, källhänvisningar, facktermer
- **casual**: Avslappnad, humoristisk, vardaglig
- **professional**: Affärsmässig, saklig, branschspecifik

#### Perspective (Perspektiv)
- **first_person**: "Vi på Genline...", "Jag har upptäckt..."
- **third_person**: "Forskare har visat...", "Företaget erbjuder..."
- **mixed**: Kombination beroende på kontext

#### Style Markers (Stilmarkörer)
Exempel:
- "berättande" - Fokus på narrativ och personliga historier
- "informativ" - Faktadriven, utbildande
- "personlig" - Delar egna erfarenheter
- "analytisk" - Djupdykning, datadrivet
- "inspirerande" - Motiverande, positiv

### 2. LIX Range (Läsbarhetsindex)

- **very_easy** (< 30): Barnböcker, enkel information
- **easy** (30-40): Dagstidningar, populärvetenskap
- **medium** (40-50): Facktidskrifter, B2B-innehåll
- **hard** (50-60): Akademiska texter, juridik
- **very_hard** (> 60): Forskning, teknisk dokumentation

### 3. Policy (Publicistpolicy)

#### Länkattribut
- **nofollow**: true/false - Kräver rel="nofollow"
- **sponsored**: true/false - Kräver rel="sponsored"
- **ugc**: true/false - User Generated Content-märkning

#### Restrictions (Begränsningar)
- Maximalt antal utgående länkar per artikel
- Förbjudna ämnen/branscher
- Geografiska begränsningar
- Språkkrav

### 4. Examples (Exempelartiklar)

Samla 3-5 representativa artiklar som visar:
- Typisk struktur
- Vanliga ämnen
- Stil och ton
- Länkplacering

## Profileringsprocess

### Steg 1: Initial analys
1. Besök publicistens webbplats
2. Läs 10-15 slumpmässiga artiklar
3. Notera återkommande mönster

### Steg 2: Djupanalys

#### Innehållsanalys
- Genomsnittlig artikellängd
- Vanliga rubrikstrukturer
- Styckelängd och formatering
- Bildanvändning

#### Språkanalys
- Ordval och komplexitet
- Meningslängd
- Facktermer vs vardagsspråk
- Användning av engelska ord

#### Länkanalys
- Antal utgående länkar per artikel
- Placering av länkar
- Ankartext-stil
- Interna vs externa länkar

### Steg 3: Dokumentation

Skapa publicistprofil enligt följande mall:

```yaml
domain: exempel.se
voice:
  tone: conversational
  perspective: mixed
  style_markers:
    - berättande
    - personlig
    - lokalförankrad
lix_range: easy
policy:
  nofollow: false
  sponsored: true
  ugc: false
  restrictions:
    - "Max 3 externa länkar per artikel"
    - "Inga casino/betting utan svensk licens"
    - "Endast skandinaviskt innehåll"
examples:
  - url: https://exempel.se/artikel1
    title: "Så lyckas du med..."
    excerpt: "Inledning som visar ton..."
```

## Vanliga publicisttyper

### 1. Lokaltidning
- Ton: Informativ, lokalförankrad
- LIX: Easy
- Policy: Strikt källkontroll, lokalt fokus

### 2. Branschblogg
- Ton: Professionell, insiktsfull
- LIX: Medium
- Policy: Thought leadership, inga konkurrenter

### 3. Livsstilsmagasin
- Ton: Inspirerande, personlig
- LIX: Easy-Medium
- Policy: Visuellt fokus, positiv vinkel

### 4. Företagsblogg
- Ton: Professionell, säljstödjande
- LIX: Medium
- Policy: Varumärkesbyggande, CTA-fokus

### 5. Hobbyforum
- Ton: Entusiastisk, community-driven
- LIX: Varierar
- Policy: Användargenererat, moderation

## Kvalitetssäkring

### Checklistor per publicisttyp

#### Nyhetssajt
- [ ] Objektiv ton
- [ ] Källhänvisningar
- [ ] Aktuell vinkel
- [ ] Balanserad framställning

#### Företagsblogg
- [ ] Varumärkesröst
- [ ] Värdeskapande innehåll
- [ ] Subtil säljvinkel
- [ ] Professionell ton

#### Nischblogg
- [ ] Djup expertis
- [ ] Communityspråk
- [ ] Detaljrikedom
- [ ] Passion för ämnet

## Uppdatering och underhåll

### Månadsvis granskning
1. Kontrollera om publicisten ändrat stil
2. Uppdatera exempelartiklar
3. Justera LIX om nödvändigt

### Kvartalsvis djupanalys
1. Ny komplett profilering
2. Jämför med tidigare profil
3. Dokumentera förändringar
4. Uppdatera skrivmallar

## Varningssignaler

### Indikationer på profiländring:
- Ny chefredaktör/ägare
- Redesign av webbplats
- Ändrad publiceringsfrekvens
- Nya innehållskategorier
- Ändrade länkpolicyer

### Åtgärder vid förändring:
1. Pausa pågående produktion
2. Genomför ny profilering
3. Uppdatera alla mallar
4. Informera skribenter

## Best Practices

1. **Överanpassa hellre än underanpassa** - Bättre att vara för lik publicisten än för olik
2. **Studera kommentarsfält** - Visar läsarnas språk och förväntningar
3. **Följ säsongsvariationer** - Många publicister ändrar ton efter säsong
4. **Respektera nischspråk** - Använd branschtermer korrekt
5. **Kvalitet över kvantitet** - Färre, bättre anpassade artiklar
