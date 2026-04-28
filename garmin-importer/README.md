# Garmin → Supabase Importer

Einmaliger Import deiner Garmin-Connect-Daten ins Health-Journal.

## Voraussetzungen

- Python 3.9+
- Garmin Connect Account mit deiner Instinct 2
- Health-Journal Account (Email + Passwort)

## Installation

Im Terminal auf deinem Computer:

```bash
cd /pfad/zu/health-journal/garmin-importer

# Virtual env (empfohlen)
python3 -m venv venv
source venv/bin/activate    # macOS/Linux
# oder: venv\Scripts\activate  # Windows

# Dependencies
pip install garminconnect requests
```

## Ausführen

```bash
python garmin_import.py
```

**Beim ersten Start:**
1. Du wirst nach **Garmin-Email + Passwort** gefragt
2. Bei aktiver MFA: kommt der **Code per SMS/App** und wird eingegeben
3. Garmin-Tokens werden in `~/.garminconnect` gecacht (für die nächsten Aufrufe)
4. Du wirst nach deinen **Health-Journal-Credentials** gefragt
5. Skript läuft durch — kann **15-25 Minuten** dauern bei 12 Monaten,
   weil pro Tag mehrere API-Calls gemacht werden müssen
6. Garmin hat **Rate-Limits** — falls Fehler kommen einfach Skript erneut starten,
   die schon importierten Tage werden übersprungen (UPSERT)

## Was wird importiert?

**Pro Tag** (`garmin_taeglich`):
- Schlafzeiten, Schlafdauer, Schlafphasen (Tief/Leicht/REM/Wach), Schlafscore
- HRV (7-Tage-Avg + letzte Nacht + Status)
- Ruhepuls, max/avg HF
- Stress (avg/max + Minuten in jeder Zone)
- Body Battery (max/min + Auf-/Entladung)
- Schritte, Distanz, Kalorien, Intensitätsminuten, Etagen
- Training Readiness (Score + Status)
- VO2max
- Atemfrequenz

**Workouts:** werden NICHT importiert — Krafttraining kommt aus Strong (separater Importer geplant). Cardio über Garmin könnte später nachgezogen werden falls relevant.

## Mehrfaches Ausführen

Sicher — UPSERT-Logik. Bei jeder Ausführung werden:
- **Existierende Tage überschrieben** (mit aktuellsten Garmin-Daten)
- **Fehlende Tage ergänzt**

So kannst du das Skript einfach jeden Monat erneut laufen lassen.

## Konfiguration

Im Skript oben sind:
- `MONATE_RUECKWAERTS = 12` — Zeitraum anpassen
- `SUPABASE_URL` und `SUPABASE_ANON_KEY` — schon richtig gesetzt

## Sicherheit

- Garmin-Login: Tokens lokal im `~/.garminconnect` gespeichert, niemals in Cloud
- Health-Journal-Login: Token nur im Skript-RAM, wird nach Beendigung weggeworfen
- Alle Datenbank-Calls gehen mit deinem User-Token, RLS sorgt dafür dass du nur eigene Daten sehen/schreiben kannst

## Troubleshooting

**"FEHLER: garminconnect nicht installiert"**
→ `pip install garminconnect`

**"MFA-Code"-Prompt erscheint**
→ Code in deiner Authenticator-App oder per SMS

**"Login-Fehler" bei Garmin**
→ Garmin-Webseite öffnen, einmal manuell einloggen, dann Skript erneut starten.
   Garmin macht manchmal Captcha-Checks.

**Rate-Limit-Fehler ("Too Many Requests")**
→ 30 Min warten, dann erneut. Schon importierte Tage werden übersprungen.

**"Token-Cache veraltet"**
→ Normal nach mehreren Monaten. Skript bittet dann um frischen Login.
