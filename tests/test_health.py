"""Health means the producer can reach Kafka, checked by fetching the topic's
partitions (the bootstrap connection closes once metadata is fetched)."""

import importlib.util
from pathlib import Path

from kafka.errors import KafkaTimeoutError

spec = importlib.util.spec_from_file_location(
    "whisper_consumer", Path(__file__).resolve().parents[1] / "whisper-consumer.py")
wc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wc)


class Producer:
    def __init__(self, answer):
        self.answer = answer

    def partitions_for(self, topic):
        if isinstance(self.answer, Exception):
            raise self.answer
        return self.answer

    def bootstrap_connected(self):
        return False  # what a healthy kafka-python producer reports


def test_reachable_when_the_topic_has_partitions():
    assert wc.kafka_reachable(Producer({0, 1}), "whispererer-log")


def test_not_reachable_on_a_metadata_timeout():
    assert not wc.kafka_reachable(Producer(KafkaTimeoutError()), "whispererer-log")


def test_not_reachable_when_the_topic_is_unknown():
    assert not wc.kafka_reachable(Producer(None), "whispererer-log")
