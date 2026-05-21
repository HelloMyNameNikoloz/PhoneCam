#include "pch.h"
#include "PhoneCamColorConvert.h"

static BYTE ClampByte(int value)
{
    if (value < 0)
    {
        return 0;
    }
    if (value > 255)
    {
        return 255;
    }
    return static_cast<BYTE>(value);
}

static BYTE BgraToY(const BYTE* pixel)
{
    int b = pixel[0];
    int g = pixel[1];
    int r = pixel[2];
    return ClampByte(((66 * r + 129 * g + 25 * b + 128) >> 8) + 16);
}

static BYTE BgraToU(int r, int g, int b)
{
    return ClampByte(((-38 * r - 74 * g + 112 * b + 128) >> 8) + 128);
}

static BYTE BgraToV(int r, int g, int b)
{
    return ClampByte(((112 * r - 94 * g - 18 * b + 128) >> 8) + 128);
}

static void BgraToNv12SameSize(
    const BYTE* source,
    UINT32 sourceStride,
    BYTE* target,
    LONG targetPitch,
    UINT32 width,
    UINT32 height)
{
    BYTE* yPlane = target;
    BYTE* uvPlane = target + targetPitch * height;

    for (UINT32 y = 0; y < height; ++y)
    {
        const BYTE* srcRow = source + y * sourceStride;
        BYTE* dstRow = yPlane + y * targetPitch;
        for (UINT32 x = 0; x < width; ++x)
        {
            dstRow[x] = BgraToY(srcRow + x * 4);
        }
    }

    for (UINT32 y = 0; y + 1 < height; y += 2)
    {
        const BYTE* row0 = source + y * sourceStride;
        const BYTE* row1 = source + (y + 1) * sourceStride;
        BYTE* dstRow = uvPlane + (y / 2) * targetPitch;
        for (UINT32 x = 0; x + 1 < width; x += 2)
        {
            const BYTE* p0 = row0 + x * 4;
            const BYTE* p1 = p0 + 4;
            const BYTE* p2 = row1 + x * 4;
            const BYTE* p3 = p2 + 4;
            int b = (p0[0] + p1[0] + p2[0] + p3[0]) / 4;
            int g = (p0[1] + p1[1] + p2[1] + p3[1]) / 4;
            int r = (p0[2] + p1[2] + p2[2] + p3[2]) / 4;
            dstRow[x] = BgraToU(r, g, b);
            dstRow[x + 1] = BgraToV(r, g, b);
        }
    }
}

void CopyOrScaleBgra(
    const BYTE* source,
    UINT32 sourceWidth,
    UINT32 sourceHeight,
    UINT32 sourceStride,
    UINT32 sourceDataSize,
    BYTE* target,
    LONG targetPitch,
    UINT32 targetWidth,
    UINT32 targetHeight)
{
    if (sourceWidth == targetWidth && sourceHeight == targetHeight && sourceStride == static_cast<UINT32>(targetPitch))
    {
        CopyMemory(target, source, sourceDataSize);
        return;
    }

    if (sourceWidth == targetWidth && sourceHeight == targetHeight)
    {
        const DWORD rowBytes = targetWidth * 4;
        for (UINT32 y = 0; y < targetHeight; ++y)
        {
            CopyMemory(target + y * targetPitch, source + y * sourceStride, rowBytes);
        }
        return;
    }

    for (UINT32 y = 0; y < targetHeight; ++y)
    {
        UINT32 sy = y * sourceHeight / targetHeight;
        const BYTE* srcRow = source + sy * sourceStride;
        BYTE* dstRow = target + y * targetPitch;
        for (UINT32 x = 0; x < targetWidth; ++x)
        {
            UINT32 sx = x * sourceWidth / targetWidth;
            CopyMemory(dstRow + x * 4, srcRow + sx * 4, 4);
        }
    }
}

void CopyOrScaleBgraToNv12(
    const BYTE* source,
    UINT32 sourceWidth,
    UINT32 sourceHeight,
    UINT32 sourceStride,
    BYTE* target,
    LONG targetPitch,
    UINT32 targetWidth,
    UINT32 targetHeight)
{
    if (sourceWidth == targetWidth && sourceHeight == targetHeight)
    {
        BgraToNv12SameSize(source, sourceStride, target, targetPitch, targetWidth, targetHeight);
        return;
    }

    BYTE* yPlane = target;
    BYTE* uvPlane = target + targetPitch * targetHeight;

    for (UINT32 y = 0; y < targetHeight; ++y)
    {
        UINT32 sy = y * sourceHeight / targetHeight;
        const BYTE* srcRow = source + sy * sourceStride;
        BYTE* dstRow = yPlane + y * targetPitch;
        for (UINT32 x = 0; x < targetWidth; ++x)
        {
            UINT32 sx = x * sourceWidth / targetWidth;
            dstRow[x] = BgraToY(srcRow + sx * 4);
        }
    }

    for (UINT32 y = 0; y + 1 < targetHeight; y += 2)
    {
        BYTE* dstRow = uvPlane + (y / 2) * targetPitch;
        for (UINT32 x = 0; x + 1 < targetWidth; x += 2)
        {
            UINT32 sx0 = x * sourceWidth / targetWidth;
            UINT32 sx1 = (x + 1) * sourceWidth / targetWidth;
            UINT32 sy0 = y * sourceHeight / targetHeight;
            UINT32 sy1 = (y + 1) * sourceHeight / targetHeight;
            const BYTE* p0 = source + sy0 * sourceStride + sx0 * 4;
            const BYTE* p1 = source + sy0 * sourceStride + sx1 * 4;
            const BYTE* p2 = source + sy1 * sourceStride + sx0 * 4;
            const BYTE* p3 = source + sy1 * sourceStride + sx1 * 4;
            int b = (p0[0] + p1[0] + p2[0] + p3[0]) / 4;
            int g = (p0[1] + p1[1] + p2[1] + p3[1]) / 4;
            int r = (p0[2] + p1[2] + p2[2] + p3[2]) / 4;
            dstRow[x] = BgraToU(r, g, b);
            dstRow[x + 1] = BgraToV(r, g, b);
        }
    }
}
