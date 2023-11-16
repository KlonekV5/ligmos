import os
try:
    import selenium
    import customtkinter as tk
except ImportError:
    print('Requirements not installed')
    os.system('pip install selenium')
    os.system('pip install packaging')
    os.system('pip install customtkinter')

from gui import *

app = Gui()
app.mainloop()
