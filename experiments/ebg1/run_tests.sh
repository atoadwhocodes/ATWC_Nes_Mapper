#!/bin/sh
set -eu
cd "$(dirname "$0")"
c++ -std=c++17 -Wall -Wextra -I tests/stubs -I mapper tests/engine_test.cpp -o legacy_test
./legacy_test
c++ -std=c++17 -Wall -Wextra -I tests/stubs -I mapper tests/extended_test.cpp -o extended_test
./extended_test
