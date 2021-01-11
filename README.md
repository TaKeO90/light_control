# LIGHT SERVER API


## TODO :
- [X] add timer to turn on or off the light
- [X] add schedule for turning on or off the light
- [ ] ...

## RUN AS A SERVICE
- edit this file down bellow.

```console
$ sudo vim /lib/systemd/system/lightserver.service
```
- Add this content on it :
```
[Unit]

Description="Light Server for controling my room light"
After=multi-user.target


[Service]

Type=idle
ExecStart=/bin/bash -c "~/lightwebserver/run.sh"

[Install]

WantedBy=multi-user.target
```

```console
$ sudo chmod 644 /lib/systemd/system/ligtserver.service
$ sudo systemctl daemon-reload
$ sudo systemctl enable lightserver.service
$ sudo reboot
$ sudo systemctl status lightserver.service
```
