""" multiroom-mqtt-mediaplayer """
import logging
import homeassistant.loader as loader
import hashlib
import voluptuous as vol
import base64
import json

from homeassistant.core import callback
from homeassistant.components.mqtt.debug_info import log_messages

from homeassistant.exceptions import TemplateError, NoEntitySpecifiedError
from homeassistant.helpers.script import Script
from homeassistant.helpers.event import (
    TrackTemplate,
    async_track_template_result,
    async_track_state_change,
)
from homeassistant.components.media_player import PLATFORM_SCHEMA, MediaPlayerEntity
from homeassistant.components import mqtt
from homeassistant.components.mqtt import (
    CONF_QOS,
    subscription
)

from homeassistant.components.media_player.const import (
    MEDIA_TYPE_MUSIC,
    SUPPORT_NEXT_TRACK,
    SUPPORT_PAUSE,
    SUPPORT_PLAY,
    SUPPORT_PREVIOUS_TRACK,
    SUPPORT_SELECT_SOURCE,
    SUPPORT_STOP,
    SUPPORT_TURN_OFF,
    SUPPORT_TURN_ON,
    SUPPORT_VOLUME_MUTE,
    SUPPORT_VOLUME_SET,
    SUPPORT_VOLUME_STEP,
)
from homeassistant.const import (
    CONF_NAME,
    STATE_OFF,
    STATE_PAUSED,
    STATE_PLAYING,
    STATE_IDLE,
)
import homeassistant.helpers.config_validation as cv

DEPENDENCIES = ["mqtt"]

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

# TOPICS

SONGTITLE = "song_title"
SONGTITLE_TOPIC = "song_title_topic"
SONGTITLE_TEMPLATE = "song_title_template"

SONGARTIST = "song_artist"
SONGARTIST_TOPIC = "song_artist_topic"
SONGARTIST_TEMPLATE = "song_artist_template"

SONGALBUM = "song_album"
SONGALBUM_TOPIC = "song_album_topic"
SONGALBUM_TEMPLATE = "song_album_template"

VOL = "volume"
VOL_TOPIC = "volume_topic"
VOL_TEMPLATE = "volume_template"

SOURCE = "source"
SOURCE_TOPIC = "source_topic"
SOURCE_TEMPLATE = "source_template"

SOURCELIST = "sourcelist"
SOURCELIST_TOPIC = "sourcelist_topic"
SOURCELIST_TEMPLATE = "sourcelist_template"

MUTE = "mute"
MUTE_TOPIC = "mute_topic"
MUTE_TEMPLATE = "mute_template"

POWER_TOPIC = "power_topic"
POWER_TEMPLATE = "power_tempalte"
POWER = "power"

PLAYERSTATUS_TOPIC = "player_status_topic"
PLAYERSTATUS_TEMPLATE = "player_status_template"
PLAYERSTATUS = "player_status"

ALBUMART = "albumart"
ALBUMART_TOPIC = "albumart_topic"
ALBUMART_TEMPLATE = "albumart_template"

ALBUMARTURL = "albumart_url"
ALBUMARTURL_TOPIC = "albumart_url_topic"
ALBUMARTURL_TEMPLATE = "albumart_url_template"

MULTIROOMCLIENTS = "multiroom_clients"
MULTIROOMCLIENTS_TOPIC = "multiroom_clients_topic"
MULTIROOMCLIENTS_TEMPLATE = "multiroom_clients_template"

MULTIROOM_MASTER = "multiroom_master"
MULTIROOM_MASTER_TOPIC = "multiroom_master_topic"
MULTIROOM_MASTER_TEMPLATE = "multiroom_master_template"

# END of TOPICS

PAYLOAD_MULTIROOM_MASTER = "payload_multiroom_master"
PAYLOAD_PLAYERSTATUS = "payload_playingstatus"
PAYLOAD_POWEROFFSTATUS = "payload_poweroff"
MULTIROOMID = "multiroom_id"

NEXT_ACTION = "next"
PREVIOUS_ACTION = "previous"
PLAY_ACTION = "play"
PAUSE_ACTION = "pause"
STOP_ACTION = "stop"
POWER_ON_ACTION = "power_on"
POWER_OFF_ACTION = "power_off"
VOL_DOWN_ACTION = "vol_down"
VOL_UP_ACTION = "vol_up"
VOL_MUTE_ACTION = "vol_mute"
VOL_UNMUTE_ACTION = "vol_unmute"
VOLUME_ACTION = "volume"
SELECT_SOURCE_ACTION = "select_source"

