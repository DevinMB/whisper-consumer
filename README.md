# whisper-commentator
ML application to produce popular whispers in a group chat. 
This portion takes in Telegram messages and pushing everything to a kafka topic. 

## Build and deploy

`docker build .` makes the image (pinned dependencies, tests in `tests/`). CI (`.github/workflows/ci.yml`, the shared `DevinMB/workflows` pipeline) runs the tests inside the image and a Trivy scan, and pushes `ghcr.io/devinmb/whisper-consumer:sha-<commit>` from `main`. Configuration from the environment: `BROKER`, `TOPIC_NAME`, `BOT_TOKEN`. The container reports healthy while it is connected to Kafka. Dependabot keeps pip, the base image and the actions current; patch and minor updates merge on green.
