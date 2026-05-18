package com.phonecam.sender;

import android.Manifest;
import android.content.Context;
import android.content.pm.PackageManager;
import android.graphics.ImageFormat;
import android.graphics.Rect;
import android.graphics.YuvImage;
import android.hardware.camera2.CameraCaptureSession;
import android.hardware.camera2.CameraCharacteristics;
import android.hardware.camera2.CameraDevice;
import android.hardware.camera2.CameraManager;
import android.hardware.camera2.CaptureRequest;
import android.media.Image;
import android.media.ImageReader;
import android.os.Handler;
import android.os.HandlerThread;
import android.util.Range;
import android.util.Size;
import android.view.Surface;

import java.io.ByteArrayOutputStream;
import java.util.Collections;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

final class CameraStreamer {
    interface Listener {
        void onStatus(String message);
    }

    private final Context context;
    private final Listener listener;
    private final ExecutorService sender = Executors.newSingleThreadExecutor();
    private HandlerThread cameraThread;
    private Handler cameraHandler;
    private ImageReader reader;
    private CameraDevice camera;
    private CameraCaptureSession session;
    private String targetUrl;
    private volatile long lastSentMs;
    private volatile boolean sending;

    CameraStreamer(Context context, Listener listener) {
        this.context = context;
        this.listener = listener;
    }

    void start(String targetUrl) throws Exception {
        this.targetUrl = targetUrl;
        stop();
        cameraThread = new HandlerThread("PhoneCamCamera");
        cameraThread.start();
        cameraHandler = new Handler(cameraThread.getLooper());
        reader = ImageReader.newInstance(1280, 720, ImageFormat.YUV_420_888, 3);
        reader.setOnImageAvailableListener(this::onImageAvailable, cameraHandler);
        openCamera();
    }

    void stop() {
        closeQuietly(session);
        closeQuietly(camera);
        if (reader != null) {
            reader.close();
            reader = null;
        }
        if (cameraThread != null) {
            cameraThread.quitSafely();
            cameraThread = null;
        }
    }

    private void openCamera() throws Exception {
        CameraManager manager = (CameraManager) context.getSystemService(Context.CAMERA_SERVICE);
        String cameraId = chooseBackCamera(manager);
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
        }, cameraHandler);
    }

    private String chooseBackCamera(CameraManager manager) throws Exception {
        for (String id : manager.getCameraIdList()) {
            CameraCharacteristics info = manager.getCameraCharacteristics(id);
            Integer facing = info.get(CameraCharacteristics.LENS_FACING);
            if (facing != null && facing == CameraCharacteristics.LENS_FACING_BACK) {
                return id;
            }
        }
        return manager.getCameraIdList()[0];
    }

    private void createSession() {
        try {
            Surface surface = reader.getSurface();
            camera.createCaptureSession(Collections.singletonList(surface), new CameraCaptureSession.StateCallback() {
                @Override
                public void onConfigured(CameraCaptureSession captureSession) {
                    session = captureSession;
                    startRepeating(surface);
                }

                @Override
                public void onConfigureFailed(CameraCaptureSession captureSession) {
                    listener.onStatus("Camera session failed");
                }
            }, cameraHandler);
        } catch (Exception exc) {
            listener.onStatus(exc.getMessage());
        }
    }

    private void startRepeating(Surface surface) {
        try {
            CaptureRequest.Builder request = camera.createCaptureRequest(CameraDevice.TEMPLATE_PREVIEW);
            request.addTarget(surface);
            request.set(CaptureRequest.CONTROL_AE_TARGET_FPS_RANGE, new Range<>(30, 30));
            session.setRepeatingRequest(request.build(), null, cameraHandler);
            listener.onStatus("Streaming to Windows receiver");
        } catch (Exception exc) {
            listener.onStatus(exc.getMessage());
        }
    }

    private void onImageAvailable(ImageReader source) {
        try (Image image = source.acquireLatestImage()) {
            if (image == null || sending || System.currentTimeMillis() - lastSentMs < 66) {
                return;
            }
            lastSentMs = System.currentTimeMillis();
            sending = true;
            byte[] nv21 = YuvConverter.toNv21(image);
            YuvImage yuv = new YuvImage(nv21, ImageFormat.NV21, image.getWidth(), image.getHeight(), null);
            ByteArrayOutputStream jpeg = new ByteArrayOutputStream();
            yuv.compressToJpeg(new Rect(0, 0, image.getWidth(), image.getHeight()), 78, jpeg);
            sender.execute(() -> send(jpeg.toByteArray()));
        } catch (Exception exc) {
            sending = false;
            listener.onStatus("Frame encode failed");
        }
    }

    private void send(byte[] jpeg) {
        try {
            NetworkClient.postJpeg(targetUrl, jpeg);
        } catch (Exception exc) {
            listener.onStatus("Receiver not reachable");
        } finally {
            sending = false;
        }
    }

    private static void closeQuietly(AutoCloseable closeable) {
        if (closeable == null) {
            return;
        }
        try {
            closeable.close();
        } catch (Exception ignored) {
        }
    }
}
