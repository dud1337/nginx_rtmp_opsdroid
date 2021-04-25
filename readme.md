# nginx\_rtmp\_opsdroid
This bot monitors and submits messages to a chatroom when an nginx-rtmp stream starts, stops, or is ongoing.

This bot gets `exec publish` commands when streams start and stop on an nginx rtmp instance.

## Requirements

### Opsdroid
* `ffmpeg` *see *`Dockerfile` **Not necessary yet. May be if we add the ability to get a frame image from stream**

### nginx RTMP server
* `nginx`
* `libnginx-mod-rtmp`

You'll also need to host a file like: `https://stream.your.server/stream_status` for opsdroid to quickly check if the stream is up. I currently do this with apache which explains why nginx's http host is on a *weird* port in the default config, but it is necessary.

## Config
See `nginx.conf`

For opsdroid `configuration.yaml`:
```yaml
web:
  webhook-token: "<YOUR TOKEN>"
  host: '0.0.0.0'
  disable_web_index_handler_in_root: true
  port: 8080

...

skills:
  nginx_rtmp_opsdroid:
    path: /tmp/skills/nginx_rtmp_opsdroid
    room_notify: "<room id>" # NOTE: For matrix, use internal ID, not alias.
    rtmp_link: "rtmp://rtmp.your.server/live/stream"
    stream_url: "https://stream.your.server"
    stream_status_url: "https://stream.your.server/stream_status"
```