JOIN_ACTION = "join"
UNJOIN_ACTION = "unjoin"



ATTR_MQTTMULTIROOM_GROUP = 'mqtt_multiroom_group'

PLATFORM_SCHEMA = mqtt.MQTT_BASE_PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_NAME): cv.string,       
        vol.Optional(MULTIROOMID): cv.string,
        vol.Optional(SONGTITLE_TOPIC): mqtt.valid_subscribe_topic,
        vol.Optional(SONGTITLE_TEMPLATE): cv.template,
        vol.Optional(SONGALBUM_TOPIC): mqtt.valid_subscribe_topic,
        vol.Optional(SONGALBUM_TEMPLATE): cv.template,
        vol.Optional(SONGARTIST_TOPIC): mqtt.valid_subscribe_topic,
        vol.Optional(SONGARTIST_TEMPLATE): cv.template,
        vol.Optional(VOL_TOPIC): mqtt.valid_subscribe_topic,
        vol.Optional(VOL_TEMPLATE): cv.template,
        vol.Optional(MUTE_TOPIC): mqtt.valid_subscribe_topic,
        vol.Optional(MUTE_TEMPLATE): cv.template,
        vol.Optional(SOURCE_TOPIC): mqtt.valid_subscribe_topic,
        vol.Optional(SOURCE_TEMPLATE): cv.template,
        vol.Optional(SOURCELIST_TOPIC): mqtt.valid_subscribe_topic,
        vol.Optional(SOURCELIST_TEMPLATE): cv.template,   
        vol.Optional(POWER_TOPIC): mqtt.valid_subscribe_topic,
        vol.Optional(POWER_TEMPLATE): cv.template,
        vol.Optional(PLAYERSTATUS_TOPIC): mqtt.valid_subscribe_topic,
        vol.Optional(PLAYERSTATUS_TEMPLATE): cv.template,
        vol.Optional(ALBUMART_TOPIC): mqtt.valid_subscribe_topic,
        vol.Optional(ALBUMART_TEMPLATE): cv.template,
        vol.Optional(ALBUMARTURL_TOPIC): mqtt.valid_subscribe_topic,
        vol.Optional(ALBUMARTURL_TEMPLATE): cv.template,
        vol.Optional(MULTIROOMCLIENTS_TOPIC): mqtt.valid_subscribe_topic,
        vol.Optional(MULTIROOMCLIENTS_TEMPLATE): cv.template,
        vol.Optional(MULTIROOM_MASTER_TOPIC): mqtt.valid_subscribe_topic,
        vol.Optional(MULTIROOM_MASTER_TEMPLATE): cv.template,
        vol.Optional(NEXT_ACTION): cv.SCRIPT_SCHEMA,
        vol.Optional(PREVIOUS_ACTION): cv.SCRIPT_SCHEMA,
        vol.Optional(PLAY_ACTION): cv.SCRIPT_SCHEMA,
        vol.Optional(PAUSE_ACTION): cv.SCRIPT_SCHEMA,
        vol.Optional(STOP_ACTION): cv.SCRIPT_SCHEMA,
        vol.Optional(VOLUME_ACTION): cv.SCRIPT_SCHEMA,
        vol.Optional(VOL_DOWN_ACTION): cv.SCRIPT_SCHEMA,
        vol.Optional(VOL_UP_ACTION): cv.SCRIPT_SCHEMA,
        vol.Optional(VOL_MUTE_ACTION): cv.SCRIPT_SCHEMA,
        vol.Optional(VOL_UNMUTE_ACTION): cv.SCRIPT_SCHEMA,
        vol.Optional(POWER_ON_ACTION): cv.SCRIPT_SCHEMA,
        vol.Optional(POWER_OFF_ACTION): cv.SCRIPT_SCHEMA,
        vol.Optional(SELECT_SOURCE_ACTION): cv.SCRIPT_SCHEMA,
        vol.Optional(JOIN_ACTION): cv.SCRIPT_SCHEMA,
        vol.Optional(UNJOIN_ACTION): cv.SCRIPT_SCHEMA,
        vol.Optional(PAYLOAD_PLAYERSTATUS): cv.string,
        vol.Optional(PAYLOAD_POWEROFFSTATUS): cv.string,  
        vol.Optional(PAYLOAD_MULTIROOM_MASTER): cv.string
    }
)

