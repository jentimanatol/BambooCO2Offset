git --version
git add .
git commit -m "'Add gdp_per_country '"
git push origin main

:: === Tagging for GitHub Actions Release Build ===
git tag v1.6
git push origin v1.6
pause
