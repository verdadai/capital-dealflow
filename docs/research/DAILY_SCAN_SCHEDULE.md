# Daily EDGAR scan schedule

## Cadence
- **Time:** 6:30 PM America/New_York (EDT/EST handled automatically)
- **Script:** `scripts/daily_edgar_scan.sh`
- **Scheduler:** `scripts/schedule_daily_scan.sh` (loop; used when system cron is unavailable)

## What it does
1. Runs `python -m src.edgar_watcher --mining-stages` with a short lookback (default 3 days)
2. Writes raw signals to `data/signals.json`
3. Writes curated CSV to:
   - `docs/leads/edgar_daily_latest.csv`
   - `docs/leads/edgar_daily_YYYY-MM-DD.csv`
4. Logs to `data/logs/`

## Manual run
```bash
cd capital-dealflow
LOOKBACK_DAYS=14 ./scripts/daily_edgar_scan.sh
```

## Start / check scheduler (this environment)
```bash
# start
tmux -f /exec-daemon/tmux.portal.conf new-session -d -s edgar-daily-630pm -c "$PWD" -- bash -lc './scripts/schedule_daily_scan.sh'

# inspect
tmux -f /exec-daemon/tmux.portal.conf capture-pane -t edgar-daily-630pm:0.0 -p | tail -30
```

## Notes
- SEC EDGAR full-text can return intermittent HTTP 500s; the watcher continues other queries.
- Many junior miners file on SEDAR+ (Canada); EDGAR alone under-samples them.
- Cloud/agent VMs may reset; if the tmux session dies, restart with the commands above.

## Freeze resilience
The scheduler checks the clock every 60 seconds (not one long sleep), so if the VM freezes past 18:30 it still runs once after waking, once per local day.
