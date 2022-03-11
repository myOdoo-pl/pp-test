import re

from lxml import etree, html

from odoo import api, models

import logging

_logger = logging.getLogger(__name__)


class MailRenderMixin(models.AbstractModel):
    _inherit = "mail.render.mixin"

    def remove_href_odoo(self, value, remove_parent=True, remove_before=False):
        if len(value) < 20:
            return value
        # value can be bytes type; ensure we get a proper string
        if type(value) is bytes:
            value = value.decode()
        has_odoo_link = re.search(r"<a\s(.*)odoo\.com", value, flags=re.IGNORECASE)
        resets_password = re.search(r"password", value, flags=re.IGNORECASE)
        _logger.info(f"HAS ODOO LINK: {has_odoo_link}")
        _logger.info(f"RESETS PASSWORD: {resets_password}")
        # if has_odoo_link:
        #     value.replace("https://www.odoo.com?utm_source=db&amp;utm_medium=email", "")
        #     return value
        if has_odoo_link:
            tree = etree.HTML(
                value
            )  # html with broken links   tree = etree.fromstring(value) just xml
            odoo_achors = tree.xpath('//a[contains(@href,"www.odoo.com")]')
            for elem in odoo_achors:
                parent = elem.getparent()
                previous = elem.getprevious()

                if remove_before and not remove_parent and previous:
                    # remove 'using' that is before <a and after </span>
                    bytes_text = etree.tostring(
                        previous, pretty_print=True, method="html"
                    )
                    only_what_is_in_tags = bytes_text[: bytes_text.rfind(b">") + 1]
                    data_formatted = html.fromstring(only_what_is_in_tags)
                    parent.replace(previous, data_formatted)
                if remove_parent and len(parent.getparent()):
                    # anchor <a href odoo has a parent powered by that must be removed
                    parent.getparent().remove(parent)
                else:
                    if parent.tag == "td":  # also here can be powerd by
                        parent.getparent().remove(parent)
                    else:
                        parent.remove(elem)

            value = etree.tostring(tree, pretty_print=True, method="html")
            # etree can return bytes; ensure we get a proper string
            if type(value) is bytes:
                value = value.decode()
            return value
        else:
            return value
