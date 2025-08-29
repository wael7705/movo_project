#!/bin/bash
echo "🚀 Running load test against 10 workers..."
ab -n 200 -c 20 http://localhost:8000/api/v1/orders/counts


