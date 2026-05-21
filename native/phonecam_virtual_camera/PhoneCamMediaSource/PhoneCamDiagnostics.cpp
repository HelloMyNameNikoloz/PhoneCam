#include "pch.h"
#include "PhoneCamDiagnostics.h"

static SRWLOCK g_diagLock = SRWLOCK_INIT;
static ULONGLONG g_lastWriteMs = 0;
static UINT64 g_sampleCount = 0;
static UINT64 g_copiedCount = 0;
static DWORD g_lastElapsedMs = 0;
static DWORD g_maxElapsedMs = 0;
static GUID g_lastSubtype = GUID_NULL;
static UINT32 g_lastWidth = 0;
static UINT32 g_lastHeight = 0;

static void WriteDiagnosticsLine(ULONGLONG now)
{
    CreateDirectoryW(L"C:\\ProgramData\\PhoneCam", nullptr);
    HANDLE file = CreateFileW(
        L"C:\\ProgramData\\PhoneCam\\native_camera.log",
        FILE_APPEND_DATA,
        FILE_SHARE_READ,
        nullptr,
        OPEN_ALWAYS,
        FILE_ATTRIBUTE_NORMAL,
        nullptr);
    if (file == INVALID_HANDLE_VALUE)
    {
        return;
    }

    WCHAR guidWide[64] = {};
    char guidText[64] = {};
    StringFromGUID2(g_lastSubtype, guidWide, ARRAYSIZE(guidWide));
    WideCharToMultiByte(CP_UTF8, 0, guidWide, -1, guidText, sizeof(guidText), nullptr, nullptr);

    char line[384] = {};
    sprintf_s(
        line,
        "[%llu] samples=%llu copied=%llu subtype=%s size=%ux%u last_ms=%lu max_ms=%lu\n",
        now,
        g_sampleCount,
        g_copiedCount,
        guidText,
        g_lastWidth,
        g_lastHeight,
        g_lastElapsedMs,
        g_maxElapsedMs);
    DWORD written = 0;
    WriteFile(file, line, static_cast<DWORD>(strlen(line)), &written, nullptr);
    CloseHandle(file);
}

void PhoneCamRecordSample(
    REFGUID subtype,
    UINT32 width,
    UINT32 height,
    bool copied,
    DWORD elapsedMs)
{
    ULONGLONG now = GetTickCount64();
    AcquireSRWLockExclusive(&g_diagLock);
    g_sampleCount++;
    g_copiedCount += copied ? 1 : 0;
    g_lastSubtype = subtype;
    g_lastWidth = width;
    g_lastHeight = height;
    g_lastElapsedMs = elapsedMs;
    g_maxElapsedMs = max(g_maxElapsedMs, elapsedMs);
    if (now - g_lastWriteMs >= 1000)
    {
        WriteDiagnosticsLine(now);
        g_sampleCount = 0;
        g_copiedCount = 0;
        g_maxElapsedMs = 0;
        g_lastWriteMs = now;
    }
    ReleaseSRWLockExclusive(&g_diagLock);
}
