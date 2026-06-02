# RS_Diffuser_Simulator

Code intended to simulate the use of Diffusers on rolling shutter capture from high speed video.

## Simulate RS Frame(s) from High-FPS Video

The script below creates rolling-shutter images from a high-FPS source video and applies a point spread function (PSF) per source frame before row-wise sampling.

```bash
python scripts/create_RS_image.py \
	--video data/Slow_Mo_Clip.mp4 \
	--output-dir data/rs_output \
	--source-fps 48000 \
	--output-fps 30 \
	--readout-ms 10 \
	--exposure-ms 2 \
	--samples 3 \
	--frames 1
```

Use measured/calibrated diffuser PSF from the paper:

```bash
python scripts/create_RS_image.py \
	--video data/Slow_Mo_Clip.mp4 \
	--output-dir data/rs_output \
	--psf-image path/to/psf.png
```

Use anisotropic Gaussian PSF (large vertical spread, small horizontal spread):

```bash
python scripts/create_RS_image.py \
	--video data/Slow_Mo_Clip.mp4 \
	--output-dir data/rs_output \
	--source-fps 48000 \
	--readout-ms 20 \
	--exposure-ms 0.5 \
	--gaussian-kernel-x 31 \
	--gaussian-kernel-y 1081 \
	--gaussian-sigma-x 4 \
	--gaussian-sigma-y 180
```

Notes:
- `--readout-ms` controls top-to-bottom rolling shutter scan time.
- `--exposure-ms` controls per-row integration time.
- `--samples` controls how many temporal samples are averaged per row.
- `--source-fps` lets you force true source acquisition FPS when the file metadata is not accurate.
- If `--psf-image` is omitted, a Gaussian PSF is used (`--gaussian-kernel`, `--gaussian-sigma`).
- You can override isotropic blur with anisotropic controls (`--gaussian-kernel-x`, `--gaussian-kernel-y`, `--gaussian-sigma-x`, `--gaussian-sigma-y`).