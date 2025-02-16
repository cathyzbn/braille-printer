// Main File for Electron

import { app, BrowserWindow, ipcMain } from "electron";
import path from "path";
import serve from "electron-serve";
import child_process from "child_process";

import dotenv from "dotenv";

dotenv.config({
  path: app.isPackaged
    ? path.join(process.resourcesPath, ".env")
    : path.resolve(process.cwd(), ".env"),
});

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function handleSetTitle(event: any, title: string) {
  const webContents = event.sender;
  const win = BrowserWindow.fromWebContents(webContents);
  if (win !== null) {
    win.setTitle(title);
  }
}

// run renderer
const isProd = process.env.NODE_ENV !== "development";
if (isProd) {
  serve({ directory: "renderer/out" });
} else {
  app.setPath("userData", `${app.getPath("userData")} (development)`);
}

const iconPath = app.isPackaged ? path.join(
  process.resourcesPath,
  "assets/png/1024x1024.png"
) : path.join(__dirname, "../../assets/png/1024x1024.png");

const createWindow = () => {
  const win = new BrowserWindow({
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      devTools: !isProd,
    },
    show: false,
    icon: iconPath
  });

  // Expose URL
  if (isProd) {
    win.loadURL("app://./home.html");
  } else {
    // const port = process.argv[2];
    win.loadURL("http://localhost:3000/");
  }

  win.webContents.on("did-finish-load", () => {
    win.maximize();
    win.show();
  });
};

const backendPath = path.join(process.resourcesPath, "braille-printer-backend/dist/app/app");

const backendDir = app.isPackaged
  ? path.dirname(backendPath)
  : path.join(__dirname, "../../../braille-printer-backend");

const env = {
  ...process.env,
  ANTHROPIC_API_KEY: "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",
  GROQ_API_KEY: "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"
}

app.whenReady().then(() => {
  const subpy = app.isPackaged
    ? child_process.spawn(backendPath, { env })
    : child_process.spawn('pipenv', ['run', 'python', 'flask_server_ai.py'], { cwd: backendDir, env });

  // handle stdout and stderr
  subpy.stdout.on("data", (data) => {
    console.log("Python: ", data.toString());
  });
  subpy.stderr.on("data", (data) => {
    console.error("Python: ", data.toString());
  });

  subpy.on("close", (code) => {
    console.log(`Python process exited with code ${code}`);
  });

  subpy.on("error", (error) => {
    console.error("Python error: ", error);
  });

  ipcMain.on("set-title", handleSetTitle);
  createWindow();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });

  app.on("before-quit", () => {
    subpy.kill();
  });
});

app.on("window-all-closed", () => {
  app.quit();
});