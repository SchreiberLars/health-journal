#!/usr/bin/env python3
"""
Garmin → Supabase Importer
Einmaliger Import deiner Garmin-Connect-Daten in das Health-Journal.

Anwendung:
    python garmin_import.py
    
Beim ersten Aufruf wirst du nach Garmin-Login + Supabase-App-Login gefragt.
Garmin-Tokens werden lokal gecacht (~/.garminconnect), Supabase-Token ist
sessionsbasiert und lebt nur im Skript.

Konfiguration unten anpassen.
"""

import os
import sys
import getpass
import json
from datetime import date, timedelta, datetime, timezone
from pathlib import Path

try:
    from garminconnect import Garmin
    from garth.exc import GarthHTTPError
except ImportError:
    print("FEHLER: garminconnect nicht installiert.")
    print("Installier mit: pip install garminconnect")
    sys.exit(1)

try:
    import requests
except ImportError:
    print("FEHLER: requests nicht installiert.")
    print("Installier mit: pip install requests")
    sys.exit(1)


# ═══════════════════════════════════════════
# KONFIGURATION
# ═══════════════════════════════════════════
SUPABASE_URL = "https://qfzzzxlxyvaokmrkbdrp.supabase.co"
SUPABASE_ANON_KEY = "sb_publishable_nGpFcOPg5OKxFK140HMjoQ_mXHGw_R9"

# Wieviele Monate rueckwaerts importieren
MONATE_RUECKWAERTS = 12

# Garmin-Token-Cache (so musst du nicht jedes Mal MFA machen)
GARMIN_TOKEN_DIR = Path.home() / ".garminconnect"


# ═══════════════════════════════════════════
# GARMIN LOGIN
# ═══════════════════════════════════════════
def garmin_login():
    """Login bei Garmin. Nutzt Token-Cache wenn vorhanden."""
    print("\n--- Garmin Login ---")
    
    # Versuche Token-Cache zu laden
    if GARMIN_TOKEN_DIR.exists():
        try:
            client = Garmin()
            client.login(str(GARMIN_TOKEN_DIR))
            print(f"✓ Garmin-Login via gespeicherte Tokens (Cache: {GARMIN_TOKEN_DIR})")
            return client
        except (GarthHTTPError, Exception) as e:
            print(f"⚠ Token-Cache veraltet, frischer Login noetig: {e}")
    
    # Frischer Login
    email = input("Garmin Email: ").strip()
    password = getpass.getpass("Garmin Passwort: ")
    
    client = Garmin(email, password)
    try:
        client.login()
    except Exception as e:
        if "MFA" in str(e) or "two-factor" in str(e).lower():
            mfa = input("MFA-Code: ").strip()
            client = Garmin(email, password, return_on_mfa=True)
            result1, result2 = client.login()
            client.resume_login(result2, mfa)
        else:
            raise
    
    # Token cachen
    GARMIN_TOKEN_DIR.mkdir(parents=True, exist_ok=True)
    client.garth.dump(str(GARMIN_TOKEN_DIR))
    print(f"✓ Garmin-Login erfolgreich, Tokens gespeichert in {GARMIN_TOKEN_DIR}")
    return client


# ═══════════════════════════════════════════
# SUPABASE LOGIN
# ═══════════════════════════════════════════
def supabase_login():
    """Login bei Supabase mit deinen App-Credentials."""
    print("\n--- Supabase Login (deine App-Credentials) ---")
    email = input("Email (z.B. lars@ssbi-blog.de): ").strip()
    password = getpass.getpass("App-Passwort: ")
    
    r = requests.post(
        f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
        headers={
            "apikey": SUPABASE_ANON_KEY,
            "Content-Type": "application/json"
        },
        json={"email": email, "password": password},
        timeout=15
    )
    r.raise_for_status()
    data = r.json()
    user_id = data["user"]["id"]
    access_token = data["access_token"]
    print(f"✓ Supabase-Login erfolgreich (User: {data['user']['email']})")
    return user_id, access_token


def sb_headers(access_token):
    return {
        "apikey": SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates"  # UPSERT-Verhalten
    }


# ═══════════════════════════════════════════
# DATEN-EXTRAKTION
# ═══════════════════════════════════════════
def to_iso(d):
    """date oder datetime -> ISO-String"""
    if d is None:
        return None
    if isinstance(d, datetime):
        return d.isoformat()
    return d.isoformat() if hasattr(d, 'isoformat') else str(d)


