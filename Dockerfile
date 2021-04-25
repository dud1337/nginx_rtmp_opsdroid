FROM opsdroid/opsdroid:latest

RUN apk update && apt add --no-cache ffmpeg
