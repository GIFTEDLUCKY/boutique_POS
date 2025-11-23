import win32print
import win32con

# Use your exact printer name from Windows Devices and Printers
PRINTER_NAME = "XP-80"  # your printer name

def open_cash_drawer():
    try:
        # ESC/POS command to open cash drawer (pin 2)
        open_drawer_command = b'\x1b\x70\x00\x19\xfa'

        # Open printer
        hPrinter = win32print.OpenPrinter(PRINTER_NAME)
        hJob = win32print.StartDocPrinter(hPrinter, 1, ("Open Drawer", None, "RAW"))
        win32print.StartPagePrinter(hPrinter)
        win32print.WritePrinter(hPrinter, open_drawer_command)
        win32print.EndPagePrinter(hPrinter)
        win32print.EndDocPrinter(hPrinter)
        win32print.ClosePrinter(hPrinter)

        return True
    except Exception as e:
        print(f"Failed to open drawer: {e}")
        return False
