from abc import ABC, abstractmethod
from .domain import (
    DeviceInfo,
    HealthMetric,
    MetricType,
    Report,
    TimePeriod,
    UserProfile,
)


class IDeviceConnector(ABC):
    @abstractmethod
    def scan_devices(self) -> list[DeviceInfo]: ...
    @abstractmethod
    def pair(self, device: DeviceInfo) -> bool: ...
    @abstractmethod
    def unpair(self, device: DeviceInfo) -> bool: ...
    @abstractmethod
    def fetch_metrics(self, device: DeviceInfo) -> list[HealthMetric]: ...


class IDeviceStorage(ABC):
    @abstractmethod
    def load_devices(self) -> list[DeviceInfo]: ...
    @abstractmethod
    def save_device(self, device: DeviceInfo) -> None: ...
    @abstractmethod
    def remove_device(self, device: DeviceInfo) -> None: ...


class IMetricStorage(ABC):
    @abstractmethod
    def load_metrics(
        self, metric_type: MetricType, period: TimePeriod
    ) -> list[HealthMetric]: ...
    @abstractmethod
    def save_metrics(self, metrics: list[HealthMetric]) -> None: ...


class IProfileStorage(ABC):
    @abstractmethod
    def load_profile(self) -> UserProfile: ...
    @abstractmethod
    def save_profile(self, profile: UserProfile) -> bool: ...


class IDataAnalyzer(ABC):
    @abstractmethod
    def build_report(self, metric_type: MetricType, period: TimePeriod) -> Report: ...
