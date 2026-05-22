package com.phonecam.companion;

import android.graphics.ImageFormat;
import android.hardware.camera2.CameraCharacteristics;
import android.hardware.camera2.CameraManager;
import android.util.Range;
import android.util.Size;

final class CameraSupport {
    private CameraSupport() {
    }

    static Range<Integer> chooseFpsRange(CameraCharacteristics info, int targetFps) {
        Range<Integer>[] ranges = info.get(CameraCharacteristics.CONTROL_AE_AVAILABLE_TARGET_FPS_RANGES);
        if (ranges == null || ranges.length == 0) {
            return new Range<>(targetFps, targetFps);
        }
        Range<Integer> best = ranges[0];
        int bestScore = Integer.MAX_VALUE;
        for (Range<Integer> range : ranges) {
            int lower = range.getLower();
            int upper = range.getUpper();
            int score = Math.abs(upper - targetFps) * 4 + Math.abs(lower - targetFps);
            if (lower <= targetFps && upper >= targetFps) {
                score -= 1000;
            }
            if (score < bestScore) {
                bestScore = score;
                best = range;
            }
        }
        return best;
    }

    static String chooseCameraId(CameraManager manager, String targetFacing) throws Exception {
        for (String id : manager.getCameraIdList()) {
            CameraCharacteristics info = manager.getCameraCharacteristics(id);
            Integer facing = info.get(CameraCharacteristics.LENS_FACING);
            int wanted = "front".equals(targetFacing)
                    ? CameraCharacteristics.LENS_FACING_FRONT
                    : CameraCharacteristics.LENS_FACING_BACK;
            if (facing != null && facing == wanted) return id;
        }
        return manager.getCameraIdList()[0];
    }

    static Size chooseSize(CameraCharacteristics info, int targetWidth, int targetHeight) {
        Size[] sizes = info.get(CameraCharacteristics.SCALER_STREAM_CONFIGURATION_MAP)
                .getOutputSizes(ImageFormat.JPEG);
        Size fallback = sizes[0];
        for (Size size : sizes) {
            if (size.getWidth() == targetWidth && size.getHeight() == targetHeight) return size;
            if (size.getWidth() == 1280 && size.getHeight() == 720) fallback = size;
        }
        return fallback;
    }

    static void closeQuietly(AutoCloseable closeable) {
        try {
            if (closeable != null) closeable.close();
        } catch (Exception ignored) {
        }
    }
}
