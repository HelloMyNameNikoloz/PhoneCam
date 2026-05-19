package com.phonecam.companion;

import java.io.DataOutputStream;
import java.io.IOException;
import java.net.InetSocketAddress;
import java.net.Socket;

final class NetworkClient {
    private static final String HOST = "127.0.0.1";
    private static final int PORT = 4768;
    private static Socket socket;
    private static DataOutputStream output;

    private NetworkClient() {
    }

    static synchronized void sendJpeg(byte[] jpeg) throws Exception {
        try {
            ensureConnected();
            output.writeInt(jpeg.length);
            output.write(jpeg);
            output.flush();
        } catch (IOException exc) {
            close();
            throw exc;
        }
    }

    private static void ensureConnected() throws IOException {
        if (socket != null && socket.isConnected() && !socket.isClosed()) {
            return;
        }
        socket = new Socket();
        socket.setTcpNoDelay(true);
        socket.connect(new InetSocketAddress(HOST, PORT), 600);
        output = new DataOutputStream(socket.getOutputStream());
    }

    private static void close() {
        try {
            if (output != null) output.close();
        } catch (IOException ignored) {
        }
        try {
            if (socket != null) socket.close();
        } catch (IOException ignored) {
        }
        output = null;
        socket = null;
    }
}
