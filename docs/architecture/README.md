# Steam Patch Intelligence architecture

Open [the architecture PDF](steam_patch_intelligence_architecture.pdf).

The design is grounded in the current project proposal, collector, tests and CSV exports. It covers product scope, inspection of the existing data, current Steam API contracts, architecture, model candidates, evaluation, the three delivery phases, DVC/MLflow responsibilities, CI/CD, deployment, operations, and decision rationales. Proposed metrics and SLOs are targets, not measured results.

The application and its data were not modified. The existing test run is recorded with its actual failures; the design identifies the invalid collector snapshot default as the first implementation prerequisite.

## Editable artifacts

- `steam_patch_intelligence_architecture.tex`: document source.
- `figures/*.svg`: editable vector diagrams; matching PDFs are embedded in the report.
- `figures/specs/*.json`: structured diagram definitions.
- `render_figures.py`: local deterministic diagram renderer. The installed FigureSpec skill supplied the specification approach, but its renderer was absent, so this package includes a small matplotlib fallback. No external model or image service is used.
- `evidence/repository_audit.json`: independently recomputed CSV counts, schema, dates, and SHA-256 hashes.
- `evidence/existing_tests.txt`: current run of `python -m unittest discover -s tests -v` from the project root; 15 tests, 5 errors.

## Rebuild

Run `python docs/architecture/build_pdf.py` from the project root. Requires Python with matplotlib and a local `pdflatex` installation with the packages named in the TeX preamble. Build intermediates are placed in `build/`; the final PDF is copied beside the source. Hyperlinks and the table of contents are embedded in the PDF.

No paid services are provisioned by rebuilding this document.
