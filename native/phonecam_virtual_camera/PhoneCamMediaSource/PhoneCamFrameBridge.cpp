#include "pch.h"

static constexpr UINT32 PHONECAM_FRAME_MAGIC = 0x50434642;
static constexpr UINT32 PHONECAM_STATS_MAGIC = 0x50435354;
static constexpr UINT32 PHONECAM_FRAME_VERSION = 1;
static constexpr UINT32 PHONECAM_FRAME_FORMAT_BGRA = 1;
static constexpr DWORD PHONECAM_BUFFER_SIZE = sizeof(PhoneCamFrameHeader) + 3840 * 2160 * 4;

HRESULT PhoneCamFrameBridge::TryCopyBgraFrame(
    BYTE* target,
    DWORD targetSize,
    LONG targetPitch,
    UINT32 width,
    UINT32 height,
    bool* copied)
{
    RETURN_HR_IF_NULL(E_POINTER, target);
    RETURN_HR_IF_NULL(E_POINTER, copied);
    *copied = false;

    RETURN_IF_FAILED(ReadSharedFrame());
    if (m_frame.empty() || m_header.Width == 0 || m_header.Height == 0)
    {
        RecordOutput(true, width, height);
        return S_OK;
    }

    RETURN_HR_IF(HRESULT_FROM_WIN32(ERROR_INSUFFICIENT_BUFFER), targetSize < targetPitch * height);
    ScaleBgra(m_frame.data(), m_header, target, targetPitch, width, height);
    bool duplicate = m_header.Sequence == m_lastDeliveredSequence;
    m_lastDeliveredSequence = m_header.Sequence;
    RecordOutput(duplicate, width, height);
    *copied = true;
    return S_OK;
}

HRESULT PhoneCamFrameBridge::OpenMappings()
{
    if (!m_frameMapping)
    {
        m_frameMapping.reset(OpenFileMappingW(FILE_MAP_READ, FALSE, L"PhoneCamFrameBuffer"));
        if (m_frameMapping)
        {
            m_frameView = static_cast<BYTE*>(MapViewOfFile(m_frameMapping.get(), FILE_MAP_READ, 0, 0, PHONECAM_BUFFER_SIZE));
        }
    }
    if (!m_statsMapping)
    {
        m_statsMapping.reset(CreateFileMappingW(INVALID_HANDLE_VALUE, nullptr, PAGE_READWRITE, 0, sizeof(PhoneCamNativeStats), L"PhoneCamStats"));
        if (m_statsMapping)
        {
            m_stats = static_cast<PhoneCamNativeStats*>(MapViewOfFile(m_statsMapping.get(), FILE_MAP_WRITE, 0, 0, sizeof(PhoneCamNativeStats)));
            if (m_stats && m_stats->Magic != PHONECAM_STATS_MAGIC)
            {
                ZeroMemory(m_stats, sizeof(PhoneCamNativeStats));
                m_stats->Magic = PHONECAM_STATS_MAGIC;
                m_stats->Version = 1;
            }
        }
    }
    return S_OK;
}

HRESULT PhoneCamFrameBridge::ReadSharedFrame()
{
    RETURN_IF_FAILED(OpenMappings());
    if (!m_frameView)
    {
        return S_OK;
    }

    PhoneCamFrameHeader header = {};
    CopyMemory(&header, m_frameView, sizeof(header));
    if (header.Magic != PHONECAM_FRAME_MAGIC || header.Version != PHONECAM_FRAME_VERSION ||
        header.Format != PHONECAM_FRAME_FORMAT_BGRA || header.Sequence == m_lastSequence ||
        header.DataSize == 0 || header.DataSize > 3840 * 2160 * 4)
    {
        return S_OK;
    }

    std::vector<BYTE> frame(header.DataSize);
    CopyMemory(frame.data(), m_frameView + sizeof(PhoneCamFrameHeader), header.DataSize);
    m_header = header;
    m_frame = std::move(frame);
    m_lastSequence = header.Sequence;
    return S_OK;
}

void PhoneCamFrameBridge::RecordOutput(bool duplicate, UINT32 width, UINT32 height)
{
    if (!m_stats)
    {
        return;
    }
    UINT64 now = UnixTimeNs();
    m_stats->OutputFrames++;
    if (duplicate)
    {
        m_stats->DuplicateFrames++;
    }
    m_stats->LastOutputNs = now;
    m_stats->LastSequence = m_header.Sequence;
    m_stats->LastLatencyMs = m_header.TimestampQpc ? (now - m_header.TimestampQpc) / 1000000 : 0;
    m_stats->LastWidth = width;
    m_stats->LastHeight = height;
}

UINT64 PhoneCamFrameBridge::UnixTimeNs()
{
    FILETIME ft = {};
    GetSystemTimePreciseAsFileTime(&ft);
    ULARGE_INTEGER value = {};
    value.LowPart = ft.dwLowDateTime;
    value.HighPart = ft.dwHighDateTime;
    return (value.QuadPart - 116444736000000000ULL) * 100ULL;
}

void PhoneCamFrameBridge::ScaleBgra(
    const BYTE* source,
    const PhoneCamFrameHeader& header,
    BYTE* target,
    LONG pitch,
    UINT32 width,
    UINT32 height)
{
    for (UINT32 y = 0; y < height; ++y)
    {
        UINT32 sy = y * header.Height / height;
        const BYTE* srcRow = source + sy * header.Stride;
        BYTE* dstRow = target + y * pitch;
        for (UINT32 x = 0; x < width; ++x)
        {
            UINT32 sx = x * header.Width / width;
            CopyMemory(dstRow + x * 4, srcRow + sx * 4, 4);
        }
    }
}
