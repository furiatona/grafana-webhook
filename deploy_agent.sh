#!/bin/bash

cat > /usr/local/bin/top5_process.sh << 'EOF'
#!/bin/bash

OUTPUT_FILE="/var/lib/node_exporter/textfile_collector/top_processes.prom"
TEMP_FILE="/tmp/top_processes.prom.$$"

{
  echo "# HELP top_processes Top 5 CPU-consuming processes on the server"
  echo "# TYPE top_processes gauge"

  declare -A cpu_sums
  while read -r user cpu command; do
    key="$user|$command"
    cpu_sums["$key"]=$(echo "${cpu_sums[$key]:-0} + $cpu" | bc)
  done < <(ps -eo user,%cpu,comm --sort=-%cpu | tail -n +2)

  for key in "${!cpu_sums[@]}"; do
    user=${key%%|*}
    command=${key#*|}
    command="${command//\"/\\\"}"
    echo "top_processes{user=\"$user\",command=\"$command\"} ${cpu_sums[$key]}"
  done | sort -k2 -nr | head -n 5
} > "$TEMP_FILE"

mv "$TEMP_FILE" "$OUTPUT_FILE"
chown prometheus:prometheus "$OUTPUT_FILE" 2>/dev/null || true
chmod 644 "$OUTPUT_FILE"
EOF

chmod +x /usr/local/bin/top5_process.sh

cat > /etc/systemd/system/top5_process.service << 'EOF'
[Unit]
Description=Collect top 5 CPU-intensive processes for Prometheus
After=network.target

[Service]
ExecStart=/bin/bash -c 'while true; do /usr/local/bin/top5_process.sh; sleep 15; done'
Restart=always
User=root

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now top5_process.service
systemctl restart top5_process.service
systemctl restart node_exporter

echo "Service status:"
systemctl status top5_process.service | head -n 3
echo "Generated metrics:"
cat /var/lib/node_exporter/textfile_collector/top_processes.prom | grep -v '^#' || echo "No data yet"

echo "Deployment complete on this server!"