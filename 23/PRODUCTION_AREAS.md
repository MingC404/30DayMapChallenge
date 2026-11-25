# Broader display region decisions

A display grouping keeps the original place and source while matching a readable parent province / state or a defined larger region. It does not change the original tea-growing or GI boundary.

| Display region | Original places | Teas | Fill | Definition / match |
|---|---|---|---|---|
| Zhejiang | Anji | Anji Bai Cha | Green | Original source place matched to its parent province |
| Fujian | Anxi; Fuding | Anxi Tie Guan Yin; Fuding Bai Cha | Neutral, mixed tea types | Original source place matched to its parent province |
| Anhui | Huoshan | Huoshan Huang Ya | Yellow | Original source place matched to its parent province |
| Yunnan | Pu'er | Pu'er (ripe) | Dark | Original source place matched to its parent province |
| Guangxi | Hengzhou | Hengxian Mo Li Hua Cha | Scented green | Original source place matched to its parent province |
| Guangdong | Yingde | Yingde Hong Cha | Black | Original source place matched to its parent province |
| Northern Taiwan | Emei | Oriental Beauty | Oolong | https://eng.taiwan.net.tw/m1.aspx?sNo=0029001 |
| Assam | Dibrugarh | Assam black tea | Black | Original source district matched to its parent state |
| West Bengal | Darjeeling | Darjeeling tea | Black | Original source district matched to its parent state |
| Kyushu | Fukuoka / Yame | Yame Gyokuro | Green | https://www.visit-kyushu.com/en/destinations/ |
| Tamil Nadu | Nilgiris | Nilgiri Orthodox | Black | Original source district matched to its parent state |
| Kansai | Kyoto / Uji | Uji matcha | Green | https://www.kansai.meti.go.jp/english/what_is_metikansai.html |
| Central Province | Nuwara Eliya | Nuwara Eliya tea | Black | Source-named Nuwara Eliya location matched to its parent province; not the certification boundary |
| Ha Giang (source-era) | Hoang Su Phi | Shan Tuyet green tea | Green | Archived province associated with Hoang Su Phi in the tourism source; source-era display grouping, not present-day administrative boundaries |

China matches: Anji to Zhejiang; Huoshan to Anhui; Fuding and Anxi to Fujian; Yingde to Guangdong; Hengzhou to Guangxi; Pu’er to Yunnan. The geoBoundaries field `Guangzhou Province` is a source naming anomaly; Guangdong is the verified display alias, with the original Yingde point inside that province geometry.

Japan: Fukuoka / Yame to the seven-prefecture Kyushu region; Kyoto / Uji to the seven-prefecture METI Kansai region (Fukui, Shiga, Kyoto, Osaka, Hyogo, Nara and Wakayama). Taiwan: Emei / Hsinchu to the Tourism Administration Northern Taiwan grouping (Taipei, New Taipei, Keelung, Yilan, Taoyuan, Hsinchu County and Hsinchu City). These named definitions are explicitly identified rather than presumed universal.

All feature IDs, source URLs, vintages, licenses and original coordinates are in the [full audit table](data/tasting/final_region_audit.csv). The display regions are in [final_regions.geojson](data/tasting/final_regions.geojson).