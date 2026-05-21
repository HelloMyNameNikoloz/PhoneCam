#include "pch.h"
#include "PhoneCamSettings.h"

#include <cstdlib>

static constexpr wchar_t PHONECAM_SETTINGS_PATH[] = L"C:\\ProgramData\\PhoneCam\\native_settings.txt";

UINT32 PhoneCamNormalizeFps(UINT32 fps)
{
    switch (fps)
    {
    case 24:
    case 30:
    case 60:
    case 120:
        return fps;
    default:
        return 30;
    }
}

UINT32 PhoneCamReadTargetFps()
{
    wil::unique_handle file(CreateFileW(
        PHONECAM_SETTINGS_PATH,
        GENERIC_READ,
        FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
        nullptr,
        OPEN_EXISTING,
        FILE_ATTRIBUTE_NORMAL,
        nullptr));
    if (!file)
    {
        return 30;
    }

    char buffer[256] = {};
    DWORD bytesRead = 0;
    if (!ReadFile(file.get(), buffer, sizeof(buffer) - 1, &bytesRead, nullptr) || bytesRead == 0)
    {
        return 30;
    }

    const char* fpsText = strstr(buffer, "fps=");
    if (!fpsText)
    {
        return 30;
    }

    return PhoneCamNormalizeFps(static_cast<UINT32>(atoi(fpsText + 4)));
}
