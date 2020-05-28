# mab0l 2.0 - chrome edition

Mappool zip and collections.db maker for osu! tournaments

[My earlier script for this](https://gist.github.com/goeo-/76977d412b17f669449f62d1a72642b5) no longer works
because of peppy enabling Cloudflare's browser checking feature and also implementing some anti-automation measures
himself.

Using an actual browser, I'm able to bypass all of this as long as he doesn't start doing captchas (which we could
account for by having the user do them, would make the process take more time though.)

## Usage

mab0l depends on a bunch of things, sadly. First, install python requirements by running

```
python -m pip install -r requirements.txt
```

Then, install [Chrome](https://www.google.com/chrome/) (probably, chromium also works) and [ChromeDriver](https://chromedriver.chromium.org/). If 
they're not installed in the default locations (or if ChromeDriver isn't in the `PATH` environment variable, edit the
variables `chrome_driver_path` and `chrome_path` in mab0l.py)

Edit the variables `to_download`, `tourney_acronym`, `osu_username`, `osu_password` to your values. You can also 
comment out the line `options.headless = True` if you want to see it work!

Start mab0l by running

```
python mab0l.py
```

Note: mab0l will remove all .osz files in the working directory when it starts, and will put all .osz in the working
directory in the zip and the collections.db when it's done. Therefore it is advised to run it in its own directory.