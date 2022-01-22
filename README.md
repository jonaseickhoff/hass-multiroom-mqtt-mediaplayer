# Multiroom and Roon MQTT Media Player

MQTT MediaPlayer with multiroom and Roon support for [Home Assistant](https://www.home-assistant.io).

This MQTT MediaPlayer has initially been built to interface with the [musiccast2mqtt](https://github.com/jonaseickhoff/musiccast2mqtt) bridge in Home Assistant. It's possible to subscribe to different topics and use specific templates per topic.


It works perfectly with [Mini Media Player](https://github.com/kalkih/mini-media-player) and [Roon MQTT extension](https://github.com/nseibert/roon-extension-mqtt)

## Installation

### Install with [HACS](https://github.com/custom-components/hacs)

Go to the HACS store and use the repo url https://github.com/nseibert/hass-multiroom-mqtt-mediaplayer and add this as a custom repository under settings.

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

### Roon

#### Zones and outputs

Roon manages zones and outputs per zone. In many configurations there will be just one outpost per zone. In this example "living room" is the zone and "streamer" is the output.

	roon/[zone]/...
	roon/[zone]/outputs/[output]/...

#### IP address and port

Currently there is no way to retrieve ip and port from the Roon API. Therefore it is necessary to look them up in the Roon UI (settings > web) and set them in _albumart_url_template_.

#### Play media

The following Roon hierarchies are supported for _content_type_ and the first search result is used:

- playlists
- internet_radio
- albums
- artists
- genres
- composers

#### Example configuration

The following configuration fits for use with the [Roon MQTT extension](https://github.com/fjgalesloot/roon-extension-mqtt).

```
- platform: multiroom-mqtt-mediaplayer
  name: "Streamer in living room"
  unique_id: 78dfe64fdc7c4474b95552b4ffa83f90
  multiroom_id: "Roon"
  power_topic: "roon/living room/outputs/streamer/source_controls/0/status"
  player_status_topic: "roon/living room/state"
  volume_topic: "roon/living room/outputs/streamer/volume/value"
  minvolume_topic: "roon/living room/outputs/streamer/volume/min"
  maxvolume_topic: "roon/living room/outputs/streamer/volume/max"
  mute_topic: "roon/living room/outputs/streamer/volume/is_muted"
  media_title_topic: "roon/living room/now_playing/three_line/line1"
  media_artist_topic: "roon/living room/now_playing/three_line/line2"
  media_album_topic: "roon/living room/now_playing/three_line/line3"
  media_position_topic: "roon/living room/seek_position"
  media_duration_topic: "roon/living room/now_playing/length"
  albumart_url_topic: "roon/living room/now_playing/image_key"
  albumart_url_template: "http://192.168.1.65:9330/api/image/{{value}}?&width=400&height=400"
  payload_playingstatus: "playing"
  payload_poweroff: "standby"
  shuffle_topic: "roon/living room/settings/shuffle"
  repeat_topic: "roon/living room/settings/loop"
  volume:
    service: mqtt.publish
    data:
      topic: "roon/living room/outputs/streamer/volume/set"
      payload: "{{volume}}"
  vol_mute:
    service: mqtt.publish
    data:
      topic: "roon/living room/outputs/streamer/volume/set"
      payload: "mute"
  vol_unmute:
    service: mqtt.publish
    data:
      topic: "roon/living room/outputs/streamer/volume/set"
      payload: "unmute"
  power_on:
    service: mqtt.publish
    data:
      topic: "roon/living room/outputs/streamer/power"
      payload: "on"
  power_off:
    service: mqtt.publish
    data:
      topic: "roon/living room/outputs/streamer/power"
      payload: "standby"
  next:
    service: mqtt.publish
    data:
      topic: "roon/living room/command"
      payload: "next"
  previous:
    service: mqtt.publish
    data:
      topic: "roon/living room/command"
      payload: "previous"
  play:
    service: mqtt.publish
    data:
      topic: "roon/living room/command"
      payload: "play"
  stop:
    service: mqtt.publish
    data:
      topic: "roon/living room/command"
      payload: "stop"
  pause:
    service: mqtt.publish
    data:
      topic: "roon/living room/command"
      payload: "pause"
  play_media:
    service: mqtt.publish
    data:
      topic: "roon/living room/browse/{{content_type}}"
      payload: "{{content_id}}"
  seek:
    service: mqtt.publish
    data:
      topic: "roon/living room/seek/set"
      payload: "{{position}}"
  shuffle:
    service: mqtt.publish
    data:
      topic: "roon/living room/settings/set/shuffle"
      payload: "{{shuffle}}"
  repeat:
    service: mqtt.publish
    data:
      topic: "roon/living room/settings/set/repeat"
      payload: "{{repeat}}"
```

