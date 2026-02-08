#!/bin/sh

# Preprocess revealshapes.cpp exactly like the real build,
# but stop after preprocessing.

g++ \
  -DHAVE_CONFIG_H \
  -I. \
  -Ilibdjvu \
  -Iexternal \
  -pthread \
  -std=c++2a \
  -g \
  -Wno-non-virtual-dtor \
  -Wall \
  -E -P \
  revealshapes.cpp > revealshapes.i
