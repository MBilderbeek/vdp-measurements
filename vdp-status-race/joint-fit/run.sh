#!/bin/sh
# run.sh STAGE LABEL MACHINE DISK [VAR=value...]: runs the disk's autoexec in the
# scratch build (env overrides FB FA FHB FHA OD LD LO RL), into out/STAGE/LABEL/MACHINE-DISK
J=/home/manuel/git/openMSX-Claude.git/.claude-data/vdprace/jointfit
st=$1; lb=$2; m=$3; k=$4; shift 4
kb=${k%%-d*}; d=$J/out/$st/$lb/$m-$kb; [ -d $d ] && exit 0; mkdir -p $d; cp $J/disks/$k/* $d/
script=$J/run.tcl; case $k in irq*) script=$J/done.tcl;; hint*) script=$J/hint.tcl;; r23*) script=$J/r23.tcl;; fh*) script=$J/fh.tcl;; esac
U=""; case " $* " in *" UNSETFH=1 "*) U="-u FHB -u FHA";; esac
cd $d && env OD=30 LD=22 LO=173 RL=26 FB=7 FA=15 FHB=15 FHA=10 "$@" DONE="All done." SHOT=$d/shot OUT=$d \
  WT=/home/manuel/git/openMSX-Claude.git/.worktrees/${BUILD:-od-scan} timeout 14400 \
  env $U /home/manuel/git/openMSX-Claude.git/.claude-data/vdprace/openmsx-bin.sh -machine $m -diska . -script $script > $d.log 2>&1
