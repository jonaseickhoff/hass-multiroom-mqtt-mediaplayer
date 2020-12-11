"""multiroom-mqtt-mediaplayer custom component"""

import logging
import voluptuous as vol

from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.helpers import config_validation as cv

DOMAIN = 'multiroom-mqtt-mediaplayer'

SERVICE_JOIN = 'join'
SERVICE_UNJOIN = 'unjoin'

ATTR_MASTER = 'master'

SERVICE_SCHEMA = vol.Schema({
    vol.Optional(ATTR_ENTITY_ID): cv.entity_ids,
})

JOIN_SERVICE_SCHEMA = SERVICE_SCHEMA.extend({
    vol.Required(ATTR_MASTER): cv.entity_id,
})

_LOGGER = logging.getLogger(__name__)


def setup(hass, config):
    """Handle service configuration."""

    async def async_service_handle(service):
        """Handle services."""
        _LOGGER.debug("service_handle from id: %s",
                      service.data.get('entity_id'))
        entity_ids = service.data.get('entity_id')
        entities = hass.data[DOMAIN].entities
        if entity_ids:
            entities = [e for e in entities if e.entity_id in entity_ids]

        if service.service == SERVICE_JOIN:
            master = [e for e in hass.data[DOMAIN].entities
                      if e.entity_id == service.data[ATTR_MASTER]]
            if master:
                client_entities = [e for e in entities
                                   if e.entity_id != master[0].entity_id]
                _LOGGER.debug("**JOIN** set clients %s for master %s",
                              [e.entity_id for e in client_entities],
                              master[0].entity_id)
                await master[0].async_join(client_entities)

        elif service.service == SERVICE_UNJOIN:
            _LOGGER.debug("**UNJOIN** entities: %s", entities)            
            for entity in entities:
                await entity.async_unjoin()

    hass.services.async_register(
        DOMAIN, SERVICE_JOIN, async_service_handle, schema=JOIN_SERVICE_SCHEMA)
    hass.services.async_register(
        DOMAIN, SERVICE_UNJOIN, async_service_handle, schema=SERVICE_SCHEMA)

    return True