# enraibler

For headless operation, you'll need to build jackd2 from source without DBUS support. Instructions adapted from http://capocasa.net/jackd-headless --

```
# Prerequisites
sudo -s
apt-get install build-essential libsamplerate-dev libasound-dev libsndfile-dev git

# Get source
cd /usr/local/src
git clone git://github.com/jackaudio/jack2.git
cd jack2

./waf configure --alsa --prefix=/usr/local --libdir=/usr/lib/arm-linux-gnueabihf
./waf
./waf install
```

> You can still install the normal jackd package to satisfy dependencies. If you run jackd from the command line, it will take precedence because it is in /usr/local/bin. Just make sure to run /usr/local/bin/jackd in startup scripts and other places where you need to provide the full path.
