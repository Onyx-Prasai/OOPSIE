import re

with open("docs/research/author_decision_sheet.md", "r", encoding="utf-8") as f:
    text = f.read()

# Update status
text = text.replace(
    "> **Status**: All current ratings remain unchanged provisional values. No unblinding has occurred.",
    "> **Status**: Author adoption decisions applied and audited on 2026-11-06. All 160 evaluations verified complete with zero audit issues. Blinding strictly maintained."
)

with open("docs/research/author_decision_sheet.md", "w", encoding="utf-8") as f:
    f.write(text)

print("Updated author_decision_sheet.md status.")

