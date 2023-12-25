"""Compounded support for DateTime entities"""

from __future__ import annotations
from datetime import datetime

from typing import Any

from homeassistant.components.datetime import DOMAIN as DATETIME_DOMAIN, DateTimeEntity

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ENTITY_ID
from homeassistant.core import Event, HomeAssistant, State, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity import BaseEntity


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Initialize Compounded Entities config entry."""

    reg = er.async_get(hass)
    entity_id = er.async_validate_entity_id(reg, config_entry.options[CONF_ENTITY_ID])

    async_add_entities((CompoundedDateTime()))


class CompoundedDateTime(BaseEntity, DateTimeEntity):
    """Represents a Compounded DateTime from number values"""

    @callback
    def async_child_state_change_listener(
        self, child_id: str, event: Event | None = None, state: State | None = None
    ) -> None:
        state.state

    def set_value(self, value: datetime) -> None:
        return super().set_value(value)
