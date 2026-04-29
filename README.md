# Breathwork Timer

A small Linux desktop app for two guided breathwork practices, built with Python + Tkinter and shipped as a single self-contained AppImage.

## Techniques

### Morning Rise (Wim Hof style)

Three rounds. Each round is:

1. **30 rapid breaths** — 1.5 s inhale, 1.5 s exhale.
2. **Exhale hold** — fully exhale and hold. The timer counts up; click the circle (or press `Space`) when you need to inhale.
3. **Recovery hold** — inhale fully and hold for 15 s.

After the third round the session ends. Color scheme: dark stone with gold.

### Deep Calm (4-7-8)

Four rounds of:

- Inhale through the nose for **4 s**
- Hold for **7 s**
- Exhale through the mouth for **8 s**

Color scheme: dark stone with blue.

## Visuals

- A breathing circle that smoothly expands on inhale and contracts on exhale (eased, not linear).
- Phase label and countdown number in the center of the circle.
- Round counter under the circle.
- Buttons to switch technique, plus Start / Pause and Reset.

## Keyboard

- `Space` — start, or release the exhale hold during Morning Rise
- `Esc` — reset

## Running the AppImage

```bash
./BreathworkTimer-x86_64.AppImage
```

The build script marks the file executable, so no extra `chmod` is needed. Tested on Linux Mint 22.3 (Zena, x86_64). Should work on any reasonably recent x86_64 Linux with `glibc >= 2.34` and an X11 or XWayland display.

If your system lacks FUSE, you can still run the AppImage by extracting it:

```bash
./BreathworkTimer-x86_64.AppImage --appimage-extract
./squashfs-root/AppRun
```

## Building from source

The build embeds [python-build-standalone](https://github.com/astral-sh/python-build-standalone) (which ships with Tkinter) into the AppDir, then wraps it with [appimagetool](https://github.com/AppImage/appimagetool). No system-level Python or Tk required; only `curl`, `tar`, and a working x86_64 Linux toolchain.

```bash
./build.sh
```

The script:

1. Downloads a portable CPython 3.12 build (with Tkinter) to `build/python/`.
2. Downloads `appimagetool` and extracts it (avoids needing FUSE).
3. Generates the icon via `make_icon.py` (pure stdlib, no Pillow).
4. Assembles `build/BreathworkTimer.AppDir/` with a relocatable `AppRun` launcher.
5. Packages the AppDir into `BreathworkTimer-x86_64.AppImage` and `chmod +x`es it.

The resulting AppImage is ~83 MB and self-contained.

## Project layout

```
.
├── main.py              # Tkinter app
├── make_icon.py         # Pure-stdlib PNG icon generator
├── build.sh             # Builds the AppImage end to end
├── .gitignore
└── README.md
```

## License

MIT.
