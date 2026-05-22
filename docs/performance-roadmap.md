# Performance Roadmap

## Current Pipeline

Android Camera2 captures JPEG frames, sends them over an ADB reverse TCP tunnel,
the Python app decodes with Pillow, writes BGRA to a shared frame file, and the
native virtual camera converts to NV12 for camera clients.

This works, but it is not the final hot path.

## Bottlenecks

- Android JPEG encode cost at 1080p60.
- Python/Pillow decode in the frame hot path.
- BGRA frame handoff uses about 8.3 MB per 1080p frame.
- Native BGRA to NV12 conversion per output sample.
- Single latest-frame file instead of a versioned ring buffer.

## Target Pipeline

1. Android captures `YUV_420_888` or hardware-encoded H.264/H.265.
2. Windows native receiver decodes or copies to NV12/I420.
3. Shared frame ring buffer stores timestamped frames.
4. Media Foundation source serves NV12 directly.
5. Python UI only controls settings and displays stats.

## Release Gates

- v1 beta: stable 1080p30 with current path and honest diagnostics.
- v1 stable: native/YUV path available for 1080p30.
- v2: 1080p60, 2K/4K, and advanced camera controls.
