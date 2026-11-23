import random
from datetime import date
from .domain import (
    DeviceInfo,
    MetricType,
    NumericMetric,
    Report,
    SleepData,
    SleepReport,
    TimePeriod,
)
from .interfaces import IDataAnalyzer, IDeviceConnector


class BluetoothConnector(IDeviceConnector):
    def scan_devices(self):
        return [
            DeviceInfo("Smart Band 9", "Xiaomi"),
            DeviceInfo("Galaxy Watch 7", "Samsung"),
        ]

    def pair(self, device):
        device.connected = True
        return True

    def unpair(self, device):
        device.connected = False
        return True

    def fetch_metrics(self, device):
        if not device.connected:
            return []
        values = {
            MetricType.HEART_RATE: random.randint(60, 90),
            MetricType.STEPS: random.randint(3000, 13000),
            MetricType.CALORIES: random.randint(1100, 2700),
            MetricType.SLEEP: round(random.uniform(5, 9), 1),
        }
        return [
            NumericMetric(kind, value, date.today()) for kind, value in values.items()
        ]


class DeviceManager:
    def __init__(self, device_storage, metric_storage, connectors):
        self.device_storage = device_storage
        self.metric_storage = metric_storage
        self.connectors = connectors

    def scan_devices(self):
        known = self.device_storage.load_devices()
        if not known:
            for connector in self.connectors:
                for device in connector.scan_devices():
                    self.device_storage.save_device(device)
        return self.device_storage.load_devices()

    def get_devices(self):
        return self.device_storage.load_devices()

    def _connector(self, device):
        return self.connectors[0]

    def connect_device(self, device):
        result = self._connector(device).pair(device)
        self.device_storage.save_device(device)
        return result

    def disconnect_device(self, device):
        result = self._connector(device).unpair(device)
        self.device_storage.save_device(device)
        return result

    def synchronize(self, device=None):
        devices = [device] if device else [d for d in self.get_devices() if d.connected]
        values = []
        for item in devices:
            values.extend(self._connector(item).fetch_metrics(item))
        self.metric_storage.save_metrics(values)
        return bool(values)

    connect = connect_device
    disconnect = disconnect_device


class ProfileService:
    def __init__(self, storage):
        self.storage = storage

    def get_profile(self):
        return self.storage.load_profile()

    def validate(self, profile):
        return bool(
            profile.name.strip()
            and profile.age > 0
            and profile.height_cm > 0
            and profile.weight_kg > 0
        )

    def update_profile(self, profile):
        if not self.validate(profile):
            return False
        return self.storage.save_profile(profile)

    def save_profile(self, profile):
        return self.update_profile(profile)


class StatisticalDataAnalyzer(IDataAnalyzer):
    def __init__(self, metric_storage):
        self.metric_storage = metric_storage

    def build_report(self, metric_type, period):
        values = self.metric_storage.load_metrics(metric_type, period)
        numbers = [m.value for m in values]
        average = sum(numbers) / len(numbers) if len(numbers) > 1 else None
        minimum = min(numbers) if len(numbers) > 1 else None
        maximum = max(numbers) if len(numbers) > 1 else None
        cls = SleepReport if metric_type == MetricType.SLEEP else Report
        scores = {m.measured_at: m.value for m in values}
        report = cls(
            metric_type, period, values, average, minimum, maximum, scores=scores
        )
        if isinstance(report, SleepReport):
            report.phases = [m for m in values if isinstance(m, SleepData)]
        return report

    def calculate_average(self, values):
        return sum(m.value for m in values) / len(values) if values else 0

    def calculate_minimum(self, values):
        return min((m.value for m in values), default=0)

    def calculate_maximum(self, values):
        return max((m.value for m in values), default=0)

    def calculate_sleep_score(self, day):
        return min(100, day.duration_hours / 8 * 100)
