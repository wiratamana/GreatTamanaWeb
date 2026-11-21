# assets/media

Drop screenshots, animated WebP loops and videos here. The file name is the slot name:

    app-chat-main.webp        (or .png / .jpg)     static screenshot
    demo-physics-loop.webp                         animated WebP loop
    pl9-wind-loop.webp                             animated WebP loop (oak stand in the wind, 14 frames, ping-pong)
    pl9-wind-loop-sakura.webp                      animated WebP loop (sakura row in the wind, same method)
    demo-editor-tour.mp4                           demo video

No HTML change is needed. When a slot has no file, the site shows a dashed placeholder. When you add the file, the
placeholder is replaced automatically.

    python tools/list_slots.py     # shows every slot, what to capture, and what is still empty

Rules: no company names, no chat sessions, no user-name paths, no corporate screenshots, no third-party pictures.
Keep images under about 400 KB (WebP, quality 85) and videos under about 15 MB (H.264 MP4, 1080p or 720p).
Animated loops: under about 2 MB, 6 to 10 fps, 960 px wide.
