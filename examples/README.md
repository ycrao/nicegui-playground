examples
--------

>   Official examples from [NiceGUI](https://github.com/zauberzeug/nicegui/tree/main/examples) .


### ffmpeg_extract_images

```bash
# need ffmpeg 
# install On Ubuntu
sudo apt install ffmpeg
cd ffmpeg_extract_images
uv run main.py
```

### generate_pdf

```bash
# need cairo deps
sudo apt update && sudo apt install pkg-config cmake libcairo2-dev
uv add html-sanitizer pycairo
cd generate_pdf
uv run main.py
```

### node_module_integration

```bash
# need install node
# I am using nvm
cd node_module_integration
# install deps using npm
npm install
# or pnpm
pnpm i
pnpm build
```

### pandas_dataframe

```bash
# need pandas
uv add pandas
cd pandas_dataframe
uv run main.py
```

### simpy

```bash
uv add simpy
cd simpy
uv run main.py
```

### sqlite_database

```bash
uv add tortoise-orm
cd sqlite_database
uv run main.py
```

### websockets

```bash
uv add websockets
cd websockets
uv run main.py
```

### zeromq

```bash
uv add pyzmq matplotlib
cd zeromq
# in terminal #1
uv run zmq-server.py 
# in terminal #2
uv run main.py
```