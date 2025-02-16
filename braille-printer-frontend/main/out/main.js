"use strict";
// Main File for Electron
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const electron_1 = require("electron");
const path_1 = __importDefault(require("path"));
const electron_serve_1 = __importDefault(require("electron-serve"));
const child_process_1 = __importDefault(require("child_process"));
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
    win.on("close", () => {
        electron_1.app.quit();
    });
};
const backendPath = path_1.default.join(process.resourcesPath, "braille-printer-backend/dist/app/app");
const backendDir = electron_1.app.isPackaged
    ? path_1.default.dirname(backendPath)
    : path_1.default.join(__dirname, "../../../braille-printer-backend");
const env = {
    ...process.env,
    ANTHROPIC_API_KEY: "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",
    GROQ_API_KEY: "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"
};
electron_1.app.whenReady().then(() => {
    const subpy = electron_1.app.isPackaged
        ? child_process_1.default.spawn(backendPath, { env })
        : child_process_1.default.spawn('pipenv', ['run', 'python', 'flask_server_ai.py'], { cwd: backendDir, env });
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
