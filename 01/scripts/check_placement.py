"""Verify evidence parsing against actual data and isolated synthetic labels."""
import csv
from collections import Counter
from build_changing_station_explorer import SOURCE, placement_matches

with SOURCE.open(encoding='utf-8-sig', newline='') as source:
    rows = list(csv.DictReader(source))
counts = Counter(key for row in rows for key in placement_matches(row['Changing Stations']))
assert counts == {'unspecified': 659, 'women': 83, 'men': 27, 'all_gender': 26}, counts
assert placement_matches("Yes, in both women's and men's restrooms") == ['women', 'men']
assert placement_matches("Yes, in men's and women's restrooms") == ['women', 'men']
assert placement_matches('Yes, in single-stall all gender restroom only') == ['all_gender']
assert placement_matches('Yes, in single-stall restroom only') == []
assert placement_matches("Yes, in women's and men's restrooms only") == ['women', 'men']
assert placement_matches("No, in women's restroom") == []
assert placement_matches("Women's Library") == []
assert placement_matches('Yes') == ['unspecified']
assert placement_matches('') == []
print('PASS: actual labels, explicit dual-type evidence, no name/single-stall inference.')