def safe_int(v):
    if v is None:
        return None
    try:
        return int(v)
    except (ValueError, TypeError):
        return None


def safe_float(v):
    if v is None:
        return None
    try:
        return float(v)
    except (ValueError, TypeError):
        return None


def fetch_taeglich(client, d):
    """Holt Tagesdaten fuer ein Datum von Garmin."""
    iso = d.isoformat()
    row = {"tagesdatum": iso}
    
    # Schlaf
    try:
        sleep = client.get_sleep_data(iso)
        if sleep and sleep.get("dailySleepDTO"):
            s = sleep["dailySleepDTO"]
            start_ts = s.get("sleepStartTimestampGMT")
            end_ts = s.get("sleepEndTimestampGMT")
            if start_ts:
                row["schlaf_start"] = datetime.fromtimestamp(start_ts/1000, tz=timezone.utc).isoformat()
            if end_ts:
                row["schlaf_ende"] = datetime.fromtimestamp(end_ts/1000, tz=timezone.utc).isoformat()
            
            sec_to_min = lambda x: round(x/60) if x else None
            row["schlaf_dauer_min"] = sec_to_min(s.get("sleepTimeSeconds"))
            row["schlaf_tief_min"] = sec_to_min(s.get("deepSleepSeconds"))
            row["schlaf_leicht_min"] = sec_to_min(s.get("lightSleepSeconds"))
            row["schlaf_rem_min"] = sec_to_min(s.get("remSleepSeconds"))
            row["schlaf_wach_min"] = sec_to_min(s.get("awakeSleepSeconds"))
            
            score = s.get("sleepScores", {}).get("overall", {}).get("value")
            row["schlaf_score"] = safe_int(score)
    except Exception as e:
        print(f"  ⚠ Schlaf-Fehler {iso}: {e}")
    
    # Tagesstats (Schritte, Kalorien, etc.)
    try:
        stats = client.get_stats(iso)
        if stats:
            row["schritte"] = safe_int(stats.get("totalSteps"))
            row["schritte_ziel"] = safe_int(stats.get("dailyStepGoal"))
            row["distanz_km"] = round(safe_float(stats.get("totalDistanceMeters") or 0)/1000, 2) or None
            row["kalorien_aktiv"] = safe_int(stats.get("activeKilocalories"))
            row["kalorien_gesamt"] = safe_int(stats.get("totalKilocalories"))
            row["intensitaet_min_moderat"] = safe_int(stats.get("moderateIntensityMinutes"))
            row["intensitaet_min_intensiv"] = safe_int(stats.get("vigorousIntensityMinutes"))
            row["etagen_hoch"] = safe_int(stats.get("floorsAscended"))
            row["ruhepuls_bpm"] = safe_int(stats.get("restingHeartRate"))
            row["hf_max_bpm"] = safe_int(stats.get("maxHeartRate"))
            row["hf_avg_bpm"] = safe_int(stats.get("averageHeartRate"))
            row["stress_avg"] = safe_int(stats.get("averageStressLevel"))
            row["stress_max"] = safe_int(stats.get("maxStressLevel"))
            row["stress_ruhe_min"] = safe_int(stats.get("restStressDuration", 0)/60) if stats.get("restStressDuration") else None
            row["stress_low_min"] = safe_int(stats.get("lowStressDuration", 0)/60) if stats.get("lowStressDuration") else None
            row["stress_mittel_min"] = safe_int(stats.get("mediumStressDuration", 0)/60) if stats.get("mediumStressDuration") else None
            row["stress_hoch_min"] = safe_int(stats.get("highStressDuration", 0)/60) if stats.get("highStressDuration") else None
            row["body_battery_max"] = safe_int(stats.get("bodyBatteryHighestValue"))
            row["body_battery_min"] = safe_int(stats.get("bodyBatteryLowestValue"))
            row["body_battery_aufgeladen"] = safe_int(stats.get("bodyBatteryChargedValue"))
            row["body_battery_verbraucht"] = safe_int(stats.get("bodyBatteryDrainedValue"))
            row["atemfrequenz_avg"] = safe_float(stats.get("avgWakingRespirationValue"))
    except Exception as e:
        print(f"  ⚠ Stats-Fehler {iso}: {e}")
    
    # HRV
    try:
        hrv = client.get_hrv_data(iso)
        if hrv and hrv.get("hrvSummary"):
            h = hrv["hrvSummary"]
            row["hrv_avg_ms"] = safe_float(h.get("weeklyAvg"))
            row["hrv_letzte_nacht_ms"] = safe_float(h.get("lastNightAvg"))
            row["hrv_status"] = h.get("status")
    except Exception as e:
        # HRV oft erst nach 3 Wochen Tragen verfuegbar
        pass
    
    # Training Readiness
    try:
        tr = client.get_training_readiness(iso)
        if tr and len(tr) > 0:
            t = tr[0]
            row["training_readiness_score"] = safe_int(t.get("score"))
            row["training_readiness_status"] = t.get("level")
    except Exception:
        pass
    
    # VO2max
    try:
        vo2 = client.get_max_metrics(iso)
        if vo2 and isinstance(vo2, list) and len(vo2) > 0:
            generic = vo2[0].get("generic", {})
            row["vo2max"] = safe_float(generic.get("vo2MaxValue"))
    except Exception:
        pass
    
    return row


