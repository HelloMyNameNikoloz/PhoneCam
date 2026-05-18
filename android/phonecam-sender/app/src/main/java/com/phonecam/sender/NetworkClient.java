package com.phonecam.sender;

import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;

final class NetworkClient {
    private NetworkClient() {
    }

    static void postJpeg(String targetUrl, byte[] jpeg) throws Exception {
        HttpURLConnection connection = (HttpURLConnection) new URL(targetUrl).openConnection();
        connection.setConnectTimeout(1000);
        connection.setReadTimeout(1000);
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
            throw new IllegalStateException("Receiver returned HTTP " + code);
        }
    }
}
