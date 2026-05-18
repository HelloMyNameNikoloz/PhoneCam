package com.phonecam.sender;

import android.Manifest;
import android.app.Activity;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.os.Bundle;
import android.view.Gravity;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.TextView;

public class MainActivity extends Activity {
    private static final int CAMERA_PERMISSION = 42;
    private static final String PREFS = "phonecam";
    private static final String URL_KEY = "receiverUrl";

    private CameraStreamer streamer;
    private EditText urlField;
    private TextView status;
    private SharedPreferences prefs;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        prefs = getSharedPreferences(PREFS, MODE_PRIVATE);
        streamer = new CameraStreamer(this, this::setStatus);
        buildUi();
        requestCameraPermission();
        maybeAutoStart();
    }

    @Override
    protected void onDestroy() {
        streamer.stop();
        super.onDestroy();
    }

    private void buildUi() {
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(48, 64, 48, 48);
        root.setGravity(Gravity.CENTER_HORIZONTAL);
        root.setBackgroundColor(0xff0f1014);

        TextView title = text("PhoneCam Sender", 28, 0xfff4f4f5);
        TextView hint = text("Paste the Android sender URL from the Windows app.", 16, 0xffa1a1aa);
        urlField = new EditText(this);
        urlField.setSingleLine(true);
        urlField.setTextColor(0xfff4f4f5);
        urlField.setHintTextColor(0xff71717a);
        urlField.setText(prefs.getString(URL_KEY, ""));
        urlField.setHint("http://PC-IP:4767/frame");

        Button start = button("Start stream");
        Button stop = button("Stop");
        status = text("Waiting", 15, 0xffa1a1aa);
        start.setOnClickListener(view -> startStream());
        stop.setOnClickListener(view -> {
            streamer.stop();
            setStatus("Stopped");
        });

        root.addView(title, fullWidth(-2));
        root.addView(hint, fullWidth(-2));
        root.addView(urlField, fullWidth(-2));
        root.addView(start, fullWidth(-2));
        root.addView(stop, fullWidth(-2));
        root.addView(status, fullWidth(-2));
        setContentView(root);
    }

    private TextView text(String value, int sp, int color) {
        TextView view = new TextView(this);
        view.setText(value);
        view.setTextSize(sp);
        view.setTextColor(color);
        view.setPadding(0, 12, 0, 12);
        return view;
    }

    private Button button(String value) {
        Button button = new Button(this);
        button.setText(value);
        button.setAllCaps(false);
        return button;
    }

    private LinearLayout.LayoutParams fullWidth(int height) {
        LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                height
        );
        params.setMargins(0, 12, 0, 12);
        return params;
    }

    private void requestCameraPermission() {
        if (checkSelfPermission(Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(new String[]{Manifest.permission.CAMERA}, CAMERA_PERMISSION);
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] results) {
        super.onRequestPermissionsResult(requestCode, permissions, results);
        if (requestCode == CAMERA_PERMISSION && results.length > 0
                && results[0] == PackageManager.PERMISSION_GRANTED) {
            maybeAutoStart();
        }
    }

    private void maybeAutoStart() {
        String saved = prefs.getString(URL_KEY, "");
        if (checkSelfPermission(Manifest.permission.CAMERA) == PackageManager.PERMISSION_GRANTED
                && saved != null && !saved.isEmpty()) {
            startStream();
        }
    }

    private void startStream() {
        String url = urlField.getText().toString().trim();
        if (url.isEmpty()) {
            setStatus("Enter the Windows receiver URL");
            return;
        }
        prefs.edit().putString(URL_KEY, url).apply();
        try {
            streamer.start(url);
            setStatus("Starting camera");
        } catch (Exception exc) {
            setStatus(exc.getMessage());
        }
    }

    private void setStatus(String message) {
        runOnUiThread(() -> status.setText(message == null ? "Unknown error" : message));
    }
}
