git --version
git add .
git commit -m "'Add gdp_per_country '"
git push origin main

:: === Tagging for GitHub Actions Release Build ===
git tag v1.2
git push origin v1.2
pause
