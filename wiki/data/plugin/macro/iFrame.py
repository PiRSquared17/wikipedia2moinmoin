# -*- coding: iso-8859-1 -*-
u"""
    MoinMoin - iFrame macro Version 1.0

    @copyright: 2013 MoinMoin:Marcel Häfner
    @license: GNU GPL, see COPYING for details.
"""

from MoinMoin import wikiutil
from MoinMoin.Page import Page

def macro_iFrame(macro, src, width = u"100%", height = u"95%", align = u"", scrolling = u"auto", marginheigth = u"0", marginwidth = u"0", frameborder = "0", longdesc = u""):

    request = macro.request
    formatter = macro.formatter
    _ = request.getText

    # Escape other parameters and set defaults
    src = wikiutil.escape(src)
    width = wikiutil.escape(width)
    height = wikiutil.escape(height)
    align = wikiutil.escape(align)
    scrolling = wikiutil.escape(scrolling)
    marginheight= wikiutil.escape(marginheigth)
    marginwidth = wikiutil.escape(marginwidth)
    frameborder = wikiutil.escape(frameborder)
    longdesc = wikiutil.escape(longdesc)

    # Output stuff
    result = """
<div class="iframe" style="width:%(width)s; height:%(height)s;">
    <iframe src="%(src)s" width="%(width)s" height="%(height)s" align="%(align)s" scrolling="%(scrolling)s" marginheight="%(marginheight)s" marginwidth="%(marginwidth)s" frameborder="%(frameborder)s" longdesc="%(longdesc)s">
        <p>%(error_msg)s <a href="%(src)s">%(src)s</a> </p>
    </iframe>
</div>
""" % { 'src': src,
                 'width': width,
                 'height': height,
                 'align': align,
                 'scrolling': scrolling,
                 'marginheight': marginheight,
                 'marginwidth': marginwidth,
                 'frameborder': frameborder,
                 'longdesc': longdesc,
                 'error_msg': _("Your browser cannot display inlined frames. You can call the inlined page through the following link:") }

    return formatter.rawHTML(result)