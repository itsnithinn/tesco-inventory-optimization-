# Publish to GitHub Pages

Publication was not performed: no authenticated GitHub connection was available. The account's existing public portfolio source was cloned read-only at commit 9e011a535a802fd17400f8cec75f50652c6d2343.

## Project repository
1. Create a public GitHub repository named `tesco-inventory-optimization` under `itsnithinn`, without an initial README.
2. Extract this package and run from the project directory:

```sh
git init -b main
git add .
git commit -m "Add reproducible synthetic inventory analytics project"
git remote add origin https://github.com/itsnithinn/tesco-inventory-optimization.git
git push -u origin main
```

3. In repository Settings → Pages, select GitHub Actions as the source. Run “Deploy static dashboard” in Actions if needed.
4. Verify the dashboard at `https://itsnithinn.github.io/tesco-inventory-optimization/` and case study at `/case-study.html`. Check the source link and filters at desktop and mobile widths. These are intended URLs, not verified live links yet.

## Existing portfolio
The delivery includes `portfolio-update.patch` against the inspected commit and an `integration/` folder containing the updated index.html and the new `projects/tesco/` files. It replaces only the Tesco placeholder card, preserving other content.

Preferred method from a fresh clone of the portfolio:

```sh
git apply --check /path/to/portfolio-update.patch
git apply /path/to/portfolio-update.patch
git add index.html projects/tesco
git commit -m "Replace Tesco placeholder with validated synthetic inventory case study"
git push
```

If the check fails because the portfolio changed, merge the Tesco card change manually rather than overwriting newer work. Alternatively copy the integration folder contents into an unchanged checkout. The card includes relative dashboard and case-study links, so those work within the portfolio itself; its repository link requires the project repository to exist.

The existing portfolio has two sections with id="projects" and other unrelated placeholder links. These were preserved. No source-level Pages configuration was present; confirm the portfolio's existing Pages branch/settings remain active.

After publishing, verify portfolio links at `https://itsnithinn.github.io/portfolio/`, `/portfolio/projects/tesco/index.html` and `/portfolio/projects/tesco/case-study.html`. Update README publication status only after successful verification.
