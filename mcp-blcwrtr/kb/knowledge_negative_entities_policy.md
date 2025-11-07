# Negative Entities Policy

## Översikt

Denna policy definierar hur vi identifierar, blockerar och hanterar negativa entiteter som kan skada SEO-värdet eller varumärkesassociationer. Särskilt fokus ligger på att undvika länkar till eller omnämnanden av konkurrenter.

## Definition av negativa entiteter

### Kategori 1: Direkta konkurrenter
**Risknivå**: KRITISK
- Företag som erbjuder identiska tjänster till samma målgrupp
- Varumärken som rankar på samma sökord
- Domäner listade i competitor_registry

**Åtgärd**: Totalblockering - ingen länkning eller positiv omnämning

### Kategori 2: Indirekta konkurrenter
**Risknivå**: HÖG
- Företag i närliggande branscher
- Substitutprodukter eller -tjänster
- Potentiella framtida konkurrenter

**Åtgärd**: Försiktig hantering - endast neutral omnämning om nödvändigt

### Kategori 3: Negativa associationer
**Risknivå**: MEDIUM
- Skandaldrabbade varumärken
- Företag med dåligt rykte
- Kontroversiella organisationer

**Åtgärd**: Undvik helt om möjligt

### Kategori 4: Spam/Lågkvalitet
**Risknivå**: MEDIUM
- Kända länkfarmer
- PBN-nätverk
- Straffade domäner

**Åtgärd**: Aldrig länka eller referera

## Identifieringsprocess

### Automatisk screening
```python
# Pseudo-kod för konkurrentdetektion
negative_entities = [
    # Direkta konkurrenter (exempel för casino-bransch)
    "betsson.com", "leovegas.com", "unibet.com",
    "casinoguide.se", "bettingexpert.com",
    
    # Varumärkesvariationer
    "*casino*guide*", "*betting*expert*",
    
    # Negativa associationer
    "scam", "bluff", "bedrägeri"
]

def check_negative_entity(text, url=None):
    for entity in negative_entities:
        if entity in text.lower():
            return True, f"Negative entity detected: {entity}"
    return False, "Clean"
```

### Manuell granskning triggers
1. Alla nya domäner som inte finns i trust_registry
2. Varumärken med .com/.se som inte är kunden
3. Spelrelaterade termer + "guide/tips/expert"
4. Finansiella tjänster utan svensk licens

## Branschspecifika listor

### Casino/Gambling
```yaml
block_always:
  - competitors: ["leovegas", "betsson", "unibet", "mrgreen"]
  - comparison_sites: ["casinoguide", "bettingexpert", "casinopro"]
  - unlicensed: ["*utan-svensk-licens*", "*offshore*"]
  
monitor_closely:
  - affiliates: ["askgamblers", "casinomeister"]
  - news: ["casinonyheter", "spelbranschen"]
```

### Genealogi/Släktforskning
```yaml
block_always:
  - competitors: ["ancestry", "myheritage", "familysearch"]
  - paid_services: ["geneanet", "findmypast"]
  
allow_neutral_mention:
  - free_resources: ["riksarkivet", "arkivdigital"]
  - tools: ["gramps", "familytreemaker"]
```

### E-handel
```yaml
block_always:
  - marketplaces: ["amazon", "wish", "aliexpress"]
  - direct_competitors: [baserat på kundens bransch]
  
case_by_case:
  - payment: ["klarna", "paypal"] # OK om kunden använder
  - logistics: ["postnord", "dhl"] # OK i praktisk kontext
```

## Hanteringsstrategier

### Vid upptäckt före publicering

1. **Länk till konkurrent**
   - Byt till neutral källa
   - Använd branschorganisation istället
   - Referera till myndighet

2. **Omnämnande av konkurrent**
   - Omformulera till generiska termer
   - "Vissa aktörer" istället för specifikt namn
   - Fokusera på kundens USP istället

