#!/bin/sh

pkill socat
socat -d -d pty,raw,echo=0 pty,raw,echo=0  &
sleep 2
socat -d -d pty,raw,echo=0 pty,raw,echo=0  &
