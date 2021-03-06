# hass-multiroom-mqtt-mediaplayer
MQTT MediaPlayer with Multiroom support for Homeassistant.

I build this MQTT MediaPlayer because i was looking for an integration for my [musiccast2mqtt](https://github.com/jonaseickhoff/musiccast2mqtt) bridge in homeassistant. 
This MQTT MediaPlayer is able to subscribe to different topics and for every topic there also can be configured a template.


It works perfectly with [Mini Media Player](https://github.com/kalkih/mini-media-player)

## Installation

### Install with [HACS](https://github.com/custom-components/hacs)

Go to the hacs store and use the repo url https://github.com/jonaseickhoff/hass-multiroom-mqtt-mediaplayer and add this as a custom repository under settings.

### Manual

Copy all files from custom_components/multiroom-mqtt-mediaplayer/ to custom_components/multiroom-mqtt-mediaplayer/ inside your config Home Assistant directory.

## Configuration

### Example Configuration

```
- platform: multiroom-mqtt-mediaplayer
  name: "kitchen MC"
  unique_id: d2f97fe6-35fd-4053-b9a0-23cca0ef7d8e
  multiroom_id: "kitchen"
  power_topic: "musiccast_test/status/kitchen/power"
  player_status_topic: "musiccast_test/status/kitchen/player/playback"
  source_topic: "musiccast_test/status/kitchen/input"
  sourcelist_topic: "musiccast_test/status/kitchen/features/input"
  volume_topic: "musiccast_test/status/kitchen/volume"
  mute_topic: "musiccast_test/status/kitchen/mute"
  media_title_topic: "musiccast_test/status/kitchen/player/title"
  media_artist_topic: "musiccast_test/status/kitchen/player/artist"
  media_album_topic: "musiccast_test/status/kitchen/player/album"
  media_position_topic: "musiccast_test/status/kitchen/player/playtime"
  media_duration_topic: "musiccast_test/status/kitchen/player/totaltime"
  albumart_url_topic: "musiccast_test/status/kitchen/player/albumarturl"
  multiroom_clients_topic: "musiccast_test/status/kitchen/link/clients"
  multiroom_master_topic: "musiccast_test/status/kitchen/link/role"
  payload_multiroom_master: "server"
  payload_playingstatus: "play"
  payload_poweroff: "standby"
  volume:
    service: mqtt.publish
    data:
      topic: "musiccast_test/set/kitchen/volume"
      payload: "{{volume}}"
  vol_mute:
    service: mqtt.publish
    data:
      topic: "musiccast_test/set/kitchen/mute"
      payload: "true"
  vol_unmute:
    service: mqtt.publish
    data:
      topic: "musiccast_test/set/kitchen/unmute"
      payload: "false"
  power_on:
    service: mqtt.publish
    data:
      topic: "musiccast_test/set/kitchen/power"
      payload: "on"
  power_off:
    service: mqtt.publish
    data:
      topic: "musiccast_test/set/kitchen/power"
      payload: "standby"
  next:
    service: mqtt.publish
    data:
      topic: "musiccast_test/set/kitchen/next"
  previous:
    service: mqtt.publish
    data:
      topic: "musiccast_test/set/kitchen/previous"
  play:
    service: mqtt.publish
    data:
      topic: "musiccast_test/set/kitchen/play"
  stop:
    service: mqtt.publish
    data:
      topic: "musiccast_test/set/kitchen/stop"
  pause:
    service: mqtt.publish
    data:
      topic: "musiccast_test/set/kitchen/pause"
  select_source:
    service: mqtt.publish
    data:
      topic: "musiccast_test/set/kitchen/input"
      payload: "{{source}}"
  join:
    service: mqtt.publish
    data:
      topic: "musiccast_test/set/kitchen/addclients"
      payload: "{{ client_ids|join(', ') }}"
  unjoin:
    service: mqtt.publish
    data:
      topic: "musiccast_test/set/kitchen/leavegroup"
      payload: ""
```


