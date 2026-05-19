# PhoneCam Frame Pipeline

The registered camera and the Python control app need a frame handoff that does not depend on a visible scrcpy window.

Implemented contract:

- Producer: PhoneCam desktop app.
- Consumer: `PhoneCamVirtualCamera.dll`.
- Transport: `C:\ProgramData\PhoneCam\framebuffer.bin`.
- Pixel format: BGRA in the handoff file; native source converts to NV12 when requested.
- Default virtual camera mode: 1920x1080 at 30 FPS.

Shared memory header:

```c
struct PhoneCamFrameHeader {
    uint32_t magic;
    uint32_t version;
    uint32_t width;
    uint32_t height;
    uint32_t stride;
    uint32_t format;
    uint32_t payload_size;
    uint32_t sequence;
    uint64_t timestamp_qpc;
};
```
