"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.electronAPI = void 0;
const electron_1 = require("electron");
exports.electronAPI = {
    setTitle: (title) => electron_1.ipcRenderer.send("set-title", title),
};
electron_1.contextBridge.exposeInMainWorld("electronAPI", exports.electronAPI);
