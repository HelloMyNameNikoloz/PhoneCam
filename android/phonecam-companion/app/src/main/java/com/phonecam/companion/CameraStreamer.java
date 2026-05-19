package com.phonecam.companion;

import android.Manifest;
import android.content.Context;
import android.content.pm.PackageManager;
import android.graphics.ImageFormat;
import android.hardware.camera2.CameraCaptureSession;
import android.hardware.camera2.CameraCharacteristics;
import android.hardware.camera2.CameraDevice;
import android.hardware.camera2.CameraManager;
import android.hardware.camera2.CaptureRequest;
import android.media.Image;
import android.media.ImageReader;
import android.os.Handler;
import android.os.HandlerThread;
import android.util.Log;
import android.util.Range;
import android.util.Size;
import android.view.Surface;

import java.nio.ByteBuffer;
import java.util.Collections;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

final class CameraStreamer {
    private static final String TAG = "PhoneCam";

    interface Listener { void onStatus(String message); }

    private final Context context;
    private final Listener listener;
    private final ExecutorService sender = Executors.newSingleThreadExecutor();
    private HandlerThread thread;
    private Handler handler;
    private ImageReader reader;
    private CameraDevice camera;
    private CameraCaptureSession session;
    private volatile boolean sending;
    private int targetFps = 30;
    private int targetWidth = 1920;
    private int targetHeight = 1080;
    private String targetFacing = "back";
    private Range<Integer> fpsRange = new Range<>(30, 30);

    CameraStreamer(Context context, Listener listener) {
        this.context = context;
        this.listener = listener;
    }

    void start(int fps, String resolution, String facing) throws Exception {
        stop();
        targetFps = Math.max(1, fps);
        targetFacing = facing == null ? "back" : facing;
        applyResolution(resolution);
        thread = new HandlerThread("PhoneCamCamera");
        thread.start();
        handler = new Handler(thread.getLooper());
        CameraManager manager = (CameraManager) context.getSystemService(Context.CAMERA_SERVICE);
        String cameraId = chooseBackCamera(manager);
        CameraCharacteristics info = manager.getCameraCharacteristics(cameraId);
        Size size = chooseSize(info);
        fpsRange = CameraSupport.chooseFpsRange(info, targetFps);
        Log.i(TAG, "Using " + size.getWidth() + "x" + size.getHeight() + " " + fpsRange);
        reader = ImageReader.newInstance(size.getWidth(), size.getHeight(), ImageFormat.JPEG, 3);
        reader.setOnImageAvailableListener(this::onImageAvailable, handler);
        openCamera(manager, cameraId);
    }

    void stop() {
        closeQuietly(session);
        closeQuietly(camera);
        if (reader != null) {
            reader.close();
            reader = null;
        }
        if (thread != null) {
            thread.quitSafely();
            thread = null;
        }
    }

    private void openCamera(CameraManager manager, String cameraId) throws Exception {
        if (context.checkSelfPermission(Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED) {
            throw new SecurityException("Camera permission is required");
        }
        manager.openCamera(cameraId, new CameraDevice.StateCallback() {
            @Override
            public void onOpened(CameraDevice device) {
                camera = device;
                createSession();
            }

            @Override
            public void onDisconnected(CameraDevice device) {
                listener.onStatus("Camera disconnected");
                stop();
            }

            @Override
            public void onError(CameraDevice device, int error) {
                listener.onStatus("Camera error " + error);
                stop();
            }
        }, handler);
    }

    private String chooseBackCamera(CameraManager manager) throws Exception {
        for (String id : manager.getCameraIdList()) {
            CameraCharacteristics info = manager.getCameraCharacteristics(id);
            Integer facing = info.get(CameraCharacteristics.LENS_FACING);
            int wanted = "front".equals(targetFacing)
                    ? CameraCharacteristics.LENS_FACING_FRONT
                    : CameraCharacteristics.LENS_FACING_BACK;
            if (facing != null && facing == wanted) {
                return id;
            }
        }
        return manager.getCameraIdList()[0];
    }

    private Size chooseSize(CameraCharacteristics info) {
        Size[] sizes = info.get(CameraCharacteristics.SCALER_STREAM_CONFIGURATION_MAP)
                .getOutputSizes(ImageFormat.JPEG);
        Size fallback = sizes[0];
        for (Size size : sizes) {
            if (size.getWidth() == targetWidth && size.getHeight() == targetHeight) {
                return size;
            }
            if (size.getWidth() == 1280 && size.getHeight() == 720) {
                fallback = size;
            }
        }
        return fallback;
    }

    private void createSession() {
        try {
            Surface surface = reader.getSurface();
            camera.createCaptureSession(Collections.singletonList(surface), new CameraCaptureSession.StateCallback() {
                @Override
                public void onConfigured(CameraCaptureSession value) {
                    session = value;
                    startRepeating(surface);
                }

                @Override
                public void onConfigureFailed(CameraCaptureSession value) {
                    listener.onStatus("Camera session failed");
                }
            }, handler);
        } catch (Exception exc) {
            listener.onStatus(exc.getMessage());
        }
    }

    private void startRepeating(Surface surface) {
        try {
            CaptureRequest.Builder request = camera.createCaptureRequest(CameraDevice.TEMPLATE_PREVIEW);
            request.addTarget(surface);
            request.set(CaptureRequest.CONTROL_AE_TARGET_FPS_RANGE, fpsRange);
            request.set(CaptureRequest.CONTROL_AF_MODE, CaptureRequest.CONTROL_AF_MODE_CONTINUOUS_VIDEO);
            request.set(CaptureRequest.JPEG_QUALITY, jpegQuality());
            session.setRepeatingRequest(request.build(), null, handler);
            listener.onStatus("Streaming to PhoneCam on Windows");
        } catch (Exception exc) {
            listener.onStatus(exc.getMessage());
        }
    }

    private void onImageAvailable(ImageReader source) {
        try (Image image = source.acquireLatestImage()) {
            if (image == null || sending) {
                return;
            }
            sending = true;
            ByteBuffer buffer = image.getPlanes()[0].getBuffer();
            byte[] jpeg = new byte[buffer.remaining()];
            buffer.get(jpeg);
            sender.execute(() -> send(jpeg));
        } catch (Exception exc) {
            sending = false;
            listener.onStatus("Frame encode failed");
        }
    }

    private void send(byte[] jpeg) {
        try {
            NetworkClient.sendJpeg(jpeg);
        } catch (Exception exc) {
            Log.w(TAG, "Frame send failed", exc);
            listener.onStatus("Waiting for Windows bridge");
        } finally {
            sending = false;
        }
    }

    private void applyResolution(String resolution) {
        if (resolution == null || !resolution.contains("x")) {
            return;
        }
        try {
            String[] parts = resolution.split("x");
            targetWidth = Integer.parseInt(parts[0]);
            targetHeight = Integer.parseInt(parts[1]);
        } catch (Exception ignored) {
        }
    }

    private byte jpegQuality() {
        return (byte) (targetFps >= 120 ? 54 : targetFps >= 60 ? 64 : 72);
    }

    private static void closeQuietly(AutoCloseable closeable) {
        try {
            if (closeable != null) closeable.close();
        } catch (Exception ignored) {
        }
    }
}
