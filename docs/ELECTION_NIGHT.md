# Election night checklist (Knesset 27)

The tool is the calculator at the bottom of `reports/knesset_27_panels.html` (also the
private claude.ai link in `HANDOFF.md`). It runs offline in the browser; nothing is sent
anywhere.

## Before election day

1. **Polling station list (D17).** When the committee publishes the K27 list of ballot
   boxes, link it and redraw the panels:
   ```bash
   PYTHONPATH=src python scripts/match_k27_boxes.py <k27_list.csv>
   PYTHONPATH=src python scripts/recommend_sector_panels.py
   PYTHONPATH=src python scripts/build_panels_site.py --fragment <scratchpad>/knesset_27_panels.html
   PYTHONPATH=src python scripts/check_panels_site.py <screenshot_dir>
   ```
   Republish the page. The panel areas then carry their K27 box numbers.
2. **Choose the panel.** Recommended: budget 2%, alternative A (about 217 boxes). Write down
   which one; the calculator works on the panel selected in the comparison table.
3. **Lists.** When the final ballot letters are known, open "רשימות, גושים והסכמי עודפים"
   in the calculator: one row per list with its letters, name, bloc and the K26 list it
   continues (or "רשימה חדשה"); keep "אחרות" for lists under 1%. Enter the surplus
   agreements once they are signed.
4. **Dry run.** Load the K26 per-box file (`data/raw/knesset_26_2026_ballots.csv`) in parts,
   as below; or run `node scripts/rehearse_election_night.js` (results in
   `reports/election_night_rehearsal.json`).

## On the night

5. **Load the results.** Each time the committee publishes or updates its per-box results
   file (CSV with `סמל ישוב`, `קלפי`, `כשרים` and a column per ballot letter; UTF-8 or
   Windows-1255), press "טעינת קובץ התוצאות של ועדת הבחירות" and pick it. Several files can
   be loaded, at once or one after the other: their boxes add up, and a box that appears
   again takes the later count. "ניקוי הקבצים שנטענו" starts over. If a panel box is not
   in the files, its two backup boxes in the same area are used.
6. **Check what was counted.** The table "שיעור ההצבעה לפי מגזר" shows the areas counted out
   of planned per sector.
   - A red warning: a whole sector has no counted area. Its result is taken from K26, and
     the forecast is not reliable. In the backtest, with no Arab-sector area counted the
     error was 10 seats on average (up to 14). Wait for that sector.
   - A gray note: a sector has fewer than half of its areas. Intervals are wider.
   - With every sector represented, the held-out error of a random part of the 2% panel
     is: 90% of the boxes 2.5 seats, 70% 2.9, 50% 3.4 (all of it 2.2;
     `reports/sector_partial.md`, `reports/sector_model.md`).
7. **Read the forecast.**
   - Seats per list (the medoid of 200 resamples of the panel) with a 90% range; a list in
     orange has between 5% and 95% to pass the threshold, so its seats are uncertain.
   - "סיכוי ל-61" for every bloc and for right + Haredi and center-left + Arab; the coalition
     builder gives the same for any set of lists.
   - The shares are the direct estimate; the seats can differ slightly near the threshold.
8. **New lists.** If a file has a list of 1% or more that is not in the lists table, the
   calculator adds it with an empty name and bloc "אחר": set its name, bloc and source list
   and press "חישוב תחזית" again.

## Rehearsal (2026-11-01, K26 file, default 2% panel)

Four cumulative files of 25% of the panel boxes each. The forecast is compared with the
final (100%) one; the K26 file is the model's own base, so this checks the procedure, not
the accuracy.

| Order | 25% | 50% | 75% | 100% |
|---|---|---|---|---|
| Random | 1 seat from final; gray note for one sector | 0; gray note | 0 | final, no warnings |
| Arab-majority sectors last | 1; red warning (Joint List sector), gray note | 1; red, gray | 0; red | final, no warnings |

All 217 areas were found; no script errors.
