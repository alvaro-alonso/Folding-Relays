# Nova-Relay

a zkRelay using ZoKrates Nova

## Setup

```sh
$ docker run -it -v "$(pwd)":/home/zokrates/trial -v "$(pwd)"/../zokrates_stdlib/stdlib:/home/zokrates/.zokrates/stdlib --platform linux/amd64 zokrates/zokrates:0.8.8
```

## Compile

In the zokrates container run

```sh
$ cd trial
$ zokrates compile -i relay.zok --curve pallas --debug
$ zokrates nova setup
```

## run relay

Once the setup is over, on another terminal on your local machine run the following

```sh
$ cd test
$ python generate_witness.py
```

`generate_witness.py` will create the `init.json` and `steps.json` files which will be automatically available in the container.

To compute the witness, generate and verify the proof go back to the terminal. and run the following commands:

```sh
$ zokrates nova prove
$ zokrates nova compress
$ zokrates nova verify
```