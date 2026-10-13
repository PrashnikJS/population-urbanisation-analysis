# Data source

World Bank, *World Development Indicators*, retrieved 14 October 2026.

- [Population, total: SP.POP.TOTL](https://data.worldbank.org/indicator/SP.POP.TOTL)
- [Urban population, percentage: SP.URB.TOTL.IN.ZS](https://data.worldbank.org/indicator/SP.URB.TOTL.IN.ZS)
- Indicator pages identify the license as [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
- The World Bank credits UN demographic/urbanisation sources, national statistical sources and World Bank estimates as applicable to each indicator.

The API query selects IND, CHN, IDN, BRA, NGA, USA, JPN and DEU, and years 1960-2025. It excludes World Bank regional aggregates by explicitly selecting countries. Raw JSON responses, API update metadata, exact request URLs and SHA-256 hashes are retained in `data/`.

The charts and tables are transformations of these data; no endorsement by the World Bank or the underlying statistical organisations is implied. Refreshing the source can revise observations. No external portfolio code was copied.