class MultiroomData:
    """Storage class for platform global data."""

    def __init__(self):
        """Initialize the data."""
        self.entities = []

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the MQTT Media Player platform."""
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = MultiroomData()

    add_entities([MQTTMediaPlayer(hass, config)],)


class MQTTMediaPlayer(MediaPlayerEntity):

    """MQTTMediaPlayer"""

    def __init__(self, hass, config):
        """Initialize"""
        self.hass = hass
        self._domain = DOMAIN
        self._name = config.get(CONF_NAME)
        self._sub_state = None
        self._topic = None
        self._payload = None
        self._templates = None
        self._supported_features = 0

        self._volume = 0.0
        self._track_name = ""
        self._track_artist = ""
        self._track_album_name = ""
        self._mqtt_player_state = None
        self._state = None
        self._albumart = None
        self._albumart_url = ""
        self._source = None
        self._source_list = []
        self._mute = False
        self._power = "standby"
        self._next_script = None
        self._previous_script = None
        self._play_script = None
        self._pause_script = None
        self._stop_script = None
        self._vol_down_script = None
        self._vol_up_script = None
        self._vol_mute_script = None
        self._vol_unmute_script = None
        self._vol_script = None
        self._power_on_script = None
        self._power_off_script = None
        self._select_source_script = None
        self._join_script = None
        self._unjoin_script = None
        self._isGroupMaster = None


        if next_action := config.get(NEXT_ACTION):
            self._next_script = Script(hass, next_action, self._name, self._domain)
        if previous_action := config.get(PREVIOUS_ACTION):
            self._previous_script = Script(hass, previous_action, self._name, self._domain)
        if play_action := config.get(PLAY_ACTION):
            self._play_script = Script(hass, play_action, self._name, self._domain)
        if pause_action := config.get(PAUSE_ACTION):
            self._pause_script = Script(hass, pause_action, self._name, self._domain)
        if stop_action := config.get(STOP_ACTION):
            self._stop_script = Script(hass, stop_action, self._name, self._domain)
        if vol_down_action := config.get(VOL_DOWN_ACTION):
            self._vol_down_script = Script(hass, vol_down_action, self._name, self._domain)
        if vol_up_action :=config.get(VOL_UP_ACTION):
            self._vol_up_script = Script(hass, vol_up_action, self._name, self._domain)
        if vol_mute_action := config.get(VOL_MUTE_ACTION):
            self._vol_mute_script = Script(hass, vol_mute_action, self._name, self._domain)
        if vol_unmute_action := config.get(VOL_UNMUTE_ACTION):
            self._vol_unmute_script = Script(hass, vol_unmute_action, self._name, self._domain)
        if volume_action := config.get(VOLUME_ACTION):
            self._vol_script = Script(hass, volume_action, self._name, self._domain)
        if power_on_action :=config.get(POWER_ON_ACTION):
            self._power_on_script = Script(hass, power_on_action, self._name, self._domain)
        if power_off_action :=config.get(POWER_OFF_ACTION):
            self._power_off_script = Script(hass, power_off_action, self._name, self._domain)
        if select_source_action :=config.get(SELECT_SOURCE_ACTION):
            self._select_source_script = Script(hass, select_source_action, self._name, self._domain)
        if join_action :=config.get(JOIN_ACTION):
            self._join_script = Script(hass, join_action, self._name, self._domain)
        if unjoin_action :=config.get(UNJOIN_ACTION):
            self._unjoin_script = Script(hass, unjoin_action, self._name, self._domain)

        self._supported_features = (
            SUPPORT_PLAY
            | SUPPORT_PAUSE
            | SUPPORT_PREVIOUS_TRACK
            | SUPPORT_NEXT_TRACK
            | SUPPORT_VOLUME_STEP
        )

        self._supported_features |= (self._vol_mute_script is not None and self._vol_unmute_script is not None and SUPPORT_VOLUME_MUTE)
        self._supported_features |= self._power_off_script is not None and SUPPORT_TURN_OFF
        self._supported_features |= self._power_on_script is not None and SUPPORT_TURN_ON
        self._supported_features |= self._vol_script is not None and SUPPORT_VOLUME_SET
        self._supported_features |= self._stop_script is not None and SUPPORT_STOP
        self._supported_features |= self._select_source_script is not None and SUPPORT_SELECT_SOURCE

        # Load config
        self._setup_from_config(config)


    def _setup_from_config(self, config):
        """(Re)Setup the entity."""

        self._multiroomid = config.get(MULTIROOMID)
        if self._multiroomid:
            self._multiroom_group = [self]
            self._multiroom_groupIds = []


        self._config = config
        self._topic = {
            key: config.get(key)
            for key in (
                POWER_TOPIC,
                PLAYERSTATUS_TOPIC,
                SOURCE_TOPIC,
                SOURCELIST_TOPIC,
                VOL_TOPIC,
                MUTE_TOPIC,
                SONGTITLE_TOPIC,
                SONGARTIST_TOPIC,
                SONGALBUM_TOPIC,
                ALBUMART_TOPIC,
                ALBUMARTURL_TOPIC,
                MULTIROOMCLIENTS_TOPIC,
                MULTIROOM_MASTER_TOPIC,
            )
        }
        self._templates = {
            POWER: config.get(POWER_TEMPLATE),
            PLAYERSTATUS: config.get(PLAYERSTATUS_TEMPLATE),
            SOURCE: config.get(SOURCE_TEMPLATE),
            SOURCELIST: config.get(SOURCELIST_TEMPLATE),
            VOL: config.get(VOL_TEMPLATE),
            MUTE: config.get(MUTE_TEMPLATE),
            SONGTITLE: config.get(SONGTITLE_TEMPLATE),
            SONGARTIST: config.get(SONGARTIST_TEMPLATE),
            SONGALBUM: config.get(SONGALBUM_TEMPLATE),
            ALBUMART: config.get(ALBUMART_TEMPLATE),
            ALBUMARTURL: config.get(ALBUMARTURL_TEMPLATE),
            MULTIROOMCLIENTS: config.get(MULTIROOMCLIENTS_TEMPLATE),
            MULTIROOM_MASTER: config.get(MULTIROOM_MASTER_TEMPLATE),
        }
        self._payload = {
             "POWER_OFF": config[PAYLOAD_POWEROFFSTATUS],
             "PLAYER_PLAYING": config[PAYLOAD_PLAYERSTATUS],
             "MULTIROOM_MASTER": config[PAYLOAD_MULTIROOM_MASTER]
        }

        for key, tpl in list(self._templates.items()):
            if tpl is None:
                self._templates[key] = lambda value: value
            else:
                tpl.hass = self.hass
                self._templates[key] = tpl.async_render_with_possible_json_value
                
    def update(self):
        """ Update the States"""
        if self._power == self._payload["POWER_OFF"]:
            self._state = STATE_OFF
        elif self._payload["PLAYER_PLAYING"]:
            if self._mqtt_player_state == self._payload["PLAYER_PLAYING"]:
                self._state = STATE_PLAYING
            else:
                self._state = STATE_PAUSED

    @property
    def should_poll(self):
        return False

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    @property
    def volume_level(self):
        """Volume level of the media player (0..1)."""
        return self._volume

    @property
    def is_volume_muted(self):
        """Boolean if volume is currently muted."""
        return self._mute == True or self._mute == "true"

    @property
    def media_content_type(self):
        """Content type of current playing media."""
        return MEDIA_TYPE_MUSIC

    @property
    def media_title(self):
        """Title of current playing media."""
        return self._track_name

    @property
    def media_artist(self):
        """Artist of current playing media, music track only."""
        return self._track_artist

    @property
    def media_album_name(self):
        """Album name of current playing media, music track only."""
        return self._track_album_name

    @property
    def supported_features(self):
        """Flag media player features that are supported."""
        return self._supported_features

    @property
    def media_image_url(self):
        """Image url of current playing media."""
        return self._albumart_url

    @property
    def media_image_hash(self):
        """Hash value for media image."""
        if self._albumart_url:
            return super().media_image_hash
        if self._albumart:
            return hashlib.md5(self._albumart).hexdigest()[:5]
        return None

    @property
    def source(self):
        """Name of the current input source."""
        return self._source

    @property
    def source_list(self):
        """List of available input sources."""
        return self._source_list

    @property
    def shuffle(self):
        """Boolean if shuffle is enabled."""
        return None

    @property
    def repeat(self):
        """Return current repeat mode."""
        return None

    @property
    def is_master(self):
        """Return true if it is a master."""
        return self._isGroupMaster

    async def async_get_media_image(self):
        """Fetch media image of current playing image."""
        if self._albumart_url:
            return await super().async_get_media_image()
        if self._albumart:
            return (self._albumart, "image/jpeg")
        return None, None

    async def async_turn_on(self):
        """Turn the media player on."""
        if self._power_on_script:
            await self._power_on_script.async_run(context=self._context)

    async def async_turn_off(self):
        """Turn the media player off."""
        if self._power_off_script:
            await self._power_off_script.async_run(context=self._context)

    async def async_volume_up(self):
        """Volume up the media player."""
        if self._vol_up_script:
            await self._vol_up_script.async_run(context=self._context)
        else:
            newvolume = min(self._volume + 0.05, 1)
            self._volume = newvolume
            await self.async_set_volume_level(newvolume)

    async def async_volume_down(self):
        """Volume down media player."""
        if self._vol_down_script:
            await self._vol_down_script.async_run(context=self._context)
        else:
            newvolume = max(self._volume - 0.05, 0)
            self._volume = newvolume
            await self.async_set_volume_level(newvolume)

    async def async_set_volume_level(self, volume):
        """Set volume level."""
        if self._vol_down_script or self._vol_up_script:
            return
        if self._vol_script:
            await self._vol_script.async_run(
                {"volume": volume * 100}, context=self._context
            )
            self._volume = volume

    async def async_mute_volume(self, mute):
        if mute:
            if self._vol_mute_script:
                await self._vol_mute_script.async_run(context=self._context)
        else:
            if self._vol_unmute_script:
                await self._vol_unmute_script.async_run(context=self._context)

    async def async_media_play_pause(self):
        """Simulate play pause media player."""
        if self._state == STATE_PLAYING:
            await self.async_media_pause()
        else:
            await self.async_media_play()

    async def async_media_play(self):
        """Send play command."""
        if self._play_script:
            await self._play_script.async_run(context=self._context)
            self._state = STATE_PLAYING

    async def async_media_pause(self):
        """Send media pause command to media player."""
        if self._pause_script:
            await self._pause_script.async_run(context=self._context)
            self._state = STATE_PAUSED

    async def async_media_stop(self):
        """Send media stop command to media player."""
        if self._stop_script:
            await self._stop_script.async_run(context=self._context)
            self._state = STATE_IDLE

    async def async_media_next_track(self):
        """Send next track command."""
        if self._next_script:
            await self._next_script.async_run(context=self._context)

    async def async_media_previous_track(self):
        """Send the previous track command."""
        if self._previous_script:
            await self._previous_script.async_run(context=self._context)

    async def async_select_source(self, source):
        """Select input source."""
        if self._select_source_script:
            await self._select_source_script.async_run(
                {"source": source}, context=self._context
            )

    # Multiroom 

    async def async_added_to_hass(self):
        """Record entity."""
        await super().async_added_to_hass()
        self.hass.data[DOMAIN].entities.append(self)
        await self._subscribe_topics()


    async def async_will_remove_from_hass(self):
        """Unsubscribe when removed."""
        self._sub_state = await subscription.async_unsubscribe_topics(
            self.hass, self._sub_state
        )

    async def async_join(self, client_entities):
        """Select input source."""
        if self._join_script:
            _LOGGER.debug("Join script: %s", list(map(lambda e: e.multiroom_id, client_entities)))
            await self._join_script.async_run(
                {"master_id": self.multiroom_id, "client_ids": list(map(lambda e: e.multiroom_id, client_entities))}, context=self._context
            )
            
    async def async_unjoin(self):
        """Select input source."""
        if self._unjoin_script:
            await self._unjoin_script.async_run(
                {"client_id": self.multiroom_id}, context=self._context
            )

    @property
    def multiroom_id(self):
        """Return the ip address of the device."""
        return self._multiroomid

    @property
    def musiccast_group(self):
        """Return the list of entities in the group."""
        return self._multiroom_group

    def refresh_group(self):
        """Refresh the entities that are part of the group."""
        _LOGGER.debug("Refreshing group data for entity: %s", self.entity_id)
        entities = self.hass.data[DOMAIN].entities
        client_entities = [e for e in entities
                           if e.multiroom_id in self._multiroom_groupIds]
        self._multiroom_group = [self] + client_entities
        if MQTTMediaPlayer:
            self.schedule_update_ha_state(False)

    @property
    def device_state_attributes(self):
        """Return entity specific state attributes."""
        attributes = {
            ATTR_MQTTMULTIROOM_GROUP: [e.entity_id for e
                                   in self._multiroom_group],
        }
        return attributes


    async def _subscribe_topics(self):
        """(Re)Subscribe to topics."""
        topics = {}

        @callback
        @log_messages(self.hass, self.entity_id)
        def power_received(msg):
            """Handle new received MQTT message."""
            payload = self._templates[POWER](msg.payload)
            self._power = payload
            if MQTTMediaPlayer:
                self.schedule_update_ha_state(True)


        if self._topic[POWER_TOPIC] is not None:
            topics[POWER_TOPIC] = {
                "topic": self._topic[POWER_TOPIC],
                "msg_callback": power_received,
                "qos": self._config[CONF_QOS],
            }

        @callback
        @log_messages(self.hass, self.entity_id)
        def playerstatus_received(msg):
            """Handle new received MQTT message."""
            payload = self._templates[PLAYERSTATUS](msg.payload)
            self._mqtt_player_state = payload
            if MQTTMediaPlayer:
                self.schedule_update_ha_state(True)
           

        if self._topic[PLAYERSTATUS_TOPIC] is not None:
            topics[PLAYERSTATUS_TOPIC] = {
                "topic": self._topic[PLAYERSTATUS_TOPIC],
                "msg_callback": playerstatus_received,
                "qos": self._config[CONF_QOS],
            }

        @callback
        @log_messages(self.hass, self.entity_id)
        def source_received(msg):
            """Handle new received MQTT message."""
            payload = self._templates[SOURCE](msg.payload)
            self._source = payload
            if MQTTMediaPlayer:
                self.schedule_update_ha_state(False)
           

        if self._topic[SOURCE_TOPIC] is not None:
            topics[SOURCE_TOPIC] = {
                "topic": self._topic[SOURCE_TOPIC],
                "msg_callback": source_received,
                "qos": self._config[CONF_QOS],
            }

        @callback
        @log_messages(self.hass, self.entity_id)
        def sourcelist_received(msg):
            """Handle new received MQTT message."""
            payload = self._templates[SOURCELIST](msg.payload)
            if(isinstance(payload, str)):
                self._source_list = json.loads(payload)
            if(isinstance(payload, list)):
                self._source_list = payload
            if MQTTMediaPlayer:
                self.schedule_update_ha_state(False)
           

        if self._topic[SOURCELIST_TOPIC] is not None:
            topics[SOURCELIST_TOPIC] = {
                "topic": self._topic[SOURCELIST_TOPIC],
                "msg_callback": sourcelist_received,
                "qos": self._config[CONF_QOS],
            }

        @callback
        @log_messages(self.hass, self.entity_id)
        def volume_received(msg):
            """Handle new received MQTT message."""
            payload = self._templates[SOURCELIST](msg.payload)
            if isinstance(payload, int):
                self._volume = int(payload) / 100.0
            if isinstance(payload, str):
                try:
                    self._volume = float(payload) / 100.0
                except:
                    pass
            if MQTTMediaPlayer:
                self.schedule_update_ha_state(False)
           

        if self._topic[VOL_TOPIC] is not None:
            topics[VOL_TOPIC] = {
                "topic": self._topic[VOL_TOPIC],
                "msg_callback": volume_received,
                "qos": self._config[CONF_QOS],
            }
        
        @callback
        @log_messages(self.hass, self.entity_id)
        def mute_received(msg):
            """Handle new received MQTT message."""
            payload = self._templates[MUTE](msg.payload)
            self._mute = payload
            if MQTTMediaPlayer:
                self.schedule_update_ha_state(False)
           

        if self._topic[MUTE_TOPIC] is not None:
            topics[MUTE_TOPIC] = {
                "topic": self._topic[MUTE_TOPIC],
                "msg_callback": mute_received,
                "qos": self._config[CONF_QOS],
            }

        @callback
        @log_messages(self.hass, self.entity_id)
        def title_received(msg):
            """Handle new received MQTT message."""
            payload = self._templates[SONGTITLE](msg.payload)
            self._track_name = payload
            if MQTTMediaPlayer:
                self.schedule_update_ha_state(False)
           

        if self._topic[SONGTITLE_TOPIC] is not None:
            topics[SONGTITLE_TOPIC] = {
                "topic": self._topic[SONGTITLE_TOPIC],
                "msg_callback": title_received,
                "qos": self._config[CONF_QOS],
            }
        
        @callback
        @log_messages(self.hass, self.entity_id)
        def artist_received(msg):
            """Handle new received MQTT message."""
            payload = self._templates[SONGARTIST](msg.payload)
            self._track_artist = payload
            if MQTTMediaPlayer:
                self.schedule_update_ha_state(False)
           

        if self._topic[SONGARTIST_TOPIC] is not None:
            topics[SONGARTIST_TOPIC] = {
                "topic": self._topic[SONGARTIST_TOPIC],
                "msg_callback": artist_received,
                "qos": self._config[CONF_QOS],
            }
        
        @callback
        @log_messages(self.hass, self.entity_id)
        def album_received(msg):
            """Handle new received MQTT message."""
            payload = self._templates[SONGALBUM](msg.payload)
            self._track_album_name = payload
            if MQTTMediaPlayer:
                self.schedule_update_ha_state(False)
           

        if self._topic[SONGALBUM_TOPIC] is not None:
            topics[SONGALBUM_TOPIC] = {
                "topic": self._topic[SONGALBUM_TOPIC],
                "msg_callback": album_received,
                "qos": self._config[CONF_QOS],
            }

        @callback
        @log_messages(self.hass, self.entity_id)
        def albumart_received(msg):
            """Handle new received MQTT message."""
            payload = self._templates[ALBUMART](msg.payload)
            self._albumart = base64.b64decode(payload.replace("\n", ""))
            if MQTTMediaPlayer:
                self.schedule_update_ha_state(False)
           

        if self._topic[ALBUMART_TOPIC] is not None:
            topics[ALBUMART_TOPIC] = {
                "topic": self._topic[ALBUMART_TOPIC],
                "msg_callback": albumart_received,
                "qos": self._config[CONF_QOS],
            }

        @callback
        @log_messages(self.hass, self.entity_id)
        def albumart_url_received(msg):
            """Handle new received MQTT message."""
            payload = self._templates[ALBUMARTURL](msg.payload)
            self._albumart_url = payload
            if MQTTMediaPlayer:
                self.schedule_update_ha_state(False)
           

        if self._topic[ALBUMARTURL_TOPIC] is not None:
            topics[ALBUMARTURL_TOPIC] = {
                "topic": self._topic[ALBUMARTURL_TOPIC],
                "msg_callback": albumart_url_received,
                "qos": self._config[CONF_QOS],
            }

        @callback
        @log_messages(self.hass, self.entity_id)
        def multiroomclients_received(msg):
            """Handle new received MQTT message."""
            payload = self._templates[MULTIROOMCLIENTS](msg.payload)
            if(isinstance(payload, str)):
                self._multiroom_groupIds = json.loads(payload)
            if(isinstance(payload, list)):
                self._multiroom_groupIds = payload
            self.refresh_group()
           

        if self._topic[MULTIROOMCLIENTS_TOPIC] is not None:
            topics[MULTIROOMCLIENTS_TOPIC] = {
                "topic": self._topic[MULTIROOMCLIENTS_TOPIC],
                "msg_callback": multiroomclients_received,
                "qos": self._config[CONF_QOS],
            }

        @callback
        @log_messages(self.hass, self.entity_id)
        def multiroommaster_received(msg):
            """Handle new received MQTT message."""
            payload = self._templates[MULTIROOM_MASTER](msg.payload)
            if(isinstance(payload, bool)):
                self._isGroupMaster = payload
            elif(isinstance(payload, str)):
                self._isGroupMaster = payload == self._payload["MULTIROOM_MASTER"]
            if MQTTMediaPlayer:
                self.schedule_update_ha_state(False)
           

        if self._topic[MULTIROOM_MASTER_TOPIC] is not None:
            topics[MULTIROOM_MASTER_TOPIC] = {
                "topic": self._topic[MULTIROOM_MASTER_TOPIC],
                "msg_callback": multiroommaster_received,
                "qos": self._config[CONF_QOS],
            }
        
        self._sub_state = await subscription.async_subscribe_topics(
            self.hass, self._sub_state, topics
        )
