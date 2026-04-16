<img width="1280" height="640" alt="visual_4_github_banner-converted-from-svg" src="https://github.com/user-attachments/assets/1035cfb1-d031-469d-9673-7be65d7fb4df" />

# Power BI Bookmark AutoUpdater

> Programmatically update Year and Month filters across all bookmarks and pages in a Power BI Project (PBIP) — without opening Power BI Desktop.

A small Python utility that operates directly on the [PBIR (Power BI Enhanced Report Format)](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-report) JSON files inside a PBIP folder. Built to eliminate the repetitive monthly clicking that comes with bookmark-heavy reports.

---

## Why this exists

If your Power BI report has bookmarks that pin hard-coded `Year` and `Month` filters, every reporting cycle requires opening Desktop, clicking through each bookmark, updating the slicers, and re-capturing the state. With 20+ bookmarks, that's an hour you'll never get back — and a real risk of missing one.

This script does it in seconds, with no clicking, and keeps the page-level default filters in sync with the bookmark filters automatically.

---

## Workflow

1. **Save as PBIP.** In Power BI Desktop, save your `.pbix` as a `.pbip` (Power BI Project). This explodes the report into a folder of JSON files.
2. **Run the script.**
   ```bash
   python bookmark_updater.py "C:\Reports\SalesAnalytics" --year 2026 --month March
   ```
3. **Convert back to PBIX.** Open the generated `_Updated` PBIP in Power BI Desktop, then **File → Save As → `.pbix`**.
4. **Publish.** Push the `.pbix` to your Fabric workspace.

---

## What it does

- Clones the entire PBIP into a `<input>_Updated` folder. The original is never modified.
- Walks every `definition/pages/<section>/page.json` and rewrites the DAX literal for `Year` and `Month` `HierarchyLevel` filters.
- Walks every `definition/bookmarks/*.bookmark.json` and applies the same updates inside `explorationState.sections[<activeSection>].filters.byExpr`.
- Updates the `cachedDisplayNames` so the slicer labels stay in sync with the underlying filter values.
- Uses strict DAX literals (`2026L` for year, `'March'` for month) so Power BI Desktop loads the updated report without dropping filters.

---

## Usage

```bash
# Default: year=2014, month=January
python bookmark_updater.py "path/to/MyReport"

# Specify year and month
python bookmark_updater.py "path/to/MyReport" --year 2026 --month March

# Specify a custom output folder
python bookmark_updater.py "path/to/MyReport" -o "path/to/Output" --year 2026 --month March
```

### Arguments

| Argument | Description | Default |
|---|---|---|
| `input` | Path to the PBIP root folder | required |
| `-o, --output` | Output folder for the updated PBIP | `<input>_Updated` |
| `--year` | Target year (integer) | `2014` |
| `--month` | Target month (string, e.g. `March`) | `January` |

---

## Requirements

- **Python 3.8+**
- No external dependencies (standard library only)
- **Power BI Desktop** for the manual PBIX ↔ PBIP conversion steps

---

## Caveats and gotchas

- **Close Power BI Desktop before running.** Desktop is not aware of changes made by external tools while it's open, and you may lose changes or corrupt files if you ignore this.
- **PBIP must be in PBIR format**, not the legacy `report.json` format. New reports are PBIR by default in the Power BI Service since January 2026; older projects may need to be upgraded.
- Currently handles `Year` and `Month` filters only.
- DAX literals are strict: year values get the `L` suffix (`2026L`), month values get embedded single quotes (`'March'`). The script handles this for you — don't try to bypass it.

---

## Background reading

- [Power BI Desktop projects (PBIP) – Microsoft Learn](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview)
- [Power BI Enhanced Report Format (PBIR) – Microsoft Learn](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-report)
- [PBIR JSON schemas (GitHub)](https://github.com/microsoft/json-schemas)

---

## License

MIT

---

## Author

**Naveen Jujaray** | Microsoft Certified Fabric Analytics Engineer Associate & Power BI Data Analyst Associate

Working daily across Microsoft Fabric, Power BI, Snowflake, and Fabric AI / Copilot. Open to conversations with data leaders, BI managers, and Fabric SMEs building Fabric-first or Snowflake-on-OneLake platforms.

[LinkedIn](https://linkedin.com/in/naveenjujaray) · [GitHub](https://github.com/naveenjujaray) · [Medium](https://medium.com/@naveenjujaray) 
