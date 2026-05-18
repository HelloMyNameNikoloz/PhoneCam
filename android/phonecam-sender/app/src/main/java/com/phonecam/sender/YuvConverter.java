package com.phonecam.sender;

import android.graphics.ImageFormat;
import android.media.Image;

import java.nio.ByteBuffer;

final class YuvConverter {
    private YuvConverter() {
    }

    static byte[] toNv21(Image image) {
        if (image.getFormat() != ImageFormat.YUV_420_888) {
            throw new IllegalArgumentException("Expected YUV_420_888");
        }
        int width = image.getWidth();
        int height = image.getHeight();
        byte[] output = new byte[width * height * 3 / 2];
        copyPlane(image.getPlanes()[0], width, height, output, 0, 1);
        copyChroma(image, output, width * height);
        return output;
    }

    private static void copyPlane(
            Image.Plane plane,
            int width,
            int height,
            byte[] output,
            int offset,
            int step
    ) {
        ByteBuffer buffer = plane.getBuffer();
        int rowStride = plane.getRowStride();
        int pixelStride = plane.getPixelStride();
        byte[] row = new byte[rowStride];
        int outputIndex = offset;
        for (int y = 0; y < height; y++) {
            int length = Math.min(rowStride, buffer.remaining());
            buffer.get(row, 0, length);
            for (int x = 0; x < width; x++) {
                output[outputIndex] = row[x * pixelStride];
                outputIndex += step;
            }
        }
    }

    private static void copyChroma(Image image, byte[] output, int offset) {
        Image.Plane uPlane = image.getPlanes()[1];
        Image.Plane vPlane = image.getPlanes()[2];
        ByteBuffer uBuffer = uPlane.getBuffer();
        ByteBuffer vBuffer = vPlane.getBuffer();
        int width = image.getWidth() / 2;
        int height = image.getHeight() / 2;
        byte[] uRow = new byte[uPlane.getRowStride()];
        byte[] vRow = new byte[vPlane.getRowStride()];
        int outputIndex = offset;
        for (int y = 0; y < height; y++) {
            uBuffer.get(uRow, 0, Math.min(uPlane.getRowStride(), uBuffer.remaining()));
            vBuffer.get(vRow, 0, Math.min(vPlane.getRowStride(), vBuffer.remaining()));
            for (int x = 0; x < width; x++) {
                output[outputIndex++] = vRow[x * vPlane.getPixelStride()];
                output[outputIndex++] = uRow[x * uPlane.getPixelStride()];
            }
        }
    }
}
