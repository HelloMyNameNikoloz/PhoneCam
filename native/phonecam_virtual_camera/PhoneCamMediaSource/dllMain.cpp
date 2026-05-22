//
// Copyright (C) Microsoft Corporation. All rights reserved.
//

// dllmain.cpp : Defines the entry point for the DLL application.
#include "pch.h"

HINSTANCE   g_hInst;
static constexpr wchar_t PhoneCamSourceClsid[] = L"{E807E3F3-AC55-490B-8371-56BC0C464978}";
static constexpr wchar_t PhoneCamSourceName[] = L"PhoneCam";

static HRESULT SetRegistryString(HKEY root, const std::wstring& key, const wchar_t* name, const std::wstring& value)
{
    HKEY handle = nullptr;
    auto status = RegCreateKeyExW(root, key.c_str(), 0, nullptr, 0, KEY_SET_VALUE, nullptr, &handle, nullptr);
    if (status != ERROR_SUCCESS) return HRESULT_FROM_WIN32(status);
    status = RegSetValueExW(handle, name, 0, REG_SZ, reinterpret_cast<const BYTE*>(value.c_str()), static_cast<DWORD>((value.size() + 1) * sizeof(wchar_t)));
    RegCloseKey(handle);
    return HRESULT_FROM_WIN32(status);
}

static std::wstring ComServerKey()
{
    return std::wstring(L"Software\\Classes\\CLSID\\") + PhoneCamSourceClsid;
}

STDAPI DllRegisterServer()
{
    wchar_t modulePath[MAX_PATH] = {};
    if (!GetModuleFileNameW(g_hInst, modulePath, ARRAYSIZE(modulePath))) return HRESULT_FROM_WIN32(GetLastError());
    RETURN_IF_FAILED(SetRegistryString(HKEY_CURRENT_USER, ComServerKey(), nullptr, PhoneCamSourceName));
    RETURN_IF_FAILED(SetRegistryString(HKEY_CURRENT_USER, ComServerKey() + L"\\InprocServer32", nullptr, modulePath));
    RETURN_IF_FAILED(SetRegistryString(HKEY_CURRENT_USER, ComServerKey() + L"\\InprocServer32", L"ThreadingModel", L"Both"));
    return S_OK;
}

STDAPI DllUnregisterServer()
{
    auto key = ComServerKey();
    RegDeleteTreeW(HKEY_CURRENT_USER, (key + L"\\InprocServer32").c_str());
    RegDeleteTreeW(HKEY_CURRENT_USER, key.c_str());
    return S_OK;
}

STDAPI DllGetClassObject(REFCLSID rclsid, REFIID riid, _COM_Outptr_ void** ppv)
{
    try
    {
        *ppv = nullptr;

        if (rclsid == __uuidof(winrt::WindowsSample::implementation::PhoneCamVirtualCameraActivate))
        {
            return winrt::make_self<PhoneCamVirtualCameraActivateFactory>()->QueryInterface(riid, ppv);
        }

#ifdef _WRL_MODULE_H_
        return ::Microsoft::WRL::Module<::Microsoft::WRL::InProc>::GetModule().GetClassObject(rclsid, riid, ppv);
#else
        return winrt::hresult_class_not_available().to_abi();
#endif
    }
    catch (...)
    {
        return winrt::to_hresult();
    }
}

bool __stdcall winrt_can_unload_now() noexcept
{
    if (winrt::get_module_lock())
    {
        return false;
    }

    winrt::clear_factory_cache();
    return true;
}

int32_t __stdcall WINRT_CanUnloadNow() noexcept
{
#ifdef _WRL_MODULE_H_
    if (!::Microsoft::WRL::Module<::Microsoft::WRL::InProc>::GetModule().Terminate())
    {
        return 1;
    }
#endif

    return winrt_can_unload_now() ? 0 : 1;
}

STDAPI_(BOOL) DllMain(_In_opt_ HINSTANCE hinst, DWORD reason, _In_opt_ void*)
{
    switch (reason)
    {
    case DLL_PROCESS_ATTACH:
        g_hInst = hinst;
        DisableThreadLibraryCalls(hinst);
        break;
    case DLL_THREAD_ATTACH:
    case DLL_THREAD_DETACH:
        break;
    case DLL_PROCESS_DETACH:
        break;
    }
    return TRUE;
}




