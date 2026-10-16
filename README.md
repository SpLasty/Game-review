# Steam review project

The proposal is in `proposal/Research_Proposal_Revamped.docx`. The code is in `scripts/`. All data is in `data/`.

Open these three CSV files in `data/processed/steam_30_games/`:

- `all_english_reviews.csv` has all 73,336 collected English reviews.
- `balanced_reviews.csv` has 30,000 reviews, with 1,000 per game and at least 10 words per review. This is the main review dataset for the project.
- `developer_announcements.csv` has 3,445 developer posts.

The collection began on October 14, 2026. That is the download date, not the date of every review. A review's `created_utc` value is when it was posted. Its `updated_utc` value is its latest recorded edit. The collected reviews range from January 14 to October 14, 2026. About 77% were posted in September or October because Steam returned recent reviews first and collection stopped after each game met its target.

`data/raw/steam_30_games/` contains the downloaded source records and saved progress used to resume collection. Its game folders show the game name and Steam ID. These local source files are excluded from Git; the three processed CSV files above are included.

The two JSON files in the processed folder are small summaries. `analysis.json` stores collection totals and analysis counts. `balanced_manifest.json` records how the balanced set was selected. They are not extra spreadsheets.

Run `scripts/run_collection.ps1` from this folder to collect and prepare the three CSV files. If collection stops or Steam returns HTTP 429, run it again to resume.
