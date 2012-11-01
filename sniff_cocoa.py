from Foundation import NSObject, NSLog
from AppKit import NSApplication, NSApp, NSWorkspace
from Cocoa import (NSEvent,
                   NSKeyDown, NSKeyDownMask, NSKeyUp, NSKeyUpMask,
                   NSLeftMouseUp, NSLeftMouseDown, NSLeftMouseUpMask, NSLeftMouseDownMask,
                   NSRightMouseUp, NSRightMouseDown, NSRightMouseUpMask, NSRightMouseDownMask,
                   NSMouseMoved, NSMouseMovedMask,
                   NSScrollWheel, NSScrollWheelMask,
                   NSAlternateKeyMask, NSCommandKeyMask, NSControlKeyMask,
                   NSStatusBar, NSVariableStatusItemLength,
                   NSMenu, NSMenuItem)
from Quartz import CGWindowListCopyWindowInfo, kCGWindowListOptionOnScreenOnly, kCGNullWindowID
from PyObjCTools import AppHelper

class SniffCocoa:
    def __init__(self):
        self.key_hook = lambda x: True
        self.mouse_button_hook = lambda x: True
        self.mouse_move_hook = lambda x: True
        self.screen_hook = lambda x: True

    def createAppDelegate (self) :
        sc = self
        class AppDelegate(NSObject):
            def applicationDidFinishLaunching_(self, notification):
                mask = (NSKeyDownMask 
                        | NSKeyUpMask
                        | NSLeftMouseDownMask 
                        | NSLeftMouseUpMask
                        | NSRightMouseDownMask 
                        | NSRightMouseUpMask
                        | NSMouseMovedMask 
                        | NSScrollWheelMask)
                sc.find_window()
                NSEvent.addGlobalMonitorForEventsMatchingMask_handler_(mask, sc.handler)
        return AppDelegate

    def run(self):
        NSApplication.sharedApplication()
        delegate = self.createAppDelegate().alloc().init()
        NSApp().setDelegate_(delegate)
        self.workspace = NSWorkspace.sharedWorkspace()
        AppHelper.runEventLoop()

    def cancel(self):
        AppHelper.stopEventLoop()

    def read_command(self, command):
        from subprocess import Popen, PIPE
        return Popen(command, shell=True, stdout=PIPE).stdout.read()

    def get_ms_name(self, application):
        if  application == u"Microsoft Excel":
            cmd = """osascript<<END
tell application "Microsoft Excel"
	get name of active workbook
end tell
END"""
            return self.read_command(cmd)
        return u""

    
    def get_window_name(self, window):
        window_name = u""
        try:
            window_name = window['kCGWindowName']
        except KeyError as e:
            print e

        # Try to find a solution
        # Account for Microsoft Office, which sometimes does not populate the window name 
        if window['kCGWindowOwnerName'] in [u"Microsoft %s" % (x) 
                                            for x in [u"Word", u"Excel", u"PowerPoint", u"Outlook", u"Entourage"]]:
            try:
                window_name = self.get_ms_name(window['kCGWindowOwnerName'])                 
            except Error as e:
                print e 
        if window_name == u"":
            # Lame default case
            print window['kCGWindowOwnerName']
            window_name =  window['kCGWindowOwnerName'] + u"-" + str(window['kCGWindowNumber'])
        return window_name.strip()

    def find_window(self):
        try:
            activeApps = self.workspace.runningApplications()
            
            #Have to look into this if it is too slow on move and scroll,
            #right now the check is done for everything.

            for app in activeApps:
                if app.isActive():
                    options = kCGWindowListOptionOnScreenOnly
                    windowList = CGWindowListCopyWindowInfo(options,
                                                            kCGNullWindowID)
                    for window in windowList:
                        if window['kCGWindowOwnerName'] == app.localizedName():
                            geometry = window['kCGWindowBounds']
                            window_name = self.get_window_name(window)
                            print window_name
                            self.screen_hook(window['kCGWindowOwnerName'],
                                             window_name,
                                             geometry['X'],
                                             geometry['Y'], 
                                             geometry['Width'], 
                                             geometry['Height'])
                            break
                    break
        except (Exception, KeyboardInterrupt) as e:
            print e
            AppHelper.stopEventLoop()


    def handler(self, event):
        try:
            self.find_window()

            loc = NSEvent.mouseLocation()
            if event.type() == NSLeftMouseDown:
                self.mouse_button_hook(1, loc.x, loc.y)
#           elif event.type() == NSLeftMouseUp:
#               self.mouse_button_hook(1, loc.x, loc.y)
            elif event.type() == NSRightMouseDown:
                self.mouse_button_hook(3, loc.x, loc.y,)
#           elif event.type() == NSRightMouseUp:
#               self.mouse_button_hook(2, loc.x, loc.y)
            elif event.type() == NSScrollWheel:
                if event.deltaY() > 0:
                    self.mouse_button_hook(4, loc.x, loc.y)
                elif event.deltaY() < 0:
                    self.mouse_button_hook(5, loc.x, loc.y)
                if event.deltaX() > 0:
                    self.mouse_button_hook(6, loc.x, loc.y)
                elif event.deltaX() < 0:
                    self.mouse_button_hook(7, loc.x, loc.y)
#               if event.deltaX() > 0:
#                   self.mouse_button_hook(8, loc.x, loc.y)
#               elif event.deltaX() < 0:
#                   self.mouse_button_hook(9, loc.x, loc.y)
            elif event.type() == NSKeyDown:
                flags = event.modifierFlags()
                modifiers = [] # OS X api doesn't care it if is left or right
                if (flags & NSControlKeyMask):
                    modifiers.append('CONTROL')
                if (flags & NSAlternateKeyMask):
                    modifiers.append('ALTERNATE')
                if (flags & NSCommandKeyMask):
                    modifiers.append('COMMAND')
                self.key_hook(event.keyCode(), 
                              modifiers,
                              event.charactersIgnoringModifiers(),
                              event.isARepeat())
            elif event.type() == NSMouseMoved:
                self.mouse_move_hook(loc.x, loc.y)
        except (Exception, KeyboardInterrupt) as e:
            print e
            AppHelper.stopEventLoop()

if __name__ == '__main__':
    sc = SniffCocoa()
    sc.run()

