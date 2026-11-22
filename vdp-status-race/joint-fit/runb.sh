#!/bin/sh
# runb.sh BUILD STAGE LABEL MACHINE DISK...: run.sh with the build BUILD
B=$1; shift; BUILD=$B exec /home/manuel/git/openMSX-Claude.git/.claude-data/vdprace/jointfit/run.sh "$@"
