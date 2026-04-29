# health-journal

Persönliches Gesundheits-Tracking zur Selbstbeobachtung chronischer Entzündungen — in Entwicklung.

Langfristige Vision: konfigurierbares, template-basiertes **Personal Health Intelligence Framework** (Open Source ~2027). Später optional als Hosted Service mit KI-Analyse und B2B-Lizenzierung für Coaches und Nutritionisten.

> Hinweis: Template-Namen beschreiben Behavior, nicht Krankheiten (MDR-Vermeidung in Deutschland).

## Aktueller Stand

**Phase 1 — Integration aller 14 Module: weitgehend abgeschlossen.** Alle Module sind in `app.html` integriert und funktional. Polish-Punkte teilweise noch offen.

**Phase 2 — Persistenz & Backend** (anstehend): Wechsel von `localStorage` zu Supabase (Frankfurt-Region, GDPR), Auth, Schema-Design, Migration.

**Phase 3 — PWA**: Manifest, Service Worker, iPhone-Installation.

**Phase 4 — Foto-Scanner für Zutatenlisten**: Claude Vision Integration für automatische Nährwert-Extraktion.

**Phase 5 — KI-gestützte Trend-Analyse über Hautfotos & Daten**: Auswertungs-Modul in der App, das eingelagerte Hautfotos zusammen mit Modul-Daten (Score-Kategorien, Anker/Region/Tag), Garmin-Werten (Stress/Schlaf/HRV) und Notizen über Zeiträume hinweg an die Claude API schickt. Ziel: Trend-Erkennung statt Einzelbild-Bewertung — "Achsel vor 3 Wochen vs. heute, in Kombination mit Ernährung, Schlaf und Stress". Voraussetzung: konsistente Foto-Bedingungen (gleiches Licht, gleiche Stelle) — Lars dokumentiert das in seinem Routine-Setup. API-Key bleibt bei Lars (kein Anthropic-Backend), damit Privacy-Vision erhalten bleibt.

## Module (14)

| Key | Modul | Besonderheit |
|-----|-------|--------------|
| med | Medikamente | Einnahme, Dosis, Uhrzeit; Sub-Optionen (z.B. Nasenspray L/R/Beide) |
| supp | Supplements | Stack-basiert nach Tageszeit |
| haut | Hautzustand | 0–5 Skala pro Körperstelle, Pflegeprodukte |
| bef | Befinden | Energie, Stimmung, Konzentration, Brain Fog — Episoden mit Start/Endzeit |
| entz | Entzündungsmarker | Finger, Gelenke; Spontan-Erfassung |
| get | Getränke | Wasser, Kaffee, Tee, Alkohol — Menge & Uhrzeit |
| ern | Ernährung | Chips-System mit Suchfeld, Trigger-Tags, Zutaten-Tracking |
| schmerz | Schmerz | Region, Intensität, Allodynie pro Region, Episoden mit Start/Endzeit |
| stuhl | Stuhlgang | Bristol-Skala 1–7 in 0.5er-Schritten |
| akt | Aktivität/Bewegung | Art, Dauer, Intensität |
| regen | Regeneration | Meditation, Atemübungen, Nurosym etc. |
| **messw** | **Messwerte** | **Basaltemperatur, Blutdruck (mit ESH-Kategorisierung), Gewicht** |
| fam | Familie/Soziales | Stimmung im Umfeld |
| hyp | Hypothesen | Hypothesen-Lifecycle (offen/bestätigt/widerlegt/angepasst) |

Plus übergreifend:

- **Notizen-System** mit Floating Action Button (📝): Beobachtung / Hypothese / Frage — Quick-Capture von überall, eigener Tab "Notizen"

## Highlights der UX

- **Recall-Bias-Schutz** bei Episoden (Schmerz/Befinden): Beim Beenden ist nicht "jetzt" der Default, sondern "vor 30 Min" — weil das Verschwinden meist später bemerkt wird als das tatsächliche Ende
- **Live-Counter** für offene Episoden ("läuft seit 2h 14min")
- **Smart-Eingabe** für Messwerte: "365" → 36,5°C; "824" → 82,4 kg
- **Editierbare Einträge**: Bleistift-Icon (✎) bei jedem Eintrag öffnet Edit-Modal
- **iOS-PWA-Support**: Safe-Area-Inset für Statusleiste

## Repo-Struktur

```
health-journal/
├── README.md                    # dieses Dokument
├── app.html                     # Haupt-App (Single-File HTML/JS/CSS)
├── modules_v8.json              # Modul-Konfiguration (Referenz)
├── global_lp.js                 # globaler Long-Press-Dispatcher
├── robots.txt                   # Disallow all
├── .gitignore
└── prototypes/                  # Einzelmodul-Prototypen
```

## Tech-Stack

- **Frontend:** Single-File HTML/JS/CSS (bewusste Wahl für Einfachheit)
- **Styling:** Vanilla CSS mit CSS-Variablen für Theming (Light/Dark)
- **Daten:** aktuell `localStorage`, Migration zu Supabase in Phase 2
- **Hosting:** GitHub Pages (privates Repo)
- **Wearable:** geplant via Garmin (Python-Pipeline lokal, keine Apple Health — Privacy)

## Wissenschaftliche Grundannahmen (für Tracking-Design)

- **Linker kleiner Finger** als zuverlässiger systemischer Entzündungsmarker
- **Knie-Unbehagen im Schneidersitz** als Inflammationsindikator (nicht Alter)
- **Muskelkrämpfe bei Belastung** als Entzündungssignal (nicht Fitness-/Elektrolyt-Problem)
- **Omega-3 braucht Fett-Co-Einnahme** für Bioverfügbarkeit
- **Post-Terzolin-Rötung** ist Herxheimer-artige Die-off-Reaktion

## Offene Phase-1-Punkte

- Konsistenz weiterer UI-Elemente (Modal-Buttons, Listen-Layouts)
- Selection-Felder als Custom-Eingabe (Tag-Manager-Pattern auf alle Module ausweiten — bei Getränke bereits vorhanden)

## Workflow-Regeln

- **Kein Push ohne explizite Absprache**
- Kein Deploy auf GitHub Pages ohne Absprache
- Session-basiertes Arbeiten

## Autor

Lars Schreiber — persönliches Projekt zur Selbstbeobachtung chronischer Entzündungserkrankungen.
