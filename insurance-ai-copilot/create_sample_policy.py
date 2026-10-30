
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)
from reportlab.lib.styles import getSampleStyleSheet


output = Path("documents/sample_auto_policy.pdf")
output.parent.mkdir(exist_ok=True)

styles = getSampleStyleSheet()

sections = [
    (
        "Sample Auto Insurance Policy",
        "This is a fictional policy created "
        "for software testing only."
    ),
    (
        "Collision Coverage",
        "Collision coverage pays for covered "
        "damage to the insured vehicle caused "
        "by a collision, subject to a $500 "
        "deductible."
    ),
    (
        "Comprehensive Coverage",
        "Comprehensive coverage applies to "
        "covered non-collision losses, "
        "including theft, fire, and hail. "
        "The deductible is $250."
    ),
    (
        "Liability Coverage",
        "Bodily injury liability limits are "
        "$100,000 per person and $300,000 "
        "per accident. Property damage "
        "liability is limited to $50,000 "
        "per accident."
    ),
    (
        "Exclusions",
        "This sample policy excludes "
        "intentional damage and vehicle use "
        "for commercial ridesharing."
    )
]

story = []

for heading, content in sections:
    story.append(
        Paragraph(heading, styles["Heading2"])
    )
    story.append(
        Paragraph(content, styles["BodyText"])
    )
    story.append(Spacer(1, 18))

doc = SimpleDocTemplate(
    str(output),
    pagesize=letter
)

doc.build(story)

print(f"Created: {output}")
