package com.phonecam.companion;

import android.graphics.Canvas;
import android.graphics.ColorFilter;
import android.graphics.PixelFormat;
import android.graphics.drawable.Drawable;

final class SpaceDrawable extends Drawable {
    private final int size;
    private final boolean horizontal;

    SpaceDrawable(int size, boolean horizontal) {
        this.size = size;
        this.horizontal = horizontal;
    }

    @Override
    public void draw(Canvas canvas) {
    }

    @Override
    public void setAlpha(int alpha) {
    }

    @Override
    public void setColorFilter(ColorFilter colorFilter) {
    }

    @Override
    public int getOpacity() {
        return PixelFormat.TRANSPARENT;
    }

    @Override
    public int getIntrinsicWidth() {
        return horizontal ? size : 0;
    }

    @Override
    public int getIntrinsicHeight() {
        return horizontal ? 0 : size;
    }
}
