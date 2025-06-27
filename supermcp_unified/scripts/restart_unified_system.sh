#!/bin/bash
echo "🔄 RESTARTING SUPERMCP UNIFIED SYSTEM"
echo "===================================="

./supermcp_unified/scripts/stop_unified_system.sh
sleep 5
./supermcp_unified/scripts/start_unified_system.sh
