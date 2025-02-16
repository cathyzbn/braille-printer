// Main File for Electron

import { app, BrowserWindow, ipcMain } from "electron";
import path from "path";
import serve from "electron-serve";

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

app.whenReady().then(() => {
  ipcMain.on("set-title", handleSetTitle);
  createWindow();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});