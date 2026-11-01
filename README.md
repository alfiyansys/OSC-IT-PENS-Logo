# OSC IT PENS — Logo

Versi vektor (SVG) dari logo **The Open Source Community**.

## 0. Isi repo

| File | Keterangan |
|---|---|
| `opensource-community-logo.svg` | Logo vektor utama, latar transparan di luar lingkaran |
| `export/opensource-community-logo-2048.png` | Render PNG 2048×2048 (transparan) |
| `source/original-raster.jpg` | Referensi raster 1 (1080×1080 JPEG) |
| `source/original-raster-2.png` | Referensi raster 2 (360×356, lebih bersih) |
| `build/build.py` | Skrip build untuk reproduksi SVG |

## 1. Metode (hybrid)

| Elemen | Cara | Alasan |
|---|---|---|
| Lingkaran, garis latar, garis bawah, coretan "SOURCE" | Dibangun ulang secara geometris dari pengukuran | Bentuk geometris murni; trace hanya menambah noise |
| Simbol biru | Auto-trace (potrace) dari **rata-rata dua referensi** yang diselaraskan (korelasi 0,95) | Bentuk organik; rata-rata dua sumber mengurangi artefak JPEG |
| "Open", "SOURCE", tagline | Font open-source → dikonversi ke *outline path*, di-fit ke kotak hasil ukur | Trace teks dari raster kecil merusak bentuk huruf |

Font yang dipakai (semua SIL OFL, sudah menjadi path sehingga SVG tidak bergantung font terpasang):

- "Open" — Oswald Bold
- "SOURCE" — Cinzel SemiBold (huruf kecil Cinzel = small caps)
- Tagline — Open Sans SemiBold Italic

### 1.1 Parameter hasil ukur

- Lingkaran: pusat (543, 547), r 514 — diselesaikan dari tiga tali busur.
- Garis latar: periode 20,85 px, fase 1,25 px.
- Registrasi referensi 2 terhadap referensi 1: skala 3×, offset (−2, +5) px.

## 2. Verifikasi

- Lebar goresan simbol pada potongan horizontal y = 300/450/600 cocok dengan sumber, selisih ≤ 2 px.
- Overlay 50% SVG terhadap JPEG asli tanpa bayangan ganda pada simbol, lingkaran, garis, dan tagline.

## 3. Keterbatasan

- Font asli tidak diketahui; Oswald, Cinzel, dan Open Sans adalah pendekatan. Diperlukan sedikit skala horizontal (0,86–1,09×) agar lebar teks sama dengan aslinya.
- Shading 3D simbol diaproksimasi dengan satu *radial gradient*.

## 4. Regenerasi

```bash
pip install potracer scipy pillow numpy fonttools brotli cairosvg
npm pack @fontsource/oswald @fontsource/cinzel @fontsource/open-sans
# ekstrak, konversi .woff → .ttf (fontTools) ke satu folder FONTDIR, lalu:
python3 build/build.py source/original-raster.jpg source/original-raster-2.png FONTDIR opensource-community-logo.svg
```
