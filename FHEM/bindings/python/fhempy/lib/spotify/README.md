
# Spotify
Control your Spotify account via official Spotify Web API. Stream music to any Spotify Connect streaming device in your house or use the googlecast module to stream directly to cast devices.

## Usage
```
define spoti PythonModule spotify
```

Login with your Spotify account and copy the authcode
```
set spoti authcode INSERT_YOUR_VERY_LONG_AUTHCODE
```

Now you can play music on your devices
```
set spoti play https://open.spotify.com/artist/4PBCFEjR4a3OGdOZ6jeKKM
```

## Attributes
 - spotify_connect: You can activate (set to on) official Spotify Connect client to listen to Spotify music directly within FHEM web. You need to stay on the device page to listen to Spotify. Default: off