3. **Jämförande innehåll**
   - Aldrig jämför direkt med konkurrent
   - Använd "till skillnad från många andra"
   - Framhäv kundens fördelar isolerat

### Vid upptäckt efter publicering

1. **Prioritet 1** (inom 24h)
   - Konkurrentlänkar
   - Negativa varumärkesassociationer
   - Regelbrott

2. **Prioritet 2** (inom 72h)
   - Indirekta konkurrenter
   - Tveksamma omnämnanden
   - Gränsfall

3. **Prioritet 3** (vid nästa uppdatering)
   - Optimeringsmöjligheter
   - Förtydliganden
   - Styrkande av positiv vinkel

## Exempel på korrekt hantering

### ❌ FEL: Direkt jämförelse
```
"Till skillnad från LeoVegas erbjuder HappyCasino bättre bonusar..."
```

### ✅ RÄTT: Indirekt positionering
```
"HappyCasino utmärker sig genom marknadens mest generösa välkomstbonus..."
```

### ❌ FEL: Länk till konkurrent
```
"Enligt [Casinoguides recension] är denna typ av spel populär..."
```

### ✅ RÄTT: Neutral källa
```
"Enligt Spelinspektionens statistik är denna typ av spel populär..."
```

## Whitelist-undantag

### Alltid tillåtna
- Myndigheter (Spelinspektionen, Riksarkivet, etc.)
- Ideella organisationer (Stödlinjen, Spelberoendes förening)
- Neutrala nyhetsmedier (DN, SVT, etc.)
- Akademiska institutioner

### Kontextberoende tillåtna
- Branschorganisationer (om kunden är medlem)
- Leverantörer (om kunden använder)
- Partners (med skriftligt godkännande)

## Kvalitetskontroll

### Pre-publicering checklist
- [ ] Kör automatisk negative entity scan
- [ ] Manuell granskning av alla externa länkar
- [ ] Verifiera att inga konkurrenter nämns
- [ ] Kontrollera indirekt språk

### Post-publicering monitoring
- Veckovis: Sök efter kundens varumärke + konkurrentnamn
- Månadsvis: Fullständig länkaudit
- Kvartalsvis: Uppdatera negative entities lista

## Eskalering

### Nivå 1: Automatisk blockering
- Systemet blockerar kända negativa entiteter
- Logg till audit_trail
- Notifikation till QC-team

### Nivå 2: Manuell granskning
- QC-team bedömer gränsfall
- Dokumenterar beslut
- Uppdaterar policy vid behov

### Nivå 3: Kundeskalering
- Vid tveksamheter kontaktas kunden
- Skriftligt godkännande för undantag
- Arkiveras i kundmapp

## Uppdateringsrutiner

### Veckovis
- Lägg till nya konkurrenter från kundfeedback
- Uppdatera spam-domäner från branschlistor

### Månadsvis
- Granska false positives
- Justera regex-patterns
- Uppdatera branschspecifika listor

### Kvartalsvis
- Fullständig genomgång av policy
- Benchmark mot branschstandard
- Implementera nya detektionsmetoder

## Träning och kommunikation

### För skribenter
- Obligatorisk genomgång vid onboarding
- Kvartalsvis uppdatering om ändringar
- Tillgång till aktuella block-listor

### För QC-team
- Fördjupad träning i gränsfallsbedömning
- Befogenhet att uppdatera listor
- Ansvar för kunskapsdelning

### För kundteam
- Kunna förklara policy för kunder
- Hantera förfrågningar om undantag
- Dokumentera kundspecifika krav

## Mätning och förbättring

### KPIs
- Antal blockerade negativa entiteter/månad
- False positive rate
- Tid från upptäckt till åtgärd
- Kundnöjdhet med hantering

### Förbättringsområden
1. Automatisering av detektion
2. ML-baserad sentimentanalys
3. Real-time monitoring
4. Proaktiv konkurrentbevakning

Denna policy är levande och uppdateras kontinuerligt baserat på nya hot och möjligheter.
