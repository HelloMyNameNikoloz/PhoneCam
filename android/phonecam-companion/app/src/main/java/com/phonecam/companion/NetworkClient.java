package com.phonecam.companion;

import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;

final class NetworkClient {
    private NetworkClient() {
    }

    static void postJpeg(byte[] jpeg) throws Exception {
        HttpURLConnection connection = (HttpURLConnection) new URL("http://127.0.0.1:4767/frame").openConnection();
        connection.setConnectTimeout(600);
        connection.setReadTimeout(600);
        connection.setDoOutput(true);
        connection.setRequestMethod("POST");
        connection.setRequestProperty("Content-Type", "image/jpeg");
        connection.setFixedLengthStreamingMode(jpeg.length);
        try (OutputStream output = connection.getOutputStream()) {
            output.write(jpeg);
        }
        int code = connection.getResponseCode();
        connection.disconnect();
        if (code < 200 || code > 299) {
            throw new IllegalStateException("Windows bridge returned HTTP " + code);
        }
    }
}
