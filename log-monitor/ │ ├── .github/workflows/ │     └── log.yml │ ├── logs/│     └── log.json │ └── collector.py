name: LOG-COLLECTOR

on:
  schedule:
    - cron: "*/10 * * * *"   # 每10分钟记录一次
  workflow_dispatch:

jobs:
  log:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Create log entry
        run: |
          mkdir -p logs

          echo "{
            \"time\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",
            \"status\": \"running\",
            \"note\": \"collector alive\"
          }" >> logs/log.json

      - name: Commit logs
        run: |
          git config user.name "log-bot"
          git config user.email "log@bot.com"

          git add logs/log.json
          git commit -m "log update $(date -u)" || echo "no changes"
          git push
