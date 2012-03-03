#!/usr/bin/python

from colors import names

def get_pixel_colour_win(i_x, i_y):
    i_desktop_window_id = win32gui.GetDesktopWindow()
    i_desktop_window_dc = win32gui.GetWindowDC(i_desktop_window_id)
    long_colour = win32gui.GetPixel(i_desktop_window_dc, i_x, i_y)
    i_colour = int(long_colour)
    return (i_colour & 0xff), ((i_colour >> 8) & 0xff), ((i_colour >> 16) & 0xff)

def get_pixel_colour_unix(i_x, i_y):
    o_gdk_pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, 1, 1)
    o_gdk_pixbuf.get_from_drawable(gtk.gdk.get_default_root_window(), gtk.gdk.colormap_get_system(), i_x, i_y, 0, 0, 1, 1)
    return [ord(c) for c in o_gdk_pixbuf.get_pixels()][:3]

def get_mouse_position_unix():
    d = Display()
    x = d.screen().root.query_pointer()._data['root_x']
    y = d.screen().root.query_pointer()._data['root_y']
    return x, y

def get_mouse_position_win():
    from ctypes import c_ulong, Structure, windll, byref
    class POINT(Structure):
        _fields_ = [("x", c_ulong),
                    ("y", c_ulong)]

    pt = POINT()
    windll.user32.GetCursorPos(byref(pt))
    return pt.x, pt.y

def show_message_unix(text):
    class MyDialog(gtk.Window):
        def __init__(self, text):
            super(MyDialog, self).__init__()
            self.text = text
            self.show_info()
            self.start()

        def start(self):
            gtk.main()

        def show_info(self):
            md = gtk.MessageDialog(self,
                gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_INFO,
                gtk.BUTTONS_CLOSE, self.text)
            md.run()
            md.connect('event-after', gtk.main_quit)

    MyDialog(text)

def show_message_win(text, caption="Color"):
    from ctypes import c_int, WINFUNCTYPE, windll
    from ctypes.wintypes import HWND, LPCSTR, UINT
    prototype = WINFUNCTYPE(c_int, HWND, LPCSTR, LPCSTR, UINT)
    paramflags = (1, "hwnd", 0), (1, "text", "Hi"), (1, "caption", None), (1, "flags", 0)
    MessageBox = prototype(("MessageBoxA", windll.user32), paramflags)
    MessageBox(text=text, caption=caption)
    
def dec2hex(n):
    n_hex = hex(n)[2:]
    if len(n_hex) == 2:
        return n_hex
    else:
        return '0'+n_hex

def distance(c1, c2):
    r1, g1, b1 = int(c1[:2], 16), int(c1[2:4], 16), int(c1[4:], 16)
    r2, g2, b2 = int(c2[:2], 16), int(c2[2:4], 16), int(c2[4:], 16)
    return (r1-r2)**2 + (g1-g2)**2 + (b1-b2)**2

if __name__ == "__main__":
    import sys

    if sys.platform == 'linux2':
        import gtk
        from Xlib.display import Display
        get_pixel_colour = get_pixel_colour_unix
        get_mouse_position = get_mouse_position_unix
        show_message = show_message_unix
    elif sys.platform == 'win32':
        import win32gui
        get_pixel_colour = get_pixel_colour_win
        get_mouse_position = get_mouse_position_win
        show_message = show_message_win
    else:
        print 'Platform not supported'
        exit()

    x, y = get_mouse_position()

    color_dec = get_pixel_colour(x, y)
    color_hex = ''.join(map(dec2hex, color_dec)).upper()

    if color_hex in names:
        color = names[color_hex]
    else:
        color, dist = "", 10000000
        for c in names:
            if distance(c, color_hex) < dist:
                color = c
                dist = distance(c, color_hex)
        color = names[color] + ' *'
    output = 'Color: %s\nHex: %s\nDecimal: %s' %(color, color_hex, color_dec)
    show_message(output)
