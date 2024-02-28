# Nova-Relay

a zkRelay using ZoKrates Nova

## Setup

```sh
$ docker run -it -v "$(pwd)":/home/zokrates/trial -v "$(pwd)"/../zokrates_stdlib/stdlib:/home/zokrates/.zokrates/stdlib --platform linux/amd64 zokrates/zokrates:0.8.8
```

## Compile

```sh
$ cd trial
$ zokrates compile -i relay.zok --curve pallas --debug
```