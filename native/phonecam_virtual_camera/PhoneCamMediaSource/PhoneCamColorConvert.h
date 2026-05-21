#pragma once

void CopyOrScaleBgraToNv12(
    const BYTE* source,
    UINT32 sourceWidth,
    UINT32 sourceHeight,
    UINT32 sourceStride,
    BYTE* target,
    LONG targetPitch,
    UINT32 targetWidth,
    UINT32 targetHeight);
