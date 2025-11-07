# Schema Patterns Guide

## Översikt

Strukturerad data (JSON-LD) hjälper sökmotorer förstå innehållet bättre och kan generera rich snippets. Denna guide definierar när och hur olika schema-typer ska föreslås i backlink-content.

## När ska schema föreslås?

### Automatiskt föreslå
- HowTo-innehåll med tydliga steg
- FAQ med fråga/svar-format
- Recensioner med betyg
- Listor med rankningar
- Event med datum/plats

### Överväg att föreslå
- Produktbeskrivningar
- Lokala företag
- Personer/författare
- Kurser/utbildningar

### Föreslå inte
- Kort content (<300 ord)
- Generella artiklar utan struktur
- Nyhetsinlägg
- Kategorisidor

## Schema-typer och användning

### 1. HowTo Schema

**När används**: Steg-för-steg guider
**Krav**: Minst 2 steg, tydligt resultat

```json
{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "Hur du börjar släktforska",
  "description": "En komplett guide för att komma igång med släktforskning",
  "totalTime": "PT30M",
  "estimatedCost": {
    "@type": "MonetaryAmount",
    "currency": "SEK",
    "value": "0"
  },
  "supply": [
    {
      "@type": "HowToSupply",
      "name": "Dator med internet"
    },
    {
      "@type": "HowToSupply", 
      "name": "Anteckningsbok"
    }
  ],
  "step": [
    {
      "@type": "HowToStep",
      "text": "Börja med dig själv och dokumentera vad du vet",
      "name": "Dokumentera känd information"
    },
    {
      "@type": "HowToStep",
      "text": "Intervjua äldre släktingar om familjehistorien",
      "name": "Samla muntliga källor"
    }
  ]
}
```

### 2. FAQ Schema

**När används**: Vanliga frågor med svar
**Krav**: Minst 2 fråga/svar-par

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Är släktforskning gratis?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Ja, många källor som Riksarkivet och FamilySearch är helt gratis. Vissa tjänster som Ancestry kräver prenumeration."
      }
    },
    {
      "@type": "Question",
      "name": "Hur långt bakåt kan man forska?",
      "acceptedAnswer": {
        "@type": "Answer", 
        "text": "I Sverige finns kyrkoböcker från cirka 1600-talet, men det varierar mellan församlingar."
      }
    }
  ]
}
```

### 3. ItemList Schema

**När används**: Rankade listor, top-X
**Krav**: Numrerad ordning, konsistent format

```json
{
  "@context": "https://schema.org",
  "@type": "ItemList",
  "name": "Top 5 svenska casinon 2024",
  "description": "De bästa online casinon med svensk licens",
  "numberOfItems": 5,
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "item": {
        "@type": "Organization",
        "name": "Casino #1",
        "description": "Bäst välkomstbonus"
      }
    }
  ]
}
```

### 4. Article Schema

**När används**: Redaktionellt innehåll
**Krav**: Författare, datum, huvudbild

```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Digitala verktyg revolutionerar släktforskningen",
  "author": {
    "@type": "Person",
    "name": "Anna Andersson"
  },
  "datePublished": "2024-01-15",
  "dateModified": "2024-01-20",
  "image": "https://example.com/article-image.jpg",
  "publisher": {
    "@type": "Organization",
    "name": "Genline",
    "logo": {
      "@type": "ImageObject",
      "url": "https://genline.se/logo.png"
    }
  }
}
```

### 5. Review Schema

**När används**: Recensioner med betyg
**Krav**: Numeriskt betyg, recenserad item

```json
{
  "@context": "https://schema.org",
  "@type": "Review",
  "itemReviewed": {
    "@type": "Product",
    "name": "Ancestry DNA-test"
  },
  "author": {
    "@type": "Person",
    "name": "Erik Eriksson"
  },
  "reviewRating": {
    "@type": "Rating",
    "ratingValue": "4",
    "bestRating": "5"
  },
  "reviewBody": "Enkelt att använda och snabba resultat..."
}
```

## Branschspecifika mönster

### Genealogi/Släktforskning

#### Dataset Schema för arkivsamlingar
```json
{
  "@context": "https://schema.org",
  "@type": "Dataset",
  "name": "Kyrkoböcker Skåne 1700-1900",
  "description": "Digitaliserade kyrkoböcker från Skåne län",
  "creator": {
    "@type": "Organization",
    "name": "Riksarkivet"
  },
  "distribution": {
    "@type": "DataDownload",
    "encodingFormat": "PDF",
    "contentUrl": "https://exempel.se/dataset"
  }
}
```

#### Event Schema för släktforskardagar
```json
{
  "@context": "https://schema.org",
  "@type": "Event",
  "name": "Släktforskardagarna 2024",
  "startDate": "2024-08-23",
  "endDate": "2024-08-25",
  "location": {
    "@type": "Place",
    "name": "Uppsala Konsert & Kongress"
  }
}
```

### Casino/Gambling

#### Game Schema för spelrecensioner
```json
{
  "@context": "https://schema.org",
  "@type": "VideoGame",
  "name": "Mega Fortune",
  "gamePlatform": "Web browser",
  "applicationCategory": "Game",
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.5",
    "ratingCount": "1250"
  }
}
```

#### Offer Schema för bonusar
```json
{
  "@context": "https://schema.org",
  "@type": "Offer",
  "name": "Välkomstbonus 100% upp till 1000 kr",
  "category": "Casino Bonus",
  "availability": "https://schema.org/InStock",
  "price": "0",
  "priceCurrency": "SEK",
  "eligibleRegion": {
    "@type": "Country",
    "name": "SE"
  }
}
```

## Implementation i content

### Inline-markering för skribenter

```markdown
## Hur du börjar släktforska [SCHEMA:HowTo]

