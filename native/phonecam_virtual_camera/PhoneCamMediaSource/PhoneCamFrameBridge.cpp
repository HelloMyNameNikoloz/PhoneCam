#include "pch.h"
#include <shlobj.h>
#include <knownfolders.h>

static constexpr UINT32 PHONECAM_FRAME_MAGIC = 0x50434642; // PCFB
static constexpr UINT32 PHONECAM_FRAME_VERSION = 1;
static constexpr UINT32 PHONECAM_FRAME_FORMAT_BGRA = 1;

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

    RETURN_IF_FAILED(ReadFrameFile());
    if (m_frame.empty() || m_header.Width == 0 || m_header.Height == 0)
    {
        return S_OK;
    }

    RETURN_HR_IF(HRESULT_FROM_WIN32(ERROR_INSUFFICIENT_BUFFER), targetSize < targetPitch * height);
    ScaleBgra(m_frame.data(), m_header, target, targetPitch, width, height);
    *copied = true;
    return S_OK;
}

HRESULT PhoneCamFrameBridge::ReadFrameFile()
{
    wil::unique_cotaskmem_string path;
    RETURN_IF_FAILED(GetFramePath(path));

    wil::unique_hfile file(CreateFileW(
        path.get(),
        GENERIC_READ,
        FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
        nullptr,
        OPEN_EXISTING,
        FILE_ATTRIBUTE_NORMAL,
        nullptr));
    if (!file)
    {
        return S_OK;
    }

    PhoneCamFrameHeader header = {};
    DWORD read = 0;
    RETURN_IF_WIN32_BOOL_FALSE(ReadFile(file.get(), &header, sizeof(header), &read, nullptr));
    if (read != sizeof(header) || header.Magic != PHONECAM_FRAME_MAGIC ||
        header.Version != PHONECAM_FRAME_VERSION || header.Format != PHONECAM_FRAME_FORMAT_BGRA)
    {
        return S_OK;
    }
    if (header.Sequence == m_lastSequence || header.DataSize == 0 || header.DataSize > 3840 * 2160 * 4)
    {
        return S_OK;
    }

    std::vector<BYTE> frame(header.DataSize);
    RETURN_IF_WIN32_BOOL_FALSE(ReadFile(file.get(), frame.data(), header.DataSize, &read, nullptr));
    if (read != header.DataSize)
    {
        return S_OK;
    }

    m_header = header;
    m_frame = std::move(frame);
    m_lastSequence = header.Sequence;
    return S_OK;
}

HRESULT PhoneCamFrameBridge::GetFramePath(wil::unique_cotaskmem_string& path)
{
    wil::unique_cotaskmem_string programData;
    RETURN_IF_FAILED(SHGetKnownFolderPath(FOLDERID_ProgramData, 0, nullptr, &programData));
    std::wstring value(programData.get());
    value += L"\\PhoneCam\\framebuffer.bin";
    path.reset(static_cast<PWSTR>(CoTaskMemAlloc((value.size() + 1) * sizeof(wchar_t))));
    RETURN_IF_NULL_ALLOC(path.get());
    wcscpy_s(path.get(), value.size() + 1, value.c_str());
    return S_OK;
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
            const BYTE* pixel = srcRow + sx * 4;
            memcpy(dstRow + x * 4, pixel, 4);
        }
    }
}
