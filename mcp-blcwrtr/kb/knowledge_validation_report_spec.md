# Validation Report Specification

## Översikt

Detta dokument specificerar strukturen och innehållet för QC-valideringsrapporter som genereras av systemet.

## Rapportstruktur

### 1. Status

Rapporten måste alltid innehålla en övergripande status:

- **APPROVED**: Score >= 85, inga kritiska problem
- **LIGHT_EDITS**: Score >= 70, mindre justeringar behövs
- **BLOCKED**: Score < 70 eller kritiska fel

### 2. Scoring (0-100)

Total poäng beräknas som viktad summa:

```
total_score = Σ(category_score * category_weight)
```

#### Kategorivikter:
- **preflight**: 0.25 (Följer preflight-instruktioner)
- **draft**: 0.15 (Allmän innehållskvalitet)
- **anchor**: 0.20 (Länkplacering och strategi)
- **trust**: 0.15 (Trovärdighetssignaler)
- **lsi**: 0.15 (Semantisk relevans)
- **fit**: 0.05 (Röst och ton)
- **compliance**: 0.05 (Branschkrav)

### 3. Issues (Problem)

Varje issue måste innehålla:

```json
{
  "type": "error|warning|info",
  "category": "anchor|trust|lsi|compliance|structure|content",
  "code": "SPECIFIC_ERROR_CODE",
  "message": "Beskrivning av problemet",
  "location": {
    "section": "Sektionsnamn",
    "paragraph": 2,
    "sentence": 1
  }
}
```

#### Felkoder

**Anchor-relaterade:**
- `ANCHOR_NOT_FOUND`: Målankare saknas helt
- `ANCHOR_IN_HEADER`: Ankare placerad i rubrik (kritiskt)
- `ANCHOR_PLACEMENT_WRONG`: Fel sektion eller paragraf
- `ANCHOR_TOO_DEEP`: För långt ner i innehållet
- `MISSING_PRIMARY_ANCHOR`: Primär ankartext matchar inte

**Trust-relaterade:**
- `MISSING_TRUST_SIGNALS`: Inga trovärdiga källor
- `INSUFFICIENT_TRUST_SIGNALS`: För få källor
- `ERR_TRUST_COMPETITOR`: Länk till konkurrent

**LSI-relaterade:**
- `INSUFFICIENT_LSI_TERMS`: <6 termer nära ankare
- `EXCESSIVE_LSI_TERMS`: >10 termer (överoptimering)
- `LSI_OVERUSE`: Term använd >2 gånger
- `ANCHOR_NOT_FOUND_FOR_LSI`: Kan inte validera LSI

**Compliance-relaterade:**
- `MISSING_GAMBLING_DISCLAIMER`: Spelansvar saknas
- `MISSING_FINANCE_DISCLAIMER`: Finansiell friskrivning saknas
- `MISSING_HEALTH_DISCLAIMER`: Medicinsk friskrivning saknas
- `ERR_COMPLIANCE`: Allmänt compliance-fel

**Struktur-relaterade:**
- `INSUFFICIENT_SECTIONS`: <3 sektioner
- `EMPTY_SECTION`: Sektion utan innehåll
- `WORD_COUNT_MISMATCH`: Avviker >20% från mål

### 4. Auto-fixes

Om auto_fix=true, dokumentera försök:

```json
{
  "type": "add_disclaimer|move_link|change_anchor|inject_lsi|add_trust",
  "description": "Vad som gjordes",
  "applied": true|false
}
```

Max 1 auto-fix per validering (AUTO_FIX_ONCE).

### 5. Recommendations

Prioriterad lista med åtgärdsförslag:
- Mest kritiska problem först
- Konkreta, handlingsbara råd
- Max 4 rekommendationer

### 6. Human Signoff Required

Boolean som indikerar om mänsklig granskning krävs:
- `true` vid: ANCHOR_IN_HEADER, ERR_TRUST_COMPETITOR, ERR_COMPLIANCE
- `true` vid: någon kategori <50 poäng
- `true` vid: 0 godkända trust-källor

### 7. Next Actions

Lista med konkreta nästa steg baserat på status:
- **APPROVED**: "Proceed to delivery"
- **LIGHT_EDITS**: Specifika redigeringsåtgärder
- **BLOCKED**: Kritiska problem som måste lösas

## Exempel på Komplett Rapport

```json
{
  "status": "LIGHT_EDITS",
  "score": 78.5,
  "breakdown": {
    "preflight": 90,
    "draft": 85,
    "anchor": 70,
    "trust": 60,
    "lsi": 80,
    "fit": 90,
    "compliance": 100
  },
  "issues": [
    {
      "type": "warning",
      "category": "anchor",
      "code": "ANCHOR_PLACEMENT_WRONG",
      "message": "Ankare bör vara i mittpunkt, hittades i introduktion",
      "location": {
        "section": "Introduktion",
        "paragraph": 3
      }
    },
    {
      "type": "error",
      "category": "trust",
      "code": "INSUFFICIENT_TRUST_SIGNALS",
      "message": "Endast 1 av 2 förväntade trust-signaler hittades"
    }
  ],
  "auto_fixes": [],
  "recommendations": [
    "Flytta ankarlänken till mittpunktssektionen",
    "Lägg till referens till ytterligare en trovärdig källa",
    "Överväg att lägga till fler LSI-termer nära ankaret"
  ],
  "human_signoff_required": false,
  "next_actions": [
    "Apply recommended edits",
    "Re-run QC validation"
  ]
}
```

## Valideringslogik

### Kritiska Fel (Blockerar alltid)
1. Ankare i rubrik
2. Länk till konkurrent
3. Saknad compliance i reglerad bransch
4. Total poäng <70

### Varningar (Kräver uppmärksamhet)
1. Fel ankarparagraf (men rätt sektion)
2. För få LSI-termer (4-5 istället för 6+)
3. Endast 1 trust-signal
4. Ordantal avviker 10-20%

### Info (Förbättringsförslag)
1. Suboptimal mångfald i ankarprofil
2. Möjlighet att lägga till schema markup
3. Internlänkningsmöjligheter

## Felkodshierarki

```
ERR_* = Kritiska fel
MISSING_* = Saknade obligatoriska element  
INSUFFICIENT_* = Under minimikrav
EXCESSIVE_* = Över maxgränser
WRONG_* = Felaktig placering/användning
```

## Integration med State Machine

Valideringsrapporten används för att avgöra nästa steg:

- **APPROVED** → DELIVER
- **LIGHT_EDITS** → EDITOR_GATE → WRITE (med fixes)
- **BLOCKED** → RESCUE_* eller ABORT

## Loggning

Alla valideringsrapporter loggas till audit_log med:
- order_ref
- validation_timestamp
- score
- status
- critical_issues[]
- auto_fixes_applied[]
