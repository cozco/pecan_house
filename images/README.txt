This folder contains public web assets copied or exported from the shared renovation design folder.
Only optimized/metadata-stripped copies should be committed here.

Suggested final photo filenames:
  exterior-hero.jpg     1600+ px wide, landscape — used in the hero background
  royal-room.jpg        4:3 ratio works best
  red-room.jpg
  bay-room.jpg
  guest-room.jpg
  twin-room.jpg
  walnut-room.jpg
  garage-apt.jpg

Once final photos are in place:
  1. In styles.css, replace the .hero-media background image URL with the exterior photo.
  2. In styles.css, find the .room-photo[data-room=...] block and replace each rendering
     with: background-image: url('images/<filename>.jpg');

Optimization tips:
  - Export at 1600px wide max for hero, 1200px wide for room cards.
  - Run through https://squoosh.app or `cwebp` to compress before committing.
  - Keep each image under ~250 KB if possible.
