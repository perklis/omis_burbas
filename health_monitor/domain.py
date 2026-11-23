"""Data classes and value types from the report's base class diagram."""

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from enum import Enum


class MetricType(Enum):
    HEART_RATE = ("Пульс", "уд/мин")
    STEPS = ("Шаги", "шагов")
    CALORIES = ("Калории", "ккал")
    SLEEP = ("Сон", "ч")

    @property
    def label(self):
        return self.value[0]

    @property
    def unit(self):
        return self.value[1]


@dataclass(frozen=True)
class TimePeriod:
    start_date: date
    end_date: date
    label: str = "Период"

    @property
    def days(self):
        return (self.end_date - self.start_date).days + 1

    @classmethod
    def options(cls):
        end = date.today()
        return [
            cls(end - timedelta(days=n - 1), end, label)
            for label, n in (("День", 1), ("Неделя", 7), ("Месяц", 30), ("Год", 365))
        ]


TimePeriod.DAY, TimePeriod.WEEK, TimePeriod.MONTH, TimePeriod.YEAR = (
    TimePeriod.options()
)


@dataclass
class UserProfile:
    name: str = "Анна Смирнова"
    gender: str = "Женский"
    age: int = 29
    height: float = 168
    weight: float = 54
    id: int = 1

    @property
    def height_cm(self):
        return self.height

    @property
    def weight_kg(self):
        return self.weight


@dataclass
class DeviceInfo:
    name: str
    model: str
    connected: bool = False
    source: str = "Bluetooth"
    id: int = 0


@dataclass
class HealthMetric:
    type: MetricType
    value: float
    recorded_at: date
    id: int = 0
    device_id: int = 0

    @property
    def measured_at(self):
        return datetime.combine(self.recorded_at, datetime.min.time())


@dataclass
class NumericMetric(HealthMetric):
    pass


@dataclass
class SleepData(HealthMetric):
    deep_sleep_min: int = 0
    light_sleep_min: int = 0
    rem_sleep_min: int = 0
    awake_min: int = 0

    @property
    def duration_hours(self):
        return (self.deep_sleep_min + self.light_sleep_min + self.rem_sleep_min) / 60


@dataclass
class Report:
    metric_type: MetricType
    period: TimePeriod
    values: list[HealthMetric]
    average: float | None = None
    minimum: float | None = None
    maximum: float | None = None
    id: int = 0
    scores: dict[datetime, float] | None = None


@dataclass
class SleepReport(Report):
    phases: list[SleepData] | None = None
