# ignition
writes files and systemd units specified in the ignition to disk.

# Build
```docker build -t eranco/extract:latest  -f Dockerfile.ignition-extract .```
# Usage
```podman run -v /:/host --privileged=true -it eranco/extract /host/var/home/core/bootstrap.ign ```
