"""Unit tests for PEFT adapter state inspection using model.get_layer_status()."""

from __future__ import annotations

import pytest
from dataclasses import dataclass
from typing import Any

from evaluation.harness import inspect_peft_layer_status


@dataclass
class MockLayerStatus:
    name: str
    module_type: str
    enabled: bool
    active_adapters: list[str]
    merged_adapters: list[str] | bool
    available_adapters: list[str]


class MockPeftModelWithStatus:
    def __init__(self, adapter_name: str = "oopsie_pilot", layer_count: int = 4):
        self.adapter_name = adapter_name
        self.layer_count = layer_count
        self.enabled = True
        self.merged = False
        self.active_adapters = [adapter_name]
        self.available_adapters = [adapter_name]

    def enable_adapters(self, enabled: bool = True):
        """Simulate PEFT's callable enable_adapters method."""
        self.enabled = enabled

    def get_layer_status(self) -> list[MockLayerStatus]:
        return [
            MockLayerStatus(
                name=f"base_model.model.layers.{i}.self_attn.q_proj",
                module_type="lora",
                enabled=self.enabled,
                active_adapters=list(self.active_adapters),
                merged_adapters=self.merged,
                available_adapters=list(self.available_adapters),
            )
            for i in range(self.layer_count)
        ]

    def set_adapter(self, adapter_name: str):
        if adapter_name not in self.available_adapters:
            raise ValueError(f"Adapter {adapter_name} not available")
        self.active_adapters = [adapter_name]
        self.enabled = True

    class _DisableContext:
        def __init__(self, parent: MockPeftModelWithStatus):
            self.parent = parent
            self.prev_enabled = True

        def __enter__(self):
            self.prev_enabled = self.parent.enabled
            self.parent.enabled = False
            return self.parent

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.parent.enabled = self.prev_enabled
            return False

    def disable_adapter(self):
        return self._DisableContext(self)


def test_callable_enable_adapters_regression():
    """Demonstrate why bool(module.enable_adapters) is buggy and rejected."""
    model = MockPeftModelWithStatus()
    # A bound method in Python is always truthy
    assert callable(model.enable_adapters)
    assert bool(model.enable_adapters) is True

    # Even when disabled, the method itself remains truthy
    model.enable_adapters(False)
    assert bool(model.enable_adapters) is True  # Buggy check would falsely report True!


def test_adapted_status_verification():
    """Verify layer status for Condition B (Adapted Generation)."""
    model = MockPeftModelWithStatus(adapter_name="oopsie_pilot")
    model.set_adapter("oopsie_pilot")

    status = inspect_peft_layer_status(model, expected_adapter="oopsie_pilot")
    assert status["layer_count"] == 4
    assert status["enabled"] is True
    assert status["none_enabled"] is False
    assert status["any_merged"] is False
    assert "oopsie_pilot" in status["active_adapters"]
    assert "oopsie_pilot" in status["available_adapters"]


def test_disabled_status_inside_context_and_restoration():
    """Verify layer status for Condition A/C inside with model.disable_adapter():."""
    model = MockPeftModelWithStatus(adapter_name="oopsie_pilot")

    # Initial state: enabled
    init_status = inspect_peft_layer_status(model, expected_adapter="oopsie_pilot")
    assert init_status["enabled"] is True

    with model.disable_adapter():
        inside_status = inspect_peft_layer_status(model, expected_adapter="oopsie_pilot")
        # In PEFT, enabled is False on all layers
        assert inside_status["enabled"] is False
        assert inside_status["none_enabled"] is True
        assert inside_status["any_merged"] is False
        # active_adapters is NOT required to be empty in PEFT
        assert "oopsie_pilot" in inside_status["active_adapters"]

    # Post-context: prior state restored
    post_status = inspect_peft_layer_status(model, expected_adapter="oopsie_pilot")
    assert post_status["enabled"] is True
    assert post_status["none_enabled"] is False


def test_disabled_status_restoration_after_exception():
    """Verify adapter state is restored even after an unhandled exception inside context."""
    model = MockPeftModelWithStatus(adapter_name="oopsie_pilot")

    with pytest.raises(RuntimeError, match="Simulation exception during forward pass"):
        with model.disable_adapter():
            inside_status = inspect_peft_layer_status(model, expected_adapter="oopsie_pilot")
            assert inside_status["none_enabled"] is True
            raise RuntimeError("Simulation exception during forward pass")

    # Outside the context: prior state must be cleanly restored
    after_status = inspect_peft_layer_status(model, expected_adapter="oopsie_pilot")
    assert after_status["enabled"] is True
    assert after_status["none_enabled"] is False


def test_inconsistent_layer_status_fails_fast():
    """Assert an error is raised if layers report contradictory enabled states."""
    class InconsistentModel:
        def get_layer_status(self):
            return [
                MockLayerStatus("layer1", "lora", True, ["oopsie_pilot"], False, ["oopsie_pilot"]),
                MockLayerStatus("layer2", "lora", False, ["oopsie_pilot"], False, ["oopsie_pilot"]),
            ]

    with pytest.raises(ValueError, match="Inconsistent layer enabled states"):
        inspect_peft_layer_status(InconsistentModel(), expected_adapter="oopsie_pilot")


def test_merged_adapters_fails_fast():
    """Assert an error is raised if adapters are merged into base weights."""
    class MergedModel:
        def get_layer_status(self):
            return [
                MockLayerStatus("layer1", "lora", True, ["oopsie_pilot"], True, ["oopsie_pilot"]),
            ]

    with pytest.raises(ValueError, match="LoRA adapters are merged"):
        inspect_peft_layer_status(MergedModel(), expected_adapter="oopsie_pilot")


def test_missing_expected_adapter_fails_fast():
    """Assert an error is raised if the expected adapter is missing from available adapters."""
    class WrongAdapterModel:
        def get_layer_status(self):
            return [
                MockLayerStatus("layer1", "lora", True, ["other_adapter"], False, ["other_adapter"]),
            ]

    with pytest.raises(ValueError, match="does not have expected adapter 'oopsie_pilot'"):
        inspect_peft_layer_status(WrongAdapterModel(), expected_adapter="oopsie_pilot")
