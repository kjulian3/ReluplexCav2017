#!/bin/bash
# Run mutliple instances of reluPra.py in parallel
# Execute "./runReluPra.sh pra1 pra2 pra3 ..." to run simultaneously 
#    python3 reluPra.py pra1
#    python3 reluPra.py pra2
#    python3 reluPra.py pra3
#    etc.

for cmd in "$@"; do {
  echo "Process \"python3 reluPra.py $cmd\" started";
  python3 reluPra.py $cmd & pid=$!
  PID_LIST+=" $pid";
} done

trap "kill $PID_LIST" SIGINT

echo "Parallel processes have started";

wait $PID_LIST

echo
echo "All processes have completed";
