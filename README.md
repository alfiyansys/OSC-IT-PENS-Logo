# OSC IT PENS — Logo

Versi vektor (SVG) dari logo **The Open Source Community**.

## 0. Isi repo

| File | Keterangan |
|---|---|
| `opensource-community-logo.svg` | Logo vektor utama (viewBox 1080×1080) |
| `export/opensource-community-logo-2048.png` | Render PNG 2048×2048 dari SVG |
| `source/original-raster.jpg` | Gambar raster asli (1080×1080 JPEG) |
| `source/trace.py` | Skrip tracing (potrace + morfologi) untuk reproduksi |

## 1. Metode

Hybrid: elemen geometris dibuat ulang bersih, elemen organik di-trace.

- **Dibuat ulang manual:** lingkaran, outline biru, garis-garis latar, garis bawah, coretan pada "SOURCE".
- **Auto-trace (potrace):** simbol biru, teks "Open", "SOURCE", dan tagline.

## 2. Keterbatasan

- Sumber berupa JPEG resolusi rendah dengan pola garis, sehingga tepi hasil trace tidak 100% identik dengan desain asli (misal bentuk huruf "p" pada "Open").
- Gradien biru diaproksimasi dengan satu radial gradient, bukan shading 3D asli.
- Untuk hasil sempurna, teks sebaiknya diganti font asli bila diketahui.

## 3. Regenerasi

```bash
pip install potracer scipy pillow numpy cairosvg
cd /path/ke/folder/berisi/source.jpg && python3 trace.py
```
