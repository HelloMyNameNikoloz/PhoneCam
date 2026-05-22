#include <windows.h>
#include <mfapi.h>
#include <mfvirtualcamera.h>
#include <iostream>
#include <string>
#include <vector>

static constexpr wchar_t SourceClsid[] = L"{E807E3F3-AC55-490B-8371-56BC0C464978}";
static constexpr wchar_t FriendlyName[] = L"PhoneCam";
#define RETURN_IF_FAILED(hrCall) do { HRESULT _hr = (hrCall); if (FAILED(_hr)) return _hr; } while (0)

using RegisterFn = HRESULT (STDAPICALLTYPE*)();

static void PrintHr(const wchar_t* action, HRESULT hr)
{
    std::wcerr << action << L" failed: 0x" << std::hex << static_cast<unsigned long>(hr) << std::endl;
}

static HRESULT InvokeDllExport(const std::wstring& dllPath, const char* name)
{
    HMODULE module = LoadLibraryW(dllPath.c_str());
    if (!module) return HRESULT_FROM_WIN32(GetLastError());
    auto fn = reinterpret_cast<RegisterFn>(GetProcAddress(module, name));
    if (!fn) {
        HRESULT hr = HRESULT_FROM_WIN32(GetLastError());
        FreeLibrary(module);
        return hr;
    }
    HRESULT hr = fn();
    FreeLibrary(module);
    return hr;
}

static HRESULT CreateCamera(IMFVirtualCamera** camera)
{
    return MFCreateVirtualCamera(
        MFVirtualCameraType_SoftwareCameraSource,
        MFVirtualCameraLifetime_System,
        MFVirtualCameraAccess_CurrentUser,
        FriendlyName,
        SourceClsid,
        nullptr,
        0,
        camera);
}

static HRESULT CheckSupported()
{
    BOOL supported = FALSE;
    HRESULT hr = MFIsVirtualCameraTypeSupported(MFVirtualCameraType_SoftwareCameraSource, &supported);
    if (FAILED(hr)) return hr;
    return supported ? S_OK : HRESULT_FROM_WIN32(ERROR_NOT_SUPPORTED);
}

static HRESULT RegisterCamera(const std::wstring& dllPath)
{
    RETURN_IF_FAILED(InvokeDllExport(dllPath, "DllRegisterServer"));
    IMFVirtualCamera* camera = nullptr;
    RETURN_IF_FAILED(CreateCamera(&camera));
    HRESULT hr = camera->Start(nullptr);
    camera->Shutdown();
    camera->Release();
    return hr;
}

static HRESULT UnregisterCamera(const std::wstring& dllPath)
{
    IMFVirtualCamera* camera = nullptr;
    HRESULT hr = CreateCamera(&camera);
    if (SUCCEEDED(hr)) {
        hr = camera->Remove();
        camera->Shutdown();
        camera->Release();
    }
    HRESULT unregisterHr = InvokeDllExport(dllPath, "DllUnregisterServer");
    return FAILED(hr) ? hr : unregisterHr;
}

int wmain(int argc, wchar_t** argv)
{
    if (argc < 2) {
        std::wcerr << L"Usage: PhoneCamCameraCtl.exe status|register|repair|unregister <PhoneCamVirtualCamera.dll>" << std::endl;
        return 2;
    }
    std::wstring command = argv[1];
    std::wstring dllPath = argc >= 3 ? argv[2] : L"PhoneCamVirtualCamera.dll";

    HRESULT hr = CoInitializeEx(nullptr, COINIT_MULTITHREADED);
    if (FAILED(hr)) { PrintHr(L"CoInitializeEx", hr); return 1; }
    hr = MFStartup(MF_VERSION);
    if (FAILED(hr)) { PrintHr(L"MFStartup", hr); CoUninitialize(); return 1; }

    if (command == L"status") hr = CheckSupported();
    else if (command == L"register") hr = RegisterCamera(dllPath);
    else if (command == L"repair") { UnregisterCamera(dllPath); hr = RegisterCamera(dllPath); }
    else if (command == L"unregister") hr = UnregisterCamera(dllPath);
    else hr = E_INVALIDARG;

    MFShutdown();
    CoUninitialize();
    if (FAILED(hr)) { PrintHr(command.c_str(), hr); return 1; }
    std::wcout << L"PhoneCam camera " << command << L" OK" << std::endl;
    return 0;
}
