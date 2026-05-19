package com.phonecam.companion;

import android.Manifest;
import android.app.Activity;
import android.content.pm.PackageManager;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.os.Bundle;
import android.view.Gravity;
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
    private TextView status;
    private TextView statusPill;
    private int targetFps = 30;
    private String resolution = "1920x1080";
    private String facing = "back";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        targetFps = getIntent().getIntExtra("fps", 30);
        resolution = getIntent().getStringExtra("resolution");
        facing = getIntent().getStringExtra("facing");
        streamer = new CameraStreamer(this, this::setStatus);
        buildUi();
        requestCameraPermission();
    }

    @Override
    protected void onDestroy() {
        streamer.stop();
        super.onDestroy();
    }

    private void buildUi() {
        LinearLayout root = column(24);
        root.setPadding(dp(22), dp(34), dp(22), dp(22));
        root.setGravity(Gravity.CENTER_HORIZONTAL);
        root.setBackgroundColor(BG);

        LinearLayout brand = row(12);
        TextView mark = label("▣", 26, ACCENT, true);
        LinearLayout names = column(2);
        names.addView(label("PhoneCam", 24, TEXT, true));
        names.addView(label("USB Android Camera", 14, MUTED, false));
        brand.addView(mark);
        brand.addView(names);

        LinearLayout card = column(18);
        card.setPadding(dp(20), dp(20), dp(20), dp(20));
        card.setBackground(round(SURFACE, 22, BORDER));

        statusPill = label("Waiting", 13, ACCENT, true);
        statusPill.setGravity(Gravity.CENTER);
        statusPill.setPadding(dp(14), dp(7), dp(14), dp(7));
        statusPill.setBackground(round(0x2010a37f, 999, 0x6610a37f));

        TextView title = label("Camera bridge", 22, TEXT, true);
        TextView hint = label((resolution == null ? "1920x1080" : resolution) + " at " + targetFps + " FPS", 15, MUTED, false);
        status = label("Connect USB and open PhoneCam on Windows.", 15, MUTED, false);

        LinearLayout actions = row(10);
        actions.addView(button("Start", true), weighted());
        actions.addView(button("Stop", false), weighted());

        card.addView(statusPill, wrap());
        card.addView(title);
        card.addView(hint);
        card.addView(actions);
        card.addView(status);

        root.addView(brand, full());
        root.addView(card, full());
        setContentView(root);
    }

    private Button button(String text, boolean primary) {
        Button button = new Button(this);
        button.setText(text);
        button.setAllCaps(false);
        button.setTextColor(primary ? 0xff051611 : TEXT);
        button.setTextSize(15);
        button.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        button.setBackground(round(primary ? ACCENT : ELEVATED, 16, primary ? ACCENT : BORDER));
        button.setOnClickListener(view -> {
            if (primary) startStream();
            else {
                streamer.stop();
                setStatus("Stopped");
            }
        });
        return button;
    }

    private TextView label(String value, int sp, int color, boolean bold) {
        TextView view = new TextView(this);
        view.setText(value);
        view.setTextSize(sp);
        view.setTextColor(color);
        if (bold) view.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        return view;
    }

    private LinearLayout column(int gap) {
        LinearLayout layout = new LinearLayout(this);
        layout.setOrientation(LinearLayout.VERTICAL);
        layout.setShowDividers(LinearLayout.SHOW_DIVIDER_MIDDLE);
        layout.setDividerDrawable(new SpaceDrawable(dp(gap), false));
        return layout;
    }

    private LinearLayout row(int gap) {
        LinearLayout layout = new LinearLayout(this);
        layout.setOrientation(LinearLayout.HORIZONTAL);
        layout.setGravity(Gravity.CENTER_VERTICAL);
        layout.setShowDividers(LinearLayout.SHOW_DIVIDER_MIDDLE);
        layout.setDividerDrawable(new SpaceDrawable(dp(gap), true));
        return layout;
    }

    private GradientDrawable round(int fill, int radius, int stroke) {
        GradientDrawable drawable = new GradientDrawable();
        drawable.setColor(fill);
        drawable.setCornerRadius(dp(radius));
        drawable.setStroke(dp(1), stroke);
        return drawable;
    }

    private LinearLayout.LayoutParams full() {
        return new LinearLayout.LayoutParams(-1, -2);
    }

    private LinearLayout.LayoutParams wrap() {
        return new LinearLayout.LayoutParams(-2, -2);
    }

    private LinearLayout.LayoutParams weighted() {
        return new LinearLayout.LayoutParams(0, dp(52), 1);
    }

    private int dp(int value) {
        return (int) (value * getResources().getDisplayMetrics().density + 0.5f);
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
            streamer.start(targetFps, resolution, facing);
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
