# Lantern story demo audio

`lantern-demo.mp3` is local synthetic English narration of the project's original fictional fixture. It is not live TTS, a practitioner recording or cultural evidence. Chinese captions are available in the story component; Chinese audio is not supplied. Duration and playback position come from the actual audio element.

Original transcript:

> A lantern drifts beyond the screen. In this fictional tale, you may follow its light toward the mountain, or take the bridge across the river. Which path will you choose?

Generated locally with eSpeak at 145 words per minute, then encoded by FFmpeg. Optional regeneration from the repository root on a machine with those tools installed:

```sh
espeak -s 145 -w /tmp/folkverse-lantern.wav 'A lantern drifts beyond the screen. In this fictional tale, you may follow its light toward the mountain, or take the bridge across the river. Which path will you choose?'
ffmpeg -y -i /tmp/folkverse-lantern.wav apps/web/public/folkverse/audio/lantern-demo.mp3
```

The shipped MP3 needs no speech service or generator installed at runtime.
