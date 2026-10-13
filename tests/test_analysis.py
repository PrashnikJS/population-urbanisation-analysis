import unittest
from analysis import combine, indicator_frame

def payload(indicator, rows):
    return [{}, [{'countryiso3code': 'IND', 'country': {'value': 'India'},
                   'date': str(year), 'value': value} for year, value in rows]]

class PopulationTests(unittest.TestCase):
    def test_growth_and_urban_estimate(self):
        df = combine(payload('pop', [(1960, 100), (1961, 110)]), payload('urban', [(1960, 20), (1961, 25)]))
        self.assertAlmostEqual(df.annual_growth_pct.iloc[1], 10)
        self.assertAlmostEqual(df.estimated_urban_population.iloc[1], 27.5)
        for actual, expected in zip(df.population_index_1960, [100, 110]):
            self.assertAlmostEqual(actual, expected)
    def test_missing_year_is_not_one_year_growth(self):
        df = combine(payload('pop', [(1960, 100), (1962, 120)]), payload('urban', [(1960, 20), (1962, 25)]))
        self.assertTrue(df.annual_growth_pct.isna().all())
    def test_missing_values_are_not_imputed(self):
        df = combine(payload('pop', [(1960, 100), (1961, None)]), payload('urban', [(1960, 20), (1961, 25)]))
        self.assertTrue(df.estimated_urban_population.isna().iloc[1])
    def test_duplicate_and_invalid_percent_are_rejected(self):
        with self.assertRaises(ValueError):
            indicator_frame(payload('pop', [(1960, 100), (1960, 100)]), 'population')
        with self.assertRaises(ValueError):
            combine(payload('pop', [(1960, 100)]), payload('urban', [(1960, 101)]))
