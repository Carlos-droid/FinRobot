import os
from finrobot.data_source.filings_src.prepline_sec_filings.sec_document import SECDocument
from unstructured.documents.elements import Title, Text

# Since testing a full extraction requires hitting the network and getting a real 10-K,
# We will create a small simulated HTML Document mimicking a 10-K to test our logic!
html_content = """
<html>
<body>
    <p>Some random text</p>
    <h1>TABLE OF CONTENTS</h1>
    <p>Part I</p>
    <p>Item 1. Business</p>
    <p>Item 1A. Risk Factors</p>

    <!-- Cluster of titles that represents the actual content -->
    <h1>PART I</h1>
    <p>This is the business section narrative.</p>
    <h1>Item 1. Business</h1>
    <p>More business text.</p>
    <h1>Item 1A. Risk Factors</h1>
    <p>These are the risk factors. The company may fail.</p>
</body>
</html>
"""

doc = SECDocument.from_string(html_content)
doc.filing_type = "10-K"

toc = doc.get_table_of_contents()
print("Table of Contents Length:", len(toc.elements))
for el in toc.elements:
    print(el.text)

print("\nRisk Narrative Length:", len(doc.get_risk_narrative()))
