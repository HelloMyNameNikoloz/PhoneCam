#pragma once

struct PhoneCamFrameHeader
{
    UINT32 Magic;
    UINT32 Version;
    UINT32 Width;
    UINT32 Height;
    UINT32 Stride;
    UINT32 Format;
    UINT32 DataSize;
    UINT32 Sequence;
    UINT64 TimestampQpc;
};

struct PhoneCamNativeStats
{
    UINT32 Magic;
    UINT32 Version;
    UINT64 OutputFrames;
    UINT64 DuplicateFrames;
    UINT64 LastOutputNs;
    UINT64 LastSequence;
    UINT64 LastLatencyMs;
    UINT32 LastWidth;
    UINT32 LastHeight;
};

class PhoneCamFrameBridge
{
public:
    HRESULT TryCopyBgraFrame(BYTE* target, DWORD targetSize, LONG targetPitch, UINT32 width, UINT32 height, bool* copied);
    HRESULT TryCopyNv12Frame(BYTE* target, DWORD targetSize, LONG targetPitch, UINT32 width, UINT32 height, bool* copied);

private:
    HRESULT ReadSharedFrame();
    HRESULT OpenMappings();
    void RecordOutput(bool duplicate, UINT32 width, UINT32 height);
    static UINT64 UnixTimeNs();
    static void CopyOrScaleBgra(const BYTE* source, const PhoneCamFrameHeader& header, BYTE* target, LONG pitch, UINT32 width, UINT32 height);

    std::vector<BYTE> m_frame;
    PhoneCamFrameHeader m_header = {};
    UINT32 m_lastSequence = 0;
    UINT32 m_lastDeliveredSequence = 0;
    wil::unique_handle m_frameMapping;
    wil::unique_handle m_statsMapping;
    BYTE* m_frameView = nullptr;
    PhoneCamNativeStats* m_stats = nullptr;
};
