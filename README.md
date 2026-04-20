# health-journal

Persönliche Gesundheits-Tracking-App — in Entwicklung.

Langfristige Vision: konfigurierbares, template-basiertes **Personal Health Intelligence Framework** (Open Source ~2027).

## Aktueller Stand

**Phase 1 (laufend):** Integration aller 13 Module in eine lauffähige Single-File-App

- Alle 13 Modul-Prototypen funktionieren einzeln (siehe `/prototypes`)
- Integration in `app.html` läuft — einige Modals öffnen, Styling noch im Feinschliff
- Daten liegen aktuell in localStorage (Wechsel zu Supabase in Phase 2)

**Phase 2–4 (geplant):** Supabase-Backend (DE, GDPR) · PWA · Claude Vision Foto-Scanner für Nährwerte

## Dateien

- `app.html` — aktueller Integrations-Stand (v61)
- `modules_v8.json` — Konfiguration aller 13 Module
- `global_lp.js` — globaler Long-Press-Dispatcher
- `prototypes/` — Einzelmodul-Prototypen für Referenz und Neuaufbau

## Module

| Key | Modul |
|-----|-------|
| haut | Hautzustand pro Körperstelle, Foto, Pflege |
| med | Medikamente — Einnahme, Dosis, Uhrzeit |
| supp | Supplements-Stack |
| bef | Befinden — Energie, Stimmung, Konzentration, Brain Fog |
| entz | Entzündungsmarker (Finger, Gelenke, etc.) |
| get | Getränke — Wasser, Kaffee, Tee, Alkohol |
| ern | Ernährung mit Chips-System, Trigger-Tags |
| schmerz | Schmerz (Stelle, Intensität, Dauer) |
| stuhl | Stuhlgang (Bristol-Skala, Uhrzeit) |
| akt | Bewegung |
| regen | Regeneration, Schlaf |
| fam | Familie, soziales Umfeld |
| hyp | Hypothesen-Tracking |

## Offene nächste Schritte

1. Alle 13 Module im `app.html` vollständig integrieren (Modals, Styling, Long-Press-Aktionen)
2. **Einheitliche Import/Export-Logik** auf Tagesbasis (JSON) — wird implementiert wenn alle Module fertig sind
3. Lösch-/Korrekturfunktion für Einträge
4. Nasenspray-Tracking mit Links/Rechts/Beide
5. Dauer als Eingabetyp (manuell oder Start/Stop-Timer)

## Autor

Lars Schreiber — persönliches Projekt zur Selbstbeobachtung chronischer Entzündungserkrankungen.
