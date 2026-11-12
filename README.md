# Moon Phase & Visibility Planner

A command-line Python tool that, for any observer location and UTC time window, computes the Moon's phase and illumination, its altitude and azimuth over time, and the moonrise and moonset times. Positions come from [Skyfield](https://rhodesmiller.com/skyfield/) and the JPL DE421 ephemeris.

## Features

- **Moon phase** at the start of the observing window: Moon–Sun ecliptic longitude difference, phase name (8 classes) and illuminated fraction
- **Altitude and azimuth** of the Moon on a user-defined time grid, with the maximum altitude and the time it is reached
- **Moonrise and moonset** times inside the window
- **Text report** and **altitude plot** of the Moon above the horizon

## Inputs

The program asks for the following values interactively (the prompts and the report are in Italian).

| Input | Description |
|---|---|
| Latitude | Observer latitude in degrees, north positive |
| Longitude | Observer longitude in degrees, east positive |
| Elevation | Height above sea level [m] |
| Start / end | Observation window in UTC, format `YYYY-MM-DD HH:MM` |
| Time step | Sampling step of the altitude curve [minutes] |

## Output

The report contains:

- observer position and time interval;
- Moon phase name, Moon–Sun ecliptic longitude difference [°] and illuminated percentage at the start of the window;
- maximum altitude of the Moon [°] and the UTC time at which it occurs;
- the list of moonrise and moonset times in the interval (or a message if there are none).

A Matplotlib window then shows the altitude of the Moon above the horizon over the chosen interval.

![Moon altitude plot](figures/moon_altitude.png)

## Method

- **Phase.** Apparent positions of the Sun and Moon are computed from the geocenter and converted to ecliptic longitude. The phase value is $\lambda_{Moon} - \lambda_{Sun} \pmod{360°}$, so 0° is new Moon, 90° first quarter, 180° full Moon and 270° last quarter. It is split into eight 45° classes centered on these values. The illuminated fraction is computed with Skyfield's `fraction_illuminated`.
- **Altitude and azimuth.** The Moon is observed from a WGS84 topocentric position (latitude, longitude, elevation) at every point of the time grid, using apparent positions.
- **Rise and set.** `skyfield.almanac.find_risings` and `find_settings` over the whole window.

## Installation and usage

```bash
git clone https://github.com/<your-username>/moon-phase-visibility.git
cd moon-phase-visibility
pip install numpy matplotlib skyfield
python moon_visibility.py
```

Skyfield 1.47 or later is required (`find_risings` and `find_settings` were introduced in that version). The first run downloads the `de421.bsp` ephemeris file (about 17 MB), so an internet connection is needed once.

Example session:

```text
 inserisci il valore della latitudine = 40.0
 inserisci il valore della longitudine = 10.0
 elevazione sopra il livello del mare = 100
Inserisci inizio osservazione UTC (YYYY-MM-DD HH:MM): 2026-11-15 18:00
Inserisci fine osservazione UTC (YYYY-MM-DD HH:MM): 2026-11-16 06:00
Inserisci passo temporale in minuti: 10
```

## Notes and limitations

- The phase is evaluated once, at the start of the window; it is not recomputed along the interval.
- The altitude curve is geometric (no atmospheric refraction), while moonrise and moonset follow Skyfield's standard convention (upper limb, standard refraction). The instant at which the plotted altitude crosses 0° can therefore differ from the reported rise or set by a few minutes.
- The maximum altitude is the maximum over the sampled points, so its accuracy depends on the chosen time step.
- The Sun is not used to determine twilight or darkness: the "night" is simply the window you enter.
- Inputs are not validated: use a positive time step and an end time later than the start time.
- DE421 covers roughly the years 1900–2050.

## Author

Andrea Bianchini

## License

MIT (see `LICENSE`).

