"""Composition root matching Main -> AppInjector in the report."""

from .services import (
    BluetoothConnector,
    DeviceManager,
    ProfileService,
    StatisticalDataAnalyzer,
)
from .storage import LocalStorage


class AppInjector:
    _instance = None

    def __init__(self, storage=None):
        self.local_storage = storage or LocalStorage()
        self.profile_service = ProfileService(self.local_storage)
        self.device_manager = DeviceManager(
            self.local_storage, self.local_storage, [BluetoothConnector()]
        )
        self.data_analyzer = StatisticalDataAnalyzer(self.local_storage)

    def create_main_window(self):
        from .ui import MainWindow

        return MainWindow(self)

    def create_profile_window(self, parent, on_saved=None):
        from .ui import ProfileWindow

        return ProfileWindow(parent, self.profile_service, on_saved)

    def create_devices_window(self, parent, on_sync=None):
        from .ui import DevicesWindow

        return DevicesWindow(parent, self.device_manager, on_sync)

    def create_report_window(self, parent):
        from .ui import ReportWindow

        return ReportWindow(parent, self.data_analyzer, self.device_manager)

    def create_device_manager(self):
        return self.device_manager

    def create_profile_service(self):
        return self.profile_service

    def create_data_analyzer(self):
        return self.data_analyzer

    def create_connector(self):
        return self.device_manager.connectors[0]

    def create_metric_storage(self):
        return self.local_storage

    def create_device_storage(self):
        return self.local_storage

    def create_profile_storage(self):
        return self.local_storage

    @classmethod
    def get(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
