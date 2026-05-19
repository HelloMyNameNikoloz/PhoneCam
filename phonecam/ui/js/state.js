window.PhoneCamState = {
  data: {
    devices: [],
    settings: {
      cameraFacing: "back",
      resolution: "1920x1080",
      fps: 30,
      showPreview: true,
      selectedDeviceId: null,
    },
    cameraRunning: false,
    virtualCameraInstalled: false,
    frameReceiver: {
      listening: false,
      framesReceived: 0,
      lastSize: null,
      postUrl: "http://127.0.0.1:4767/frame",
      streamUrl: "http://127.0.0.1:4767/stream.mjpg",
    },
    performance: {
      targetFps: 30,
      captureFps: 0,
      outputFps: 0,
      bridgeFps: 0,
      droppedFrames: 0,
      latencyMs: 0,
      resolution: null,
      health: "bad",
    },
    status: "waiting",
    activePanel: "camera",
    error: null,
    missingAdb: false,
    missingCompanionApk: false,
    missingScrcpy: false,
    logs: [],
  },

  merge(payload) {
    this.data = {
      ...this.data,
      ...payload,
      settings: { ...this.data.settings, ...(payload.settings || {}) },
    };
  },
};
