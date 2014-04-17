# -*- coding: iso-8859-1 -*-
"""
    MoinMoin - Action to load page content from Wikipedia2MoinMoin

    @copyright: 2007-2008 MoinMoin:ReimarBauer,
                2008 MoinMoin:ThomasWaldmann
                2013 Marcel H�fner
    @license: GNU GPL, see COPYING for details.
"""

import os
import lxml.etree
import urllib

from MoinMoin import wikiutil, config
from MoinMoin.action import ActionBase, AttachFile
from MoinMoin.PageEditor import PageEditor
from MoinMoin.Page import Page
from MoinMoin.security.textcha import TextCha


class Wikipedia(ActionBase):
    """ Load page action

    Note: the action name is the class name
    """
    def __init__(self, pagename, request):
        ActionBase.__init__(self, pagename, request)
        self.use_ticket = True
        _ = self._
        self.form_trigger = 'Load'
        self.form_trigger_label = _('Load')
        self.pagename = pagename
        self.method = 'POST'
        self.enctype = 'multipart/form-data'

    def __getWikipedia(self, language, article):
        params = { "format":"xml", "action":"query", "prop":"revisions", "rvprop":"timestamp|user|comment|content" }
        params["titles"] = "%s" % urllib.quote(article.encode("utf8"))
        qs = "&".join("%s=%s" % (k, v)  for k, v in params.items())
        url = "http://%s.wikipedia.org/w/api.php?%s" % (language, qs, )
        tree = lxml.etree.parse(urllib.urlopen(url))
        revs = tree.xpath('//rev')
        if revs:
            return revs[-1].text
        else:
            return -1

    def do_action(self):
        """ Load """
        status = False
        _ = self._
        form = self.form
        request = self.request
        # Currently we only check TextCha for upload (this is what spammers ususally do),
        # but it could be extended to more/all attachment write access
        if not TextCha(request).check_answer_from_form():
            return status, _('TextCha: Wrong answer! Go back and try again...')

        # Load Data from the form
        comment = form.get('comment', u'')
        comment = wikiutil.clean_input(comment)

        article = form.get('article',u'')
        article = wikiutil.clean_input(article)

        language = form.get('language',u'')
        language = wikiutil.clean_input(language)

        if not article:
            return False, _("No article name submited, try again.")

        rename = form.get('rename', '').strip()
        if rename:
            target = rename
        else:
            target = filename

        target = wikiutil.clean_input(target)

        if target:
            content = self.__getWikipedia(language,article)

            if not content:
                    return False, _("Article not found.")
            else:
                content = wikiutil.decodeUnknownInput(content)

            self.pagename = target
            pg = PageEditor(request, self.pagename)
            try:
                msg = pg.saveText(content, 0, comment=comment)
                status = True
            except pg.EditConflict, e:
                msg = e.message
            except pg.SaveError, msg:
                msg = unicode(msg)
        else:
            msg = _("Pagename not specified!")
        return status, msg

    def do_action_finish(self, success):
        if success:
            url = Page(self.request, self.pagename).url(self.request)
            self.request.http_redirect(url)
        else:
            self.render_msg(self.make_form(), "dialog")

    def get_form_html(self, buttons_html):
        _ = self._
        return """
<h2>%(headline)s</h2>
<p>%(explanation)s</p>
<dl>
<dt>%(upload_label_article)s</dt>
<dd>
    <select name="language">
        <option>de</option>
        <option>en</option>
    </select>
    <input type="text" name="article" size="50" value="%(pagename)s">
</dd>

<dt>%(upload_label_rename)s</dt>
<dd><input type="text" name="rename" size="50" value="%(pagename)s"></dd>

<dt>%(upload_label_comment)s</dt>
<dd><input type="text" name="comment" size="80" maxlength="200"></dd>
</dl>
%(textcha)s
<p>
<input type="hidden" name="action" value="%(action_name)s">
<input type="hidden" name="do" value="upload">
</p>
<td class="buttons">
%(buttons_html)s
</td>""" % {
    'headline': _("Upload article from wikipedia"),
    'explanation': _("You can upload an article from <a href=\"http://en.wikipedia.com/\" target=\"new\">Wikipedia</a> for the page named below. "
                     "If you change the page name, you can also upload content for another page. "
                     "If the page name is empty, we derive the page name from the file name."),
    'upload_label_article': _('Article from Wikipedia'),
    'upload_label_comment': _('Comment'),
    'upload_label_rename': _('Page name'),
    'pagename': wikiutil.escape(self.pagename, quote=1),
    'buttons_html': buttons_html,
    'action_name': self.form_trigger,
    'textcha': TextCha(self.request).render(),
}

def execute(pagename, request):
    """ Glue code for actions """
    Wikipedia(pagename, request).render()
