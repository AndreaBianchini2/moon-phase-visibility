# Script per verificare Visibilità della luna, ed eventualmente la Fase Lunare
import numpy as np
import matplotlib.pyplot as plt

from datetime import datetime, timedelta, timezone

from skyfield.api import load, wgs84
from skyfield import almanac
from skyfield.framelib import ecliptic_frame


LAT = float(input(" inserisci il valore della latitudine = "))
LON = float(input(" inserisci il valore della longitudine = "))
ELEV_M = float(input(" elevazione sopra il livello del mare = "))

# intervallo in UTC
from datetime import datetime, timezone

start_str = input("Inserisci inizio osservazione UTC (YYYY-MM-DD HH:MM): ")
end_str = input("Inserisci fine osservazione UTC (YYYY-MM-DD HH:MM): ")
STEP_MIN = int(input("Inserisci passo temporale in minuti: "))

START_UTC = datetime.strptime(start_str, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
END_UTC = datetime.strptime(end_str, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)

def phase_name(phase_deg: float) -> str:
    """Restituisce un nome semplice della fase a partire dall'angolo 0-360°."""
    if phase_deg < 22.5 or phase_deg >= 337.5:
        return "Luna nuova"
    elif phase_deg < 67.5:
        return "Falce crescente"
    elif phase_deg < 112.5:
        return "Primo quarto"
    elif phase_deg < 157.5:
        return "Gibbosa crescente"
    elif phase_deg < 202.5:
        return "Luna piena"
    elif phase_deg < 247.5:
        return "Gibbosa calante"
    elif phase_deg < 292.5:
        return "Ultimo quarto"
    else:
        return "Falce calante"


def build_time_grid(start_dt: datetime, end_dt: datetime, step_min: int):
    """Costruisce una griglia temporale UTC sia come lista datetime che come Time Skyfield."""
    dt_list = []
    current = start_dt
    while current <= end_dt:
        dt_list.append(current)
        current += timedelta(minutes=step_min)

    years = [d.year for d in dt_list]
    months = [d.month for d in dt_list]
    days = [d.day for d in dt_list]
    hours = [d.hour for d in dt_list]
    minutes = [d.minute for d in dt_list]
    seconds = [d.second for d in dt_list]

    return dt_list, ts.utc(years, months, days, hours, minutes, seconds)


# =========================
# CARICAMENTO DATI
# =========================

ts = load.timescale()
eph = load('de421.bsp')

earth = eph['earth']
moon = eph['moon']
sun = eph['sun']

observer = earth + wgs84.latlon(LAT, LON, elevation_m=ELEV_M)


# =========================
# 1) FASE LUNARE A INIZIO NOTTE
# =========================

t_phase = ts.utc(
    START_UTC.year, START_UTC.month, START_UTC.day,
    START_UTC.hour, START_UTC.minute, START_UTC.second
)

e = earth.at(t_phase)
s = e.observe(sun).apparent()
m = e.observe(moon).apparent()

_, slon, _ = s.frame_latlon(ecliptic_frame)
_, mlon, _ = m.frame_latlon(ecliptic_frame)

phase_deg = (mlon.degrees - slon.degrees) % 360.0
illum_percent = 100.0 * m.fraction_illuminated(sun)
phase_label = phase_name(phase_deg)


# =========================
# 2) ALTEZZA DELLA LUNA DURANTE LA NOTTE
# =========================

dt_list, times = build_time_grid(START_UTC, END_UTC, STEP_MIN)

apparent = observer.at(times).observe(moon).apparent()
alt, az, distance = apparent.altaz()

alt_deg = alt.degrees
az_deg = az.degrees

imax = int(np.argmax(alt_deg))
max_alt = alt_deg[imax]
max_alt_time = dt_list[imax]


# =========================
# 3) MOONRISE / MOONSET
# =========================

t0 = ts.utc(
    START_UTC.year, START_UTC.month, START_UTC.day,
    START_UTC.hour, START_UTC.minute, START_UTC.second
)
t1 = ts.utc(
    END_UTC.year, END_UTC.month, END_UTC.day,
    END_UTC.hour, END_UTC.minute, END_UTC.second
)

rise_times, rise_flags = almanac.find_risings(observer, moon, t0, t1)
set_times, set_flags = almanac.find_settings(observer, moon, t0, t1)

valid_rises = [t for t, y in zip(rise_times, rise_flags) if y == 1]
valid_sets = [t for t, y in zip(set_times, set_flags) if y == 1]


# =========================
# 4) REPORT TESTUALE
# =========================

print("\n=== MOON PHASE & VISIBILITY REPORT ===")
print(f"Osservatore: lat={LAT:.4f}°, lon={LON:.4f}°, quota={ELEV_M:.1f} m")
print(f"Intervallo UTC: {START_UTC}  ->  {END_UTC}")

print(f"\nFase lunare a inizio notte: {phase_label}")
print(f"Angolo di fase: {phase_deg:.1f}°")
print(f"Percentuale illuminata: {illum_percent:.1f}%")

print(f"\nMassima altezza della Luna: {max_alt:.2f}°")
print(f"Raggiunta a: {max_alt_time.strftime('%Y-%m-%d %H:%M UTC')}")

if valid_rises:
    print("\nMoonrise nel periodo:")
    for t in valid_rises:
        print(" -", t.utc_strftime('%Y-%m-%d %H:%M:%S UTC'))
else:
    print("\nNessun moonrise nell'intervallo scelto.")

if valid_sets:
    print("\nMoonset nel periodo:")
    for t in valid_sets:
        print(" -", t.utc_strftime('%Y-%m-%d %H:%M:%S UTC'))
else:
    print("\nNessun moonset nell'intervallo scelto.")


# =========================
# 5) GRAFICO
# =========================

plt.figure(figsize=(11, 6))
plt.plot(dt_list, alt_deg, label='Altezza Luna')
plt.axhline(0.0, linestyle='--', label='Orizzonte')
plt.scatter([max_alt_time], [max_alt], label='Massimo')

plt.title(f"Luna: altezza sull'orizzonte\n{phase_label} | illuminata {illum_percent:.1f}%")
plt.xlabel("Tempo UTC")
plt.ylabel("Altezza [gradi]")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()