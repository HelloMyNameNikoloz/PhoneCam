# PhoneCam Frame Pipeline

The registered camera and the Python control app need a frame handoff that does not depend on a visible scrcpy window.

Planned contract:

- Producer: PhoneCam desktop app or a helper process started by it.
- Consumer: `PhoneCamVirtualCamera.dll`.
- Transport: named shared memory plus an event pair.
- Pixel format: NV12 first, YUY2 fallback for legacy capture apps.
- Default mode: 1920x1080 at 30 FPS.

Shared memory header:

```c
struct PhoneCamFrameHeader {
    uint32_t magic;
    uint32_t version;
    uint32_t width;
    uint32_t height;
    uint32_t fourcc;
    uint32_t stride;
    uint64_t frame_index;
    uint64_t timestamp_qpc;
    uint32_t payload_size;
};
```

The current native source still uses the Microsoft sample generator. Replacing that generator with this consumer is the next implementation step.
