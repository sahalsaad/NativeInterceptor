from collections import namedtuple

KeyboardEvent = namedtuple('KeyboardEvent', ['event_type', 'key_code',
                                             'scan_code', 'alt_pressed',
                                             'time'])
MouseEvent = namedtuple('MouseEvent', ['event_type', 'key_code',
                                       'scan_code', 'alt_pressed',
                                       'time'])
handlers = []

WM_QUIT        = 0x0012
WM_MOUSEMOVE   = 0x0200
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP   = 0x0202
WM_RBUTTONDOWN = 0x0204
WM_RBUTTONUP   = 0x0205
WM_MBUTTONDOWN = 0x0207
WM_MBUTTONUP   = 0x0208
WM_MOUSEWHEEL  = 0x020A
WM_MOUSEHWHEEL = 0x020E

MSG_TEXT = {WM_MOUSEMOVE:   'WM_MOUSEMOVE',
            WM_LBUTTONDOWN: 'WM_LBUTTONDOWN',
            WM_LBUTTONUP:   'WM_LBUTTONUP',
            WM_RBUTTONDOWN: 'WM_RBUTTONDOWN',
            WM_RBUTTONUP:   'WM_RBUTTONUP',
            WM_MBUTTONDOWN: 'WM_MBUTTONDOWN',
            WM_MBUTTONUP:   'WM_MBUTTONUP',
            WM_MOUSEWHEEL:  'WM_MOUSEWHEEL',
            WM_MOUSEHWHEEL: 'WM_MOUSEHWHEEL'}


def listen():
    """
    Calls `handlers` for each keyboard event received. This is a blocking call.
    """
    # Adapted from http://www.hackerthreads.org/Topic-42395
    from ctypes import windll, CFUNCTYPE, POINTER, c_int, c_void_p, byref
    import win32con, win32api, win32gui, atexit

    event_types = {win32con.WM_KEYDOWN: 'key down',
                   win32con.WM_KEYUP: 'key up',
                   0x104: 'key down',  # WM_SYSKEYDOWN, used for Alt key.
                   0x105: 'key up',  # WM_SYSKEYUP, used for Alt key.
                   }

    def low_level_handler(nCode, wParam, lParam):
        """
        Processes a low level Windows keyboard event.
        """
        event = KeyboardEvent(event_types[wParam], lParam[0], lParam[1],
                              lParam[2] == 32, lParam[3])
        for handler in handlers:
            handler(event)

        # Be a good neighbor and call the next hook.
        return windll.user32.CallNextHookEx(hook_id, nCode, wParam, lParam)

    def low_level_mouse_handler(nCode, wParam, lParam):
        event = KeyboardEvent(MSG_TEXT.get(wParam, str(wParam)), lParam[0], lParam[1],
                              lParam[2] == 32, lParam[3])
        for handler in handlers:
            handler(event)

        # Be a good neighbor and call the next hook.
        return windll.user32.CallNextHookEx(mouse_hook_id, nCode, wParam, lParam)

    # Our low level handler signature.
    CMPFUNC = CFUNCTYPE(c_int, c_int, c_int, POINTER(c_void_p))
    # Convert the Python handler into C pointer.
    pointer = CMPFUNC(low_level_handler)
    mouse_pointer = CMPFUNC(low_level_mouse_handler)

    # Hook both key up and key down events for common keys (non-system).
    hook_id = windll.user32.SetWindowsHookExW(win32con.WH_KEYBOARD_LL, pointer, None, 0)
    mouse_hook_id = windll.user32.SetWindowsHookExW(win32con.WH_MOUSE_LL, mouse_pointer, None, 0)

    # Register to remove the hook when the interpreter exits. Unfortunately a
    # try/finally block doesn't seem to work here.
    atexit.register(windll.user32.UnhookWindowsHookEx, hook_id)

    while True:
        msg = win32gui.GetMessage(None, 0, 0)
        win32gui.TranslateMessage(byref(msg))
        win32gui.DispatchMessage(byref(msg))


if __name__ == '__main__':
    def print_event(e):
        print(e)


    handlers.append(print_event)
    listen()
