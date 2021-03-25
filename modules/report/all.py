from monitorizer.core.config import Config
from modules.report.acunetix import AcunetixReport
from modules.report.local import LocalReport
from modules.report.slack import SlackReport
from monitorizer.ui.cli import Console


class Report(Config, Console, LocalReport, SlackReport, AcunetixReport):
    def __init__(self):
        super().__init__()