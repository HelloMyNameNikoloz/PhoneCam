package com.phonecam.companion;

import android.hardware.camera2.CameraCharacteristics;
import android.util.Range;

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
}