# ═══════════════════════════════════════════
# SUPABASE UPLOAD
# ═══════════════════════════════════════════
def upsert_taeglich(rows, user_id, access_token):
    """Bulk-UPSERT Tagesdaten."""
    if not rows:
        return 0
    # user_id zu jeder Zeile
    for r in rows:
        r["user_id"] = user_id
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/garmin_taeglich",
        headers={**sb_headers(access_token), "Prefer": "resolution=merge-duplicates,return=minimal"},
        json=rows,
        timeout=30
    )
    if r.status_code >= 400:
        print(f"  ⚠ Upsert-Fehler ({r.status_code}): {r.text[:200]}")
        return 0
    return len(rows)


def log_sync(user_id, access_token, von, bis, tage, status, fehler=None):
    payload = {
        "user_id": user_id,
        "zeitraum_von": von.isoformat(),
        "zeitraum_bis": bis.isoformat(),
        "tage_synced": tage,
        "workouts_synced": 0,
        "status": status,
        "beendet_am": datetime.now(timezone.utc).isoformat()
    }
    if fehler:
        payload["fehler_message"] = fehler[:500]
    requests.post(
        f"{SUPABASE_URL}/rest/v1/garmin_sync_log",
        headers={**sb_headers(access_token), "Prefer": "return=minimal"},
        json=payload,
        timeout=15
    )


# ═══════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════
def main():
    print("=" * 60)
    print("  Garmin → Supabase Health-Journal Importer")
    print("=" * 60)
    
    # Logins
    try:
        gc = garmin_login()
    except Exception as e:
        print(f"✗ Garmin-Login fehlgeschlagen: {e}")
        sys.exit(1)
    
    try:
        user_id, access_token = supabase_login()
    except Exception as e:
        print(f"✗ Supabase-Login fehlgeschlagen: {e}")
        sys.exit(1)
    
    # Zeitraum
    bis = date.today()
    von = bis - timedelta(days=MONATE_RUECKWAERTS * 30)
    print(f"\nImportiere Daten von {von} bis {bis} ({(bis-von).days} Tage)")
    
    # Tagesdaten holen
    print("\n--- Tagesdaten ---")
    taeglich_rows = []
    d = von
    while d <= bis:
        if d.day == 1:
            print(f"  {d.strftime('%B %Y')}...")
        try:
            row = fetch_taeglich(gc, d)
            # Nur Zeilen mit *irgendwelchen* Daten speichern
            if any(v is not None for k, v in row.items() if k != "tagesdatum"):
                taeglich_rows.append(row)
        except Exception as e:
            print(f"  ⚠ Tag {d}: {e}")
        d += timedelta(days=1)
    
    print(f"\n→ {len(taeglich_rows)} Tage mit Daten gefunden")
    
    # Bulk-Upload
    print("\n--- Upload zu Supabase ---")
    # In Chunks von 100, sonst Payload-Limit
    n_taeglich = 0
    for i in range(0, len(taeglich_rows), 100):
        chunk = taeglich_rows[i:i+100]
        n_taeglich += upsert_taeglich(chunk, user_id, access_token)
    print(f"  ✓ {n_taeglich} Tagesdaten hochgeladen")
    
    # Log
    log_sync(user_id, access_token, von, bis, n_taeglich, "success")
    
    print("\n" + "=" * 60)
    print("  ✓ Import abgeschlossen!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Abbruch durch Nutzer")
        sys.exit(130)
    except Exception as e:
        print(f"\n✗ Fehler: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
