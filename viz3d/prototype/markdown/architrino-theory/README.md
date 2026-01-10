
The viz3d app is deployed via GitHub pages. 

To do so, the 'docs' directory contains an entire copy of this markdown directory.

Periodically the 'docs' directory should be refreshed.

# dry-run

rsync -av --delete --dry-run \
  /Users/markmorris/vibe/neoclassical.ai/viz3d/prototype/markdown/ \
  /Users/markmorris/vibe/neoclassical.ai/docs/markdown/


# refresh

rsync -av --delete \
  /Users/markmorris/vibe/neoclassical.ai/viz3d/prototype/markdown/ \
  /Users/markmorris/vibe/neoclassical.ai/docs/markdown/
