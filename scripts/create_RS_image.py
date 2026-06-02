from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
	sys.path.insert(0, str(REPO_ROOT))

from src.simulate import RollingShutterConfig, simulate_rolling_shutter


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(
		description="Create rolling-shutter simulated frames from high-FPS video using diffuser PSF."
	)
	parser.add_argument(
		"--video",
		type=str,
		default="data/Slow_Mo_Clip.mp4",
		help="Path to high-FPS source video.",
	)
	parser.add_argument(
		"--output-dir",
		type=str,
		default="data/rs_output",
		help="Directory for output PNG frame(s).",
	)
	parser.add_argument(
		"--psf-image",
		type=str,
		default=None,
		help="Optional grayscale PSF image (from paper/calibration).",
	)
	parser.add_argument("--output-fps", type=float, default=30.0)
	parser.add_argument("--readout-ms", type=float, default=10.0)
	parser.add_argument("--exposure-ms", type=float, default=2.0)
	parser.add_argument("--samples", type=int, default=3)
	parser.add_argument("--frames", type=int, default=1)
	parser.add_argument("--start-time", type=float, default=0.0)
	parser.add_argument("--gaussian-kernel", type=int, default=31)
	parser.add_argument("--gaussian-sigma", type=float, default=4.0)
	return parser.parse_args()


def main() -> None:
	args = parse_args()

	config = RollingShutterConfig(
		output_fps=args.output_fps,
		readout_time_ms=args.readout_ms,
		exposure_time_ms=args.exposure_ms,
		exposure_samples=args.samples,
		output_frames=args.frames,
		start_time_s=args.start_time,
	)

	outputs = simulate_rolling_shutter(
		video_path=args.video,
		out_path=args.output_dir,
		config=config,
		psf_path=args.psf_image,
		gaussian_kernel_size=args.gaussian_kernel,
		gaussian_sigma=args.gaussian_sigma,
	)

	print("Wrote RS simulated frame(s):")
	for output in outputs:
		print(output)


if __name__ == "__main__":
	main()
