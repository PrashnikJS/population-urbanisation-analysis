"""Compare population growth and urbanisation, without predicting demand."""
from pathlib import Path
import json
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).parent

def indicator_frame(payload, column):
    records = payload[1]
    rows = [{'country_code': r['countryiso3code'], 'country': r['country']['value'],
             'year': int(r['date']), column: r['value']} for r in records]
    df = pd.DataFrame(rows)
    if df.duplicated(['country_code', 'year']).any():
        raise ValueError('Repeated country-year observation')
    df[column] = pd.to_numeric(df[column], errors='coerce')
    return df

def combine(population_payload, urban_payload):
    population = indicator_frame(population_payload, 'population')
    urban = indicator_frame(urban_payload, 'urban_share_pct')
    df = population.merge(urban.drop(columns='country'),
                          on=['country_code', 'year'], how='outer', validate='one_to_one')
    df = df.sort_values(['country_code', 'year']).reset_index(drop=True)
    if ((df.population.dropna() <= 0).any() or
            ((df.urban_share_pct.dropna() < 0) | (df.urban_share_pct.dropna() > 100)).any()):
        raise ValueError('Indicator outside its valid range')
    previous = df.groupby('country_code').population.shift()
    previous_year = df.groupby('country_code').year.shift()
    df['annual_growth_pct'] = ((df.population / previous - 1) * 100).where(df.year - previous_year == 1)
    baseline = df.loc[df.year == 1960].set_index('country_code').population
    df['population_index_1960'] = df.population / df.country_code.map(baseline) * 100
    df['estimated_urban_population'] = df.population * df.urban_share_pct / 100
    return df

def save_charts(df, out):
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
                         'axes.spines.top': False, 'axes.spines.right': False})
    fig, ax = plt.subplots(figsize=(11, 6))
    for country, group in df.groupby('country'):
        ax.plot(group.year, group.population_index_1960, label=country, linewidth=2)
    ax.set(title='Population growth on a common 1960 baseline', xlabel='Year',
           ylabel='Population index (1960 = 100)')
    ax.legend(ncol=2, loc='upper left'); ax.grid(alpha=.2)
    fig.tight_layout(); fig.savefig(out / 'population_growth.png', dpi=180); plt.close(fig)

    fig, ax = plt.subplots(figsize=(11, 6))
    for country, group in df.groupby('country'):
        ax.plot(group.year, group.urban_share_pct, label=country, linewidth=2)
    ax.set(title='Urban share of population', xlabel='Year', ylabel='Urban population (%)', ylim=(0, 100))
    ax.legend(ncol=2); ax.grid(alpha=.2)
    fig.tight_layout(); fig.savefig(out / 'urbanisation_trends.png', dpi=180); plt.close(fig)

    decade = df[df.year.isin([1960, 1970, 1980, 1990, 2000, 2010, 2020, 2025])]
    pivot = decade.pivot(index='country', columns='year', values='urban_share_pct')
    fig, ax = plt.subplots(figsize=(10, 5))
    image = ax.imshow(pivot, cmap='YlGnBu', vmin=0, vmax=100, aspect='auto')
    ax.set_xticks(range(len(pivot.columns)), pivot.columns)
    ax.set_yticks(range(len(pivot.index)), pivot.index)
    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            value = pivot.iloc[i, j]
            ax.text(j, i, '-' if pd.isna(value) else f'{value:.0f}', ha='center', va='center',
                    color='white' if pd.notna(value) and value > 65 else 'black')
    ax.set_title('Urban share by country and selected year (%)')
    fig.colorbar(image, ax=ax, label='Urban share (%)')
    fig.tight_layout(); fig.savefig(out / 'urban_share_heatmap.png', dpi=180); plt.close(fig)

def main():
    pop = json.loads((ROOT / 'data/population.json').read_text())
    urban = json.loads((ROOT / 'data/urban_share.json').read_text())
    df = combine(pop, urban)
    out = ROOT / 'outputs'; out.mkdir(exist_ok=True)
    df.to_csv(out / 'country_year.csv', index=False)
    latest_year = int(df.dropna(subset=['population', 'urban_share_pct']).year.max())
    latest = df[df.year == latest_year].copy()
    latest.to_csv(out / 'latest_country_summary.csv', index=False)
    metrics = {'countries': int(df.country_code.nunique()), 'country_year_rows': len(df),
               'year_min': int(df.year.min()), 'year_max': int(df.year.max()),
               'missing_population': int(df.population.isna().sum()),
               'missing_urban_share': int(df.urban_share_pct.isna().sum()),
               'latest_comparison_year': latest_year, 'charts': 3}
    save_charts(df, out)
    (out / 'metrics.json').write_text(json.dumps(metrics, indent=2))
    india = latest[latest.country_code == 'IND'].iloc[0]
    note = f"The {latest_year} India observation has an urban share of {india.urban_share_pct:.2f}%. Indexed population plots compare relative growth rather than population size. National urban definitions differ; these indicators alone do not measure purchasing power or forecast market demand."
    (out / 'findings.md').write_text('# Population and urbanisation review\n\n' + note + '\n')
    (out / 'report.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Population and urbanisation</title><style>body{font:16px/1.6 system-ui;max-width:1100px;margin:35px auto;padding:20px;color:#18303e}img{width:100%;height:auto}table{border-collapse:collapse;font-size:13px}td,th{padding:8px;border:1px solid #ccc}.wide{overflow:auto}</style><h1>Population and urbanisation analysis</h1><p>' + note + '</p><img alt="Indexed population trends" src="population_growth.png"><img alt="Urbanisation trends" src="urbanisation_trends.png"><img alt="Urban share heatmap" src="urban_share_heatmap.png"><h2>Latest observations</h2><div class="wide">' + latest.round(2).to_html(index=False) + '</div></html>')
    print(json.dumps(metrics, indent=2))

if __name__ == '__main__':
    main()
