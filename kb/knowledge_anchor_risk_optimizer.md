# Anchor Risk Optimizer Policy

## Översikt

Detta dokument definierar policyn för val av ankartyp och riskminimering i backlink-produktion. Målet är att skapa en naturlig och säker ankarprofil som maximerar SEO-värde utan att triggra spam-filter.

## Ankartyper

### 1. Exact Match (Exakt matchning)
- **Definition**: Ankartexten matchar exakt målsökordet
- **Exempel**: "casino" för att ranka på "casino"
- **Risknivå**: HÖG
- **Rekommenderad andel**: 5-15% av total portfolio
- **Användning**: Sparsamt, endast för högkvalitativa publikationer

### 2. Partial Match (Delvis matchning)
- **Definition**: Ankartexten innehåller målsökordet plus andra ord
- **Exempel**: "bästa casino online", "casino för nybörjare"
- **Risknivå**: MEDIUM
- **Rekommenderad andel**: 20-40% av total portfolio
- **Användning**: Primärt val för de flesta länkar

### 3. Brand (Varumärke)
- **Definition**: Ankartexten är varumärkesnamnet
- **Exempel**: "HappyCasino", "HappyCasino.se"
- **Risknivå**: LÅG
- **Rekommenderad andel**: 25-45% av total portfolio
- **Användning**: Säkraste valet, bygger varumärkeskännedom

### 4. Generic (Generisk)
- **Definition**: Allmänna fraser utan specifika sökord
- **Exempel**: "klicka här", "läs mer", "besök webbplatsen"
- **Risknivå**: LÅG
- **Rekommenderad andel**: 15-30% av total portfolio
- **Användning**: För naturlig variation

## Riskberäkning

### Formel för portfoliorisk
```
risk_score = (exact_ratio * 0.7) + ((1 - diversity_score) * 0.3)
```

### Risknivåer
- **LÅG** (0.0 - 0.3): Säker profil, kan öka exact match
- **MEDIUM** (0.3 - 0.6): Balanserad profil, underhåll nuvarande mix
- **HÖG** (> 0.6): Riskabel profil, minska exact match omedelbart

## Optimeringsregler

### Vid HÖG risk:
1. Stoppa alla nya exact match-länkar
2. Konvertera planerade exact till partial eller brand
3. Fokusera på brand och generic nästa 30 dagar

### Vid MEDIUM risk:
1. Begränsa exact match till max 1 av 10 nya länkar
2. Prioritera partial match för kommersiella sidor
3. Övervaka trendutveckling veckovis

### Vid LÅG risk:
1. Kan försiktigt öka exact match (max 20%)
2. Testa starkare ankarvarianter
3. Bibehåll minst 60% brand/generic för säkerhet

## Branschspecifika justeringar

### Reglerade branscher (gambling, finance, health):
- Reducera exact match med 50%
- Öka brand-fokus
- Alltid inkludera disclaimers

### Lokala företag:
- Inkludera geografiska modifierare
- "casino stockholm" istället för bara "casino"

### SaaS/Tech:
- Fokusera på feature-baserade ankare
- "projekthanteringsverktyg" istället för varumärke

## Kvalitetskontroll

### Innan publicering:
1. Kontrollera total portfoliobalans
2. Verifiera att risknivå är acceptabel
3. Säkerställ naturlig språkvariation
4. Undvik upprepning av exakt samma ankartext

### Månadsvis granskning:
1. Analysera portfolioutveckling
2. Identifiera överanvända ankare
3. Justera strategi baserat på resultat
4. Dokumentera förändringar

## Exempel på optimering

### Scenario: Ny kund med 0 länkar
1. Månad 1-2: 80% brand, 20% generic
2. Månad 3-4: 50% brand, 30% generic, 20% partial
3. Månad 5+: 40% brand, 25% generic, 25% partial, 10% exact

### Scenario: Existerande kund med hög exact-ratio
1. Omedelbar stopp för exact match
2. Nästa 20 länkar: 60% brand, 40% generic
3. Gradvis introduktion av partial efter normalisering

## Automatiska säkerhetsåtgärder

- Om exact_ratio > 30%: Blockera alla exact-förslag
- Om diversity < 0.5: Kräv manuell granskning
- Om konkurrent-ankar detekteras: Omedelbar avvisning

## Undantag

Undantag från denna policy kräver:
1. Dokumenterad affärsmotivering
2. Godkännande från SEO-ansvarig
3. Tidsbegränsad testperiod
4. Noggrann övervakning
