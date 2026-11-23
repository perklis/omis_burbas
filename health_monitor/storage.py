"""LocalStorage implements the three storage interfaces in the class diagram."""

import json
import random
from datetime import date, timedelta
from pathlib import Path
from .domain import (
    DeviceInfo,
    HealthMetric,
    MetricType,
    NumericMetric,
    TimePeriod,
    UserProfile,
)
from .interfaces import IDeviceStorage, IMetricStorage, IProfileStorage


class LocalStorage(IDeviceStorage, IMetricStorage, IProfileStorage):
    def __init__(self, path=None):
        self.path = Path(path or Path.home() / ".health_monitor" / "data.json")
        self.profile = UserProfile()
        self.devices = [
            DeviceInfo("Smart Band 9", "Xiaomi"),
            DeviceInfo("Galaxy Watch 7", "Samsung"),
        ]
        self.metrics: list[HealthMetric] = []
        self._load()

    def _load(self):
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            data = {}
        if data.get("profile"):
            p = data["profile"]
            self.profile = UserProfile(
                p["name"],
                p.get("gender", "Не указан"),
                int(p["age"]),
                int(p.get("height_cm", p.get("height", 168))),
                int(p.get("weight_kg", p.get("weight", 54))),
                int(p.get("id", 1)),
            )
        if data.get("devices"):
            self.devices = [DeviceInfo(**d) for d in data["devices"]]
        for ds, row in data.get("metrics", {}).items():
            for key, value in row.items():
                kind = MetricType[key]
                self.metrics.append(
                    NumericMetric(kind, float(value), date.fromisoformat(ds))
                )
        if not self.metrics:
            today = date.today()
            ranges = {
                MetricType.HEART_RATE: (72, 9),
                MetricType.STEPS: (8430, 2100),
                MetricType.CALORIES: (1860, 320),
                MetricType.SLEEP: (7.5, 1),
            }
            for n in range(364, -1, -1):
                d = today - timedelta(days=n)
                for kind, (avg, spread) in ranges.items():
                    value = max(0, random.gauss(avg, spread))
                    if kind == MetricType.SLEEP:
                        value = round(value, 1)
                    self.metrics.append(NumericMetric(kind, value, d))
            self._persist()

    def _persist(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        metrics = {}
        for m in self.metrics:
            metrics.setdefault(m.recorded_at.isoformat(), {})[m.type.name] = m.value
        data = {
            "profile": self.profile.__dict__,
            "devices": [d.__dict__ for d in self.devices],
            "metrics": metrics,
        }
        self.path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def load_devices(self):
        return self.devices

    def save_device(self, device):
        if device not in self.devices:
            self.devices.append(device)
        self._persist()

    def remove_device(self, device):
        self.devices = [d for d in self.devices if d != device]
        self._persist()

    def load_profile(self):
        return self.profile

    def save_profile(self, profile):
        self.profile = profile
        self._persist()
        return True

    def load_metrics(self, metric_type, period):
        cutoff = date.today() - timedelta(days=period.days - 1)
        return [
            m for m in self.metrics if m.type == metric_type and m.recorded_at >= cutoff
        ]

    def save_metrics(self, metrics):
        for metric in metrics:
            self.metrics = [
                m
                for m in self.metrics
                if not (m.type == metric.type and m.recorded_at == metric.recorded_at)
            ]
            self.metrics.append(metric)
        self._persist()

    # Convenience names used by UI workflow code.
    get_devices = load_devices
    get_profile = load_profile
    get_metrics = load_metrics

    def save_devices(self, devices):
        self.devices = list(devices)
        self._persist()

    def save_metric(self, metric):
        self.save_metrics([metric])
