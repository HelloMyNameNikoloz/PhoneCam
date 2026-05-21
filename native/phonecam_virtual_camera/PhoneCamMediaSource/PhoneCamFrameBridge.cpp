#include "pch.h"
#include "PhoneCamColorConvert.h"

static constexpr UINT32 PHONECAM_FRAME_MAGIC = 0x50434642;
static constexpr UINT32 PHONECAM_STATS_MAGIC = 0x50435354;
static constexpr UINT32 PHONECAM_FRAME_VERSION = 1;
static constexpr UINT32 PHONECAM_FRAME_FORMAT_BGRA = 1;
static constexpr DWORD PHONECAM_BUFFER_SIZE = sizeof(PhoneCamFrameHeader) + 3840 * 2160 * 4;
static constexpr wchar_t PHONECAM_FRAME_PATH[] = L"C:\\ProgramData\\PhoneCam\\framebuffer.bin";
static constexpr wchar_t PHONECAM_STATS_PATH[] = L"C:\\ProgramData\\PhoneCam\\native_stats.bin";

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
    CopyOrScaleBgra(m_frame.data(), m_header.Width, m_header.Height, m_header.Stride, m_header.DataSize, target, targetPitch, width, height);
    bool duplicate = m_header.Sequence == m_lastDeliveredSequence;
    m_lastDeliveredSequence = m_header.Sequence;
    RecordOutput(duplicate, width, height);
    *copied = true;
    return S_OK;
}

HRESULT PhoneCamFrameBridge::TryCopyNv12Frame(
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

    RETURN_HR_IF(E_INVALIDARG, targetPitch <= 0 || height < 2);
    DWORD required = static_cast<DWORD>(targetPitch) * height * 3 / 2;
    RETURN_HR_IF(HRESULT_FROM_WIN32(ERROR_INSUFFICIENT_BUFFER), targetSize < required);
    CopyOrScaleBgraToNv12(m_frame.data(), m_header.Width, m_header.Height, m_header.Stride, target, targetPitch, width, height);
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
        CreateDirectoryW(L"C:\\ProgramData\\PhoneCam", nullptr);
        m_frameFile.reset(CreateFileW(
            PHONECAM_FRAME_PATH,
            GENERIC_READ,
            FILE_SHARE_READ | FILE_SHARE_WRITE,
            nullptr,
            OPEN_EXISTING,
            FILE_ATTRIBUTE_NORMAL,
            nullptr));
        if (m_frameFile)
        {
            m_frameMapping.reset(CreateFileMappingW(m_frameFile.get(), nullptr, PAGE_READONLY, 0, PHONECAM_BUFFER_SIZE, nullptr));
        }
        if (m_frameMapping)
        {
            m_frameView = static_cast<BYTE*>(MapViewOfFile(m_frameMapping.get(), FILE_MAP_READ, 0, 0, PHONECAM_BUFFER_SIZE));
        }
    }
    if (!m_statsMapping)
    {
        m_statsFile.reset(CreateFileW(
            PHONECAM_STATS_PATH,
            GENERIC_READ | GENERIC_WRITE,
            FILE_SHARE_READ | FILE_SHARE_WRITE,
            nullptr,
            OPEN_ALWAYS,
            FILE_ATTRIBUTE_NORMAL,
            nullptr));
        if (m_statsFile)
        {
            LARGE_INTEGER size = {};
            size.QuadPart = sizeof(PhoneCamNativeStats);
            SetFilePointerEx(m_statsFile.get(), size, nullptr, FILE_BEGIN);
            SetEndOfFile(m_statsFile.get());
            m_statsMapping.reset(CreateFileMappingW(m_statsFile.get(), nullptr, PAGE_READWRITE, 0, sizeof(PhoneCamNativeStats), nullptr));
        }
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

    if (m_frame.size() != header.DataSize)
    {
        m_frame.resize(header.DataSize);
    }
    CopyMemory(m_frame.data(), m_frameView + sizeof(PhoneCamFrameHeader), header.DataSize);

    PhoneCamFrameHeader verify = {};
    CopyMemory(&verify, m_frameView, sizeof(verify));
    if (verify.Sequence != header.Sequence || verify.DataSize != header.DataSize)
    {
        return S_OK;
    }

    m_header = header;
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
