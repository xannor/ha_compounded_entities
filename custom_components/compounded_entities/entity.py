"""Base entity for the Compounded Entities integration."""
from __future__ import annotations

from typing import Any

from homeassistant.components.homeassistant import exposed_entities
from homeassistant.const import (
    ATTR_ENTITY_ID,
    STATE_UNAVAILABLE,
)
from homeassistant.core import Event, HomeAssistant, callback, State
from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.helpers.entity import DeviceInfo, Entity
from homeassistant.helpers.event import async_track_state_change_event

from .const import DOMAIN


class BaseEntity(Entity):
    """Represents a base entity."""

    _attr_should_poll = False
    _is_new_entity: bool

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry_title: str,
        domain: str,
        entities: dict[str, str],
        unique_id: str,
    ) -> None:
        """Initialize entity."""

        reg = er.async_get(hass)
        dev_reg = dr.async_get(hass)
        wrapped = {key: reg.async_get(entities[key]) for key in entities}
        target = next(
            filter(lambda e: e is not None, map(lambda t: t[1], iter(wrapped.items()))),
            None,
        )
        device_id = target.device_id if target else None
        entity_category = target.entity_category if target else None
        has_entity_name = target.has_entity_name if target else False

        name: str | None = config_entry_title
        if target:
            name = target.original_name

        self._device_id = device_id
        if device_id and (device := dev_reg.async_get(device_id)):
            self._attr_device_info = DeviceInfo(
                connections=device.connections, identifiers=device.identifiers
            )
        self._attr_entity_category = entity_category
        self._attr_has_entity_name = has_entity_name
        self._attr_name = name
        self._attr_unique_id = unique_id
        self._entities = wrapped

        self._is_new_entity = reg.async_get_entity_id(domain, DOMAIN, unique_id) is None

    @callback
    def async_child_state_change_listener(
        self, child_id: str, event: Event | None = None, state: State | None = None
    ) -> None:
        """Handle child part state"""

        return

    @callback
    def async_state_change_listener(self, event: Event | None = None) -> None:
        """Handle children updates."""

        for child, config in self._entities.items():
            if (
                state := self.hass.states.get(config.entity_id)
            ) is None or state.state == STATE_UNAVAILABLE:
                self._attr_available = False
                return
            self.async_child_state_change_listener(child, event, state)

        self._attr_available = True

    async def async_added_to_hass(self) -> None:
        """Register callbacks."""
        await super().async_added_to_hass()

        def _async_state_change_listener(event: Event | None = None) -> None:
            self.async_state_change_listener(event)
            self.async_write_ha_state()

        self.async_on_remove(
            async_track_state_change_event(
                self.hass,
                map(lambda t: t[1].entity_id, self._entities.items()),
                _async_state_change_listener,
            )
        )

        _async_state_change_listener()
