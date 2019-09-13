import gettext
import gi
import time
from datetime import datetime
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from mintreport import InfoReport, InfoReportAction
import configobj

class Report(InfoReport):

    def __init__(self):

        gettext.install("mintreport", "/usr/share/linuxmint/locale", names="ngettext")

        self.icon = "software-update-urgent-symbolic"
        self.has_ignore_button = False

    def is_pertinent(self):
        # Defines whether this report should show up
        self.eol_date = None
        base_codename = None

        config = configobj.ConfigObj("/etc/os-release")
        for base_distribution in ['ubuntu', 'debian']:
            if '%s_CODENAME' % base_distribution.upper() in config:
                base_codename = config.get('%s_CODENAME' % base_distribution.upper())
                distro_info = open("/usr/share/distro-info/%s.csv" % base_distribution, "r").readlines()
                for line in distro_info[1:]:
                    elements = line.split(",")
                    if len(elements) == 6:
                        version, codename, series, created, release, eol = line.split(",")
                    elif len(elements) == 7:
                        version, codename, series, created, release, eol, eol_server = line.split(",")
                    else:
                        continue
                    if series != base_codename:
                        continue
                    self.eol_date = time.mktime(time.strptime(eol.rstrip(), '%Y-%m-%d'))
                    self.eol_date = datetime.fromtimestamp(self.eol_date)

        self.days_before_eol = (self.eol_date - datetime.now()).days
        if self.days_before_eol < 90:
            if self.days_before_eol > 0:
                self.title = _("Your version of Linux Mint will soon reach End-Of-Life (EOL)")
                self.description = ngettext('It will stop receiving support and updates in a day.', \
                                            'It will stop receiving support and updates in {num_days} days.', self.days_before_eol) \
                                            .format(num_days=self.days_before_eol)
            else:
                self.title = _("Your version of Linux Mint is no longer supported")
                self.description = ngettext('It reached End-Of-Life (EOL) yesterday.', \
                                            'It reached End-Of-Life (EOL) {num_days} days ago.', self.days_before_eol) \
                                            .format(num_days=(self.days_before_eol * -1))
            return True
        else:
            return False

    def get_descriptions(self):
        # Return the descriptions
        descriptions = []
        descriptions.append(self.description)
        descriptions.append(_("Visit %s to find information about newer releases.") % "<a href='https://www.linuxmint.com'>https://www.linuxmint.com</a>")
        return descriptions

    def get_actions(self):
        # Return available actions
        actions = []
        return actions

if __name__ == "__main__":
    report = Report()
    print(report.is_pertinent())
