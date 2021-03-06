import threading

import win32con
import win32gui

from GLHF.apps import base

import bf4datatypes
import bf4datafeeder
import bf4drawing

import logging
logger = logging.getLogger(__name__)


class BF4Application(base.BaseApplication):
    CONFIG_FILE = "D:\\temp\\bf4_appinfo_dump.cfg"
    
globalLock = threading.Lock()
dataContainer = bf4datatypes.DataContainer()
app = BF4Application("BF4EH", dataContainer, globalLock)
feeder = bf4datafeeder.BF4DataFeeder(app)
centerX = (app.cfg.windowRight - app.cfg.windowLeft)/2
centerY = (app.cfg.windowBottom - app.cfg.windowTop)/2 + 10

def onPaint(hwnd, msg, wp, lp):
    hDc, ps=win32gui.BeginPaint(hwnd)
    win32gui.SetGraphicsMode(hDc, win32con.GM_ADVANCED)
    bf4drawing.setTextColor(hDc)
    
    bf4drawing.drawCrossHair(hDc, centerX, centerY, size=10)
    bf4drawing.drawSoldiers(hDc, dataContainer, globalLock, centerX, centerY)
    
    win32gui.EndPaint(hwnd, ps)
    return 0
wndproc={win32con.WM_PAINT:onPaint}

def main():
    hProcess = app.openProcess()
    feeder.initializeRPM(hProcess)
    feederThread = threading.Thread(target=feeder.run)
    feederThread.start()
    
    classAtom = app.createWindowClass(wndproc)
    hwnd = app.createWindow(classAtom)

    app.render(hwnd, classAtom)
    
    globalLock.acquire()
    app.cfg.killed = True
    globalLock.release()
    
    # clean up
    logger.info("Waiting for the feeder thread to close...")
    feederThread.join()
    logger.info("Application terminates.")
    
if __name__ == "__main__":
    logging.basicConfig()
    logging.root.setLevel(logging.DEBUG)
    main()