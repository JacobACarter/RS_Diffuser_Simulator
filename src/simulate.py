from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from src.util.util import get_video_properties, load_video


@dataclass
class RollingShutterConfig:
	output_fps: float = 30.0
	readout_time_ms: float = 10.0
	exposure_time_ms: float = 2.0
	exposure_samples: int = 3
	output_frames: int = 1
	start_time_s: float = 0.0


def _normalize_kernel(kernel: np.ndarray) -> np.ndarray:
	kernel = kernel.astype(np.float32)
	total = float(kernel.sum())
	if total <= 0:
		raise ValueError("PSF kernel sum must be > 0")
	return kernel / total


def build_gaussian_psf(kernel_size: int = 31, sigma: float = 4.0) -> np.ndarray:
	if kernel_size % 2 == 0:
		kernel_size += 1
	g1d = cv2.getGaussianKernel(kernel_size, sigma)
	kernel = g1d @ g1d.T
	return _normalize_kernel(kernel)


def load_psf(psf_path: str | None = None, kernel_size: int = 31, sigma: float = 4.0) -> np.ndarray:
	if psf_path is None:
		return build_gaussian_psf(kernel_size=kernel_size, sigma=sigma)

	psf = cv2.imread(psf_path, cv2.IMREAD_GRAYSCALE)
	if psf is None:
		raise FileNotFoundError(f"Could not load PSF image: {psf_path}")
	return _normalize_kernel(psf)


def _load_frame_at_index(cap: cv2.VideoCapture, index: int) -> np.ndarray:
	cap.set(cv2.CAP_PROP_POS_FRAMES, index)
	ok, frame = cap.read()
	if not ok or frame is None:
		raise RuntimeError(f"Failed to read frame at index {index}")
	return frame


def _apply_psf(frame: np.ndarray, psf_kernel: np.ndarray) -> np.ndarray:
	# Keep values in float during filtering to avoid clipping artifacts.
	frame_f = frame.astype(np.float32)
	blurred = cv2.filter2D(frame_f, ddepth=-1, kernel=psf_kernel, borderType=cv2.BORDER_REFLECT)
	return np.clip(blurred, 0, 255).astype(np.uint8)


def simulate_rolling_shutter(
	video_path: str,
	out_path: str,
	config: RollingShutterConfig,
	psf_path: str | None = None,
	gaussian_kernel_size: int = 31,
	gaussian_sigma: float = 4.0,
) -> list[str]:
	cap = load_video(video_path)
	if cap is None:
		raise RuntimeError(f"Unable to open video: {video_path}")

	props = get_video_properties(cap)
	width = props["width"]
	height = props["height"]
	src_fps = float(props["fps"])
	src_frames = int(props["frames"])

	if src_fps <= 0:
		raise ValueError("Source video FPS must be > 0")

	if config.exposure_samples < 1:
		raise ValueError("exposure_samples must be >= 1")

	psf_kernel = load_psf(psf_path, kernel_size=gaussian_kernel_size, sigma=gaussian_sigma)

	readout_s = config.readout_time_ms / 1000.0
	exposure_s = config.exposure_time_ms / 1000.0
	row_period_s = readout_s / max(1, height)

	output_dir = Path(out_path)
	output_dir.mkdir(parents=True, exist_ok=True)
	output_paths: list[str] = []

	frame_cache: dict[int, np.ndarray] = {}

	for out_idx in range(config.output_frames):
		rs_time0 = config.start_time_s + (out_idx / config.output_fps)
		rs_frame = np.zeros((height, width, 3), dtype=np.float32)

		for row in range(height):
			row_start_t = rs_time0 + row * row_period_s
			if config.exposure_samples == 1:
				sample_times = [row_start_t + 0.5 * exposure_s]
			else:
				sample_times = np.linspace(
					row_start_t,
					row_start_t + exposure_s,
					config.exposure_samples,
					dtype=np.float64,
				)

			row_accum = np.zeros((width, 3), dtype=np.float32)

			for sample_t in sample_times:
				src_index = int(round(sample_t * src_fps))
				src_index = max(0, min(src_frames - 1, src_index))

				if src_index not in frame_cache:
					raw = _load_frame_at_index(cap, src_index)
					frame_cache[src_index] = _apply_psf(raw, psf_kernel)

				row_accum += frame_cache[src_index][row].astype(np.float32)

			rs_frame[row] = row_accum / float(config.exposure_samples)

		rs_out = np.clip(rs_frame, 0, 255).astype(np.uint8)
		out_file = output_dir / f"rs_sim_{out_idx:04d}.png"
		ok = cv2.imwrite(str(out_file), rs_out)
		if not ok:
			raise RuntimeError(f"Failed to write output image: {out_file}")
		output_paths.append(str(out_file))

	cap.release()
	return output_paths

