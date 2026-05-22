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
    private static final int BG = 0xff0f1014;
    private static final int SURFACE = 0xff17181f;
    private static final int ELEVATED = 0xff20222b;
    private static final int BORDER = 0xff30323d;
    private static final int TEXT = 0xfff4f4f5;
    private static final int MUTED = 0xffa1a1aa;
    private static final int ACCENT = 0xff10a37f;

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
        LinearLayout root = ui.column(24);
        root.setPadding(ui.dp(22), ui.dp(34), ui.dp(22), ui.dp(22));
        root.setGravity(Gravity.CENTER_HORIZONTAL);
        root.setBackgroundColor(BG);

        LinearLayout brand = ui.row(12);
        TextView mark = ui.label("▣", 26, ACCENT, true);
        LinearLayout names = ui.column(2);
        names.addView(ui.label("PhoneCam", 24, TEXT, true));
        names.addView(ui.label("USB Android Camera", 14, MUTED, false));
        brand.addView(mark);
        brand.addView(names);

        LinearLayout card = ui.column(18);
        card.setPadding(ui.dp(20), ui.dp(20), ui.dp(20), ui.dp(20));
        card.setBackground(ui.round(SURFACE, 22, BORDER));

        statusPill = ui.label("Waiting", 13, ACCENT, true);
        statusPill.setGravity(Gravity.CENTER);
        statusPill.setPadding(ui.dp(14), ui.dp(7), ui.dp(14), ui.dp(7));
        statusPill.setBackground(ui.round(0x2010a37f, 999, 0x6610a37f));

        TextView title = ui.label("Camera bridge", 22, TEXT, true);
        hint = ui.label("", 15, MUTED, false);
        updateHint();
        status = ui.label("Connect USB and open PhoneCam on Windows.", 15, MUTED, false);

        LinearLayout actions = ui.row(10);
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
        button.setTextColor(primary ? 0xff051611 : TEXT);
        button.setTextSize(15);
        button.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        button.setBackground(ui.round(primary ? ACCENT : ELEVATED, 16, primary ? ACCENT : BORDER));
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
            statusPill.setText(message != null && message.startsWith("Streaming") ? "Live" : "Ready");
        });
    }
}
