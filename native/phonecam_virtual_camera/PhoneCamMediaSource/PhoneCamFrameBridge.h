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

class PhoneCamFrameBridge
{
public:
    HRESULT TryCopyBgraFrame(BYTE* target, DWORD targetSize, LONG targetPitch, UINT32 width, UINT32 height, bool* copied);

private:
    HRESULT ReadFrameFile();
    static HRESULT GetFramePath(wil::unique_cotaskmem_string& path);
    static void ScaleBgra(const BYTE* source, const PhoneCamFrameHeader& header, BYTE* target, LONG pitch, UINT32 width, UINT32 height);

    std::vector<BYTE> m_frame;
    PhoneCamFrameHeader m_header = {};
    UINT32 m_lastSequence = 0;
};
