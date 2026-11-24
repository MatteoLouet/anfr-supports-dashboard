# BDML Individual Project: Data Visualization, Data Storytelling & Business Intelligence

## Project Overview

Design and build an interactive Data Visualization and Business Intelligence web application using **Streamlit**.

Your application must use a real public dataset, clean and analyze the data, define relevant Key Performance Indicators (KPIs), and present an interactive dashboard that guides the user through a clear decision-oriented narrative:

**Problem → Data → KPIs → Analysis → Insights → Business/Policy Implications → Recommendations**

The objective is not simply to produce charts. Your dashboard should transform raw data into actionable information that can support decisions.

Your project should combine two complementary dimensions:

### Data Storytelling
Each visualization, metric, filter and interaction should contribute to a coherent story and answer a specific analytical question.

### Business Intelligence
Your application should allow a decision-maker to:

- monitor important KPIs;
- compare performance between locations, periods, categories or entities;
- identify trends, patterns and anomalies;
- explore data through filters and drill-downs;
- benchmark entities or territories;
- identify areas requiring attention;
- obtain evidence-based recommendations.

The final application should resemble a simplified BI decision-support dashboard, rather than only an exploratory data-analysis notebook converted to Streamlit.

## Approved Data Portals

Choose one dataset or a small, coherent combination of datasets from one of the following sources:

- French Open Data: [data.gouv.fr](https://www.data.gouv.fr/datasets)
- Environmental & Health Data: [Green Data for Health](https://gd4h.ecologie.gouv.fr/en/catalogue)
- European Open Data: [European Data Portal](https://data.europa.eu/data/combined?locale=en)

Tip: Prefer datasets with:

- reasonable size;
- a clearly identifiable business, societal or policy question;
- meaningful time and/or geographical dimensions;
- numerical or categorical measures that can become KPIs;
- sufficient information to compare entities or periods.

Possible domains include: Business | Housing | Transport | Energy | Tourism | Environment | Health | Air Quality | Water | Mobility | Territory | Public Services | Climate

## Learning Objectives

By the end of the project, you should be able to:

### Data Storytelling
- Frame a meaningful data problem and transform it into a story arc with a defined audience and clear takeaways.
- Develop the narrative: context → evidence → insights → implications.
- Communicate insights effectively using charts, maps, KPIs and annotations.

### Data Management & Analytics
- Ingest, clean, transform and validate open data.
- Identify missing values, duplicates, outliers and data-quality issues.
- Document assumptions, transformations and limitations.
- Apply EDA and analytical operations, including filtering, group-bys, joins, aggregations and calculated measures.

### Business Intelligence
- Translate a general problem into business/decision questions.
- Define meaningful KPIs and performance measures.
- Compare results against previous periods, geographic areas or other relevant benchmarks.
- Use aggregation and segmentation to identify patterns.
- Detect important trends, anomalies and areas requiring attention.
- Develop rankings or scorecards when relevant.
- Transform analytical findings into decision-support recommendations.

### Streamlit & Visualization
- Build an interactive dashboard using Streamlit.
- Apply appropriate visualizations for comparison, distribution, trends, relationships and geographic information.
- Implement meaningful filters and interactions.
- Apply good dashboard UX and performance practices.

## Reproducibility

Package and deliver a reproducible project with Python code, dataset/source information, requirements and a clear README.

---

## Notes projet (choix dataset)

- Piste envisagée : antennes radio ANFR (Cartoradio).
- ⚠️ cartoradio.fr n'est **pas** un portail approuvé → récupérer les données ANFR via **data.gouv.fr** (portail approuvé).
