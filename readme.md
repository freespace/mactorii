Usage
=====

For now it must be ran from command line:
./mactorii.app/Contents/MacOS/mactorii /path/to/some/place/*.jpg

It is still a bit slow, so start with a small image collection. mactorii 
supports whaever PIL supports, so you don't have to use *.jpg

Operation
=========

Clicking on an image will sort all images loaded based on their 
similarity to the selected image. The selected image is displayed as the
top-left image. Images are drawn down then across, so the closest match 
would be directly below the top-left image.

Hovering over an image will show you its size. While hovering over an
image you can press the following keys:

- `d`					deletes the image you are hovering over. By "delete" 
					it moves the image into .mactorii-trash, so nothing 
					is /actually/ deleted. In full-view mode this also
					deletes the picture, and drops you back into 
					thumbnail mode.
					
- `u`					undeletes the last image. There is no hard limit on 
					the undo queue.

You can press the following keys at anytime:

- `left/right`			in thumbnail view, scrolls left/right.
	- `+shift`		in thumbnail view, scrolls 2x as fast.

- `f`					displays fps.
- `c`					attempts to cluster similar images.
- `v`					displays the picture you are hovering over in full
					window view. Pressing this key while in full-view
					will drop you back into thumbnail view.
