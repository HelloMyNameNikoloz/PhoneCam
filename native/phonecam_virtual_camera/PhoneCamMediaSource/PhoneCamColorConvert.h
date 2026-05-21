#pragma once

void CopyOrScaleBgra(
    const BYTE* source,
    UINT32 sourceWidth,
    UINT32 sourceHeight,
    UINT32 sourceStride,
    UINT32 sourceDataSize,
    BYTE* target,
    LONG targetPitch,
    UINT32 targetWidth,
    UINT32 targetHeight);

void CopyOrScaleBgraToNv12(
    const BYTE* source,
    UINT32 sourceWidth,
    UINT32 sourceHeight,
    UINT32 sourceStride,
    BYTE* target,
    LONG targetPitch,
    UINT32 targetWidth,
    UINT32 targetHeight);
