"use strict";
// Main File for Electron
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const electron_1 = require("electron");
const path_1 = __importDefault(require("path"));
const electron_serve_1 = __importDefault(require("electron-serve"));
const tsc_alias_1 = require("tsc-alias");
(0, tsc_alias_1.replaceTscAliasPaths)();
const dotenv_1 = __importDefault(require("dotenv"));
dotenv_1.default.config({
    path: electron_1.app.isPackaged
        ? path_1.default.join(process.resourcesPath, ".env")
        : path_1.default.resolve(process.cwd(), ".env"),
});
// eslint-disable-next-line @typescript-eslint/no-explicit-any
function handleSetTitle(event, title) {
    const webContents = event.sender;
    const win = electron_1.BrowserWindow.fromWebContents(webContents);
    if (win !== null) {
        win.setTitle(title);
    }
}
// run renderer
const isProd = process.env.NODE_ENV !== "development";
if (isProd) {
    (0, electron_serve_1.default)({ directory: "renderer/out" });
}
else {
    electron_1.app.setPath("userData", `${electron_1.app.getPath("userData")} (development)`);
}
const iconPath = electron_1.app.isPackaged ? path_1.default.join(process.resourcesPath, "assets/png/1024x1024.png") : path_1.default.join(__dirname, "../../assets/png/1024x1024.png");
const createWindow = () => {
    const win = new electron_1.BrowserWindow({
        webPreferences: {
            preload: path_1.default.join(__dirname, "preload.js"),
            devTools: !isProd,
        },
        show: false,
        icon: iconPath
    });
    // Expose URL
    if (isProd) {
        win.loadURL("app://./home.html");
    }
    else {
        // const port = process.argv[2];
        win.loadURL("http://localhost:3000/");
    }
    win.webContents.on("did-finish-load", () => {
        win.maximize();
        win.show();
    });
};
electron_1.app.whenReady().then(() => {
    electron_1.ipcMain.on("set-title", handleSetTitle);
    createWindow();
    electron_1.app.on("activate", () => {
        if (electron_1.BrowserWindow.getAllWindows().length === 0)
            createWindow();
    });
});
electron_1.app.on("window-all-closed", () => {
    if (process.platform !== "darwin")
        electron_1.app.quit();
});
