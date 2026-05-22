package com.phonecam.companion;

import android.Manifest;
import android.app.Activity;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Typeface;
import android.os.Bundle;
import android.view.Gravity;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;

public class MainActivity extends Activity {
    private static final int CAMERA_PERMISSION = 42;
    private static final int BG = 0xff0d0d0d;
    private static final int SURFACE = 0xff171717;
    private static final int ELEVATED = 0xff212121;
    private static final int BORDER = 0x14ffffff; // rgba(255, 255, 255, 0.08)
    private static final int TEXT = 0xffececec;
    private static final int MUTED = 0xff676767;
    private static final int ACCENT = 0xffffffff;

    private CameraStreamer streamer;
    private CompanionUi ui;
    private TextView status;
    private TextView statusPill;
    private TextView hint;
    private int targetFps = 30;
    private String resolution = "1920x1080";
    private String facing = "back";
    private String transport = "jpeg";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        readIntent(getIntent());
        ui = new CompanionUi(this);
        streamer = new CameraStreamer(this, this::setStatus);
        keepCameraSessionVisible();
        buildUi();
        requestCameraPermission();
    }

    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        setIntent(intent);
        readIntent(intent);
        updateHint();
        if (checkSelfPermission(Manifest.permission.CAMERA) == PackageManager.PERMISSION_GRANTED) {
            startStream();
        }
    }

    @Override
    protected void onDestroy() {
        streamer.stop();
        super.onDestroy();
    }

    private void buildUi() {
        LinearLayout root = ui.column(32); // Increased gap for premium feel
        root.setPadding(ui.dp(28), ui.dp(56), ui.dp(28), ui.dp(28)); // Extremely spacious margins
        root.setGravity(Gravity.CENTER_HORIZONTAL);
        root.setBackgroundColor(BG);

        LinearLayout brand = ui.row(12);
        TextView mark = ui.label("▣", 26, ACCENT, true);
        LinearLayout names = ui.column(2);
        names.addView(ui.label("PhoneCam", 22, TEXT, true)); // Clean font sizing
        names.addView(ui.label("USB Android Camera", 13, MUTED, false));
        brand.addView(mark);
        brand.addView(names);

        LinearLayout card = ui.column(24); // Airy elements inside the card
        card.setPadding(ui.dp(28), ui.dp(28), ui.dp(28), ui.dp(28)); // High-end spacing
        card.setBackground(ui.round(SURFACE, 18, BORDER)); // Refined modern radius

        statusPill = ui.label("Ready", 12, 0xffb4b4b8, true);
        statusPill.setGravity(Gravity.CENTER);
        statusPill.setPadding(ui.dp(12), ui.dp(6), ui.dp(12), ui.dp(6));
        statusPill.setBackground(ui.round(0x1a676767, 999, 0x59676767)); // Sophisticated initial state

        TextView title = ui.label("Camera bridge", 20, TEXT, true);
        hint = ui.label("", 14, MUTED, false);
        updateHint();
        status = ui.label("Connect USB and open PhoneCam on Windows.", 14, MUTED, false);

        LinearLayout actions = ui.row(12);
        actions.addView(button("Start", true), ui.weighted());
        actions.addView(button("Stop", false), ui.weighted());

        card.addView(statusPill, ui.wrap());
        card.addView(title);
        card.addView(hint);
        card.addView(actions);
        card.addView(status);

        root.addView(brand, ui.full());
        root.addView(card, ui.full());
        setContentView(root);
    }

    private Button button(String text, boolean primary) {
        Button button = new Button(this);
        button.setText(text);
        button.setAllCaps(false);
        button.setTextColor(primary ? 0xff0d0d0d : TEXT); // Pure black text on white button, or off-white on charcoal button
        button.setTextSize(14);
        button.setTypeface(Typeface.create("sans-serif-medium", Typeface.NORMAL)); // Smooth modern font weights
        button.setBackground(ui.round(primary ? ACCENT : ELEVATED, 12, primary ? ACCENT : BORDER)); // Elegant radius
        button.setOnClickListener(view -> {
            if (primary) startStream();
            else {
                streamer.stop();
                setStatus("Stopped");
            }
        });
        return button;
    }

    private void keepCameraSessionVisible() {
        setShowWhenLocked(true);
        setTurnScreenOn(true);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
    }

    private void readIntent(Intent intent) {
        targetFps = intent.getIntExtra("fps", 30);
        resolution = intent.getStringExtra("resolution");
        facing = intent.getStringExtra("facing");
        transport = intent.getStringExtra("transport");
        if (resolution == null) resolution = "1920x1080";
        if (facing == null) facing = "back";
        if (transport == null) transport = "jpeg";
    }

    private void updateHint() {
        if (hint != null) hint.setText(resolution + " at " + targetFps + " FPS");
    }

    private void requestCameraPermission() {
        if (checkSelfPermission(Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(new String[]{Manifest.permission.CAMERA}, CAMERA_PERMISSION);
        } else {
            startStream();
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] results) {
        super.onRequestPermissionsResult(requestCode, permissions, results);
        if (requestCode == CAMERA_PERMISSION && results.length > 0
                && results[0] == PackageManager.PERMISSION_GRANTED) startStream();
    }

    private void startStream() {
        try {
            streamer.start(targetFps, resolution, facing, transport);
            setStatus("Starting camera");
        } catch (Exception exc) {
            setStatus(exc.getMessage());
        }
    }

    private void setStatus(String message) {
        runOnUiThread(() -> {
            status.setText(message == null ? "Unknown error" : message);
            if (message != null && message.startsWith("Streaming")) {
                statusPill.setText("Live");
                statusPill.setTextColor(0xffa7f3d0);
                statusPill.setBackground(ui.round(0x1a10a37f, 999, 0x5910a37f));
            } else if (message != null && (message.contains("error") || message.contains("failed") || message.contains("Exception"))) {
                statusPill.setText("Error");
                statusPill.setTextColor(0xfffca5a5);
                statusPill.setBackground(ui.round(0x1adc2626, 999, 0x59dc2626));
            } else if (message != null && message.equals("Stopped")) {
                statusPill.setText("Stopped");
                statusPill.setTextColor(0xffb4b4b8);
                statusPill.setBackground(ui.round(0x1a676767, 999, 0x59676767));
            } else {
                statusPill.setText("Ready");
                statusPill.setTextColor(0xffb4b4b8);
                statusPill.setBackground(ui.round(0x1a676767, 999, 0x59676767));
            }
        });
    }
}
