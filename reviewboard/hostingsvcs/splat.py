"""Support for Splat as a bug tracker."""

from __future__ import unicode_literals

import logging

from django import forms
from django.utils.html import strip_tags
from django.utils.translation import ugettext_lazy as _

from reviewboard.hostingsvcs.bugtracker import BugTracker
from reviewboard.hostingsvcs.forms import HostingServiceForm
from reviewboard.hostingsvcs.service import HostingService
from reviewboard.reviews.markdown_utils import render_markdown


class SplatForm(HostingServiceForm):
    """The Splat bug tracker configuration form."""

    splat_org_name = forms.SlugField(
        label=_('Splat Organization Name'),
        max_length=64,
        required=True,
        widget=forms.TextInput(attrs={'size': 60}))


class Splat(HostingService, BugTracker):
    """The Splat bug tracker.

    Splat is a SaaS bugtracker hosted at https://hellosplat.com. It is owned
    and run by Beanbag, Inc. and is used as the official bug tracker for
    Review Board.
    """

    name = 'Splat'
    form = SplatForm
    bug_tracker_field = \
        'https://hellosplat.com/s/%(splat_org_name)s/tickets/%%s/'
    supports_bug_trackers = True

    def get_bug_info_uncached(self, repository, bug_id):
        """Return the bug info from the server.

        Args:
            repository (reviewboard.scmtools.model.Repository):
                The repository that is using Splat as a bug tracker.

            bug_id (unicode):
                The bug identifier.

        Returns:
            dict:
            A dictionary of the bug information.
        """
        result = {
            'summary': '',
            'description': '',
            'status': '',
        }

        url = (
            'https://hellosplat.com/api/orgs/%s/tickets/%s/?only-fields=status'
            ',summary,text,text_format'
            % (repository.extra_data['bug_tracker-splat_org_name'], bug_id)
        )

        try:
            rsp = self.client.json_get(url)[0]
            ticket = rsp['ticket']
        except Exception as e:
            logging.warning('Unable to fetch Splat data from %s: %s',
                            url, e, exc_info=True)
        else:
            text = ticket['text']

            if ticket['text_format'] == 'markdown':
                text = render_markdown(text)

            result = {
                'description': strip_tags(text),
                'status': ticket['status'],
                'summary': ticket['summary'],
            }

        return result