### Steg 1: Dokumentera känd information
Börja med att skriva ner allt du redan vet...

### Steg 2: Intervjua släktingar  
Prata med äldre familjemedlemmar...

[SCHEMA:TotalTime:PT2H]
[SCHEMA:EstimatedCost:0 SEK]
```

### FAQ-markering

```markdown
## Vanliga frågor [SCHEMA:FAQ]

**Fråga: Är släktforskning dyrt?**
Svar: Många källor är helt gratis...

**Fråga: Behöver jag särskild utbildning?**
Svar: Nej, alla kan börja släktforska...
```

## Validering och kvalitet

### Obligatoriska fält per schema

#### HowTo
- [ ] name
- [ ] step (minst 2)
- [ ] description

#### FAQ  
- [ ] Minst 2 frågor
- [ ] Kompletta svar
- [ ] Frågeformat konsistent

#### ItemList
- [ ] Numrerad ordning
- [ ] position för varje item
- [ ] name för listan

### Kvalitetskrav

1. **Relevans**: Schema måste matcha innehållet exakt
2. **Fullständighet**: Alla obligatoriska fält ifyllda
3. **Korrekthet**: Validerar mot schema.org
4. **Värde**: Tillför användarnytta

## Verktyg för validering

### Online-verktyg
- Google Rich Results Test
- Schema.org Validator
- Structured Data Testing Tool

### Automatisk validering
```python
# Pseudo-kod för schema-validering
def validate_schema(json_ld):
    required_fields = get_required_fields(json_ld["@type"])
    for field in required_fields:
        if field not in json_ld:
            return False, f"Missing required field: {field}"
    return True, "Valid"
```

## Best Practices

### DO's
- ✅ Använd schema som matchar innehållet perfekt
- ✅ Inkludera alla rekommenderade fält
- ✅ Validera före publicering
- ✅ Uppdatera schema vid innehållsändringar
- ✅ Använd unika ID:n för items

### DON'Ts
- ❌ Tvinga in schema som inte passar
- ❌ Duplicera schema på samma sida
- ❌ Inkludera osynligt innehåll
- ❌ Överdriva ratings/reviews
- ❌ Glömma uppdatera vid ändringar

## Mätning av impact

### KPIs att följa
- Rich snippet appearances
- CTR-förbättring
- SERP-positioner
- User engagement

### A/B-testing
```markdown
Version A: Utan schema
Version B: Med HowTo schema
Mät: CTR, dwell time, conversions
```

## Framtida schema-typer

### Under utveckling
- LearningResource (kurser)
- SpecialAnnouncement (viktiga uppdateringar)
- VirtualLocation (online-events)

### Branschspecifika möjligheter
- GenealogyRecord (släktdata)
- GamblingOffer (spelbonusar)
- FinancialProduct (lån/kort)

## Uppdateringsrutiner

### Vid innehållsändring
1. Kontrollera om schema fortfarande matchar
2. Uppdatera relevanta fält
3. Re-validera
4. Deploy

### Schema.org uppdateringar
- Bevaka nya schema-typer
- Testa beta-funktioner
- Implementera när stabila

Denna guide uppdateras kontinuerligt när nya schema-möjligheter blir tillgängliga.
