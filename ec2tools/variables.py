"""
    Static assignments for universally used colors and variables

"""
import os
from libtools import Colors, ColorMap

# globals
c = Colors()
cm = ColorMap()

try:

    from libtools.oscodes_unix import exit_codes
    os_type = 'Linux'
    user_home = os.getenv('HOME')
    splitchar = '/'                                     # character for splitting paths (linux)

    # special colors - linux
    text = c.BLUE

except Exception:
    from libtools.oscodes_win import exit_codes           # non-specific os-safe codes
    os_type = 'Windows'
    username = os.getenv('username')
    splitchar = '\\'                                    # character for splitting paths (windows)
    user_home = 'Users' + splitchar + username
    # special colors - windows
    text = c.CYAN


# universal colors
act = c.ORANGE
rd = c.RED
yl = c.YELLOW
fs = c.GOLD3
bd = c.BOLD
gn = c.BRIGHT_GREEN
title = c.BRIGHT_WHITE + c.BOLD
cyn = c.CYAN
bcy = c.BRIGHT_CYAN
bl = c.BLUE
dbl = c.DARK_BLUE
bbc = bd + c.BRIGHT_CYAN
bbl = bd + c.BRIGHT_BLUE
bgr = c.BLUE_GRAY
highlight = bd + c.BRIGHT_BLUE
frame = text
btext = text + c.BOLD
bwt = c.BRIGHT_WHITE
bdwt = c.BOLD + c.BRIGHT_WHITE
ub = c.UNBOLD
url = c.URL
rst = c.RESET
