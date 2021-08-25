import re
from io import StringIO

import matplotlib.dates as dates
import pandas
import tabula
from matplotlib import pyplot, rcParams

data = pandas.concat(
    [
        pandas.read_csv(
            StringIO(
                "番号,発表日,番号2,年代,性別,居住地,職業,感染経路\n"
                + re.sub(
                    ",+",
                    ",",
                    x.to_csv(index=False, header=False)
                    .replace(" ", ",")
                    .replace(")100", "),100"),
                )
            )
        )
        for x in tabula.read_pdf(
            "https://www.city.kawasaki.jp/350/cmsfiles/contents/0000116/116827/4.pdf",
            pages="all",
        )
    ]
)
data.番号 = data.番号.str.replace("例目", "").astype(int)
data.loc[pandas.isna(data.感染経路), "職業":"感染経路"] = data[pandas.isna(data.感染経路)][
    ["感染経路", "職業"]
].values
data.発表日 = data.発表日.replace("(.+)日\\(.?\\)", "\\1", regex=True).str.replace(
    "月", "-", regex=False
)
if (data.番号 < 4446).sum():
    data.loc[data.番号 < 4446, "発表日"] = pandas.to_datetime(
        "2020-" + data.発表日[data.番号 < 4446]
    )
if (data.番号 >= 4446).sum():
    data.loc[data.番号 >= 4446, "発表日"] = pandas.to_datetime(
        "2021-" + data.発表日[data.番号 >= 4446]
    )
data.年代 = (
    data.年代.replace("\\(\\d+\\) ?", "", regex=True)
    .replace(".+ ", "", regex=True)
    .replace("100歳以", "100歳以上", regex=False)
    .replace("(\\d+代)", "​\\1", regex=True)
    .replace("100歳以上", "​​100歳以上", regex=False)
)
rcParams["font.family"] = "sans-serif"
rcParams["font.sans-serif"] = ["Meiryo"]
table = (
    data.groupby(["発表日", "年代"])
    .発表日.count()
    .unstack()
    .resample("D")
    .sum()
    .rolling(7)
    .mean()
)
fig, ax = pyplot.subplots(figsize=(10, 5))
ax.stackplot(table.index, table.T, baseline="sym")
ax.legend(table.columns, loc="upper left", ncol=2)
ax.xaxis.set_major_formatter(dates.DateFormatter("%y-%m"))
pyplot.show()
table = (
    data.groupby(["発表日", "性別"])
    .発表日.count()
    .unstack()
    .resample("D")
    .sum()
    .rolling(7)
    .mean()
)
fig, ax = pyplot.subplots(figsize=(10, 5))
ax.stackplot(table.index, table.T, baseline="sym")
ax.legend(table.columns, loc="upper left", ncol=2)
ax.xaxis.set_major_formatter(dates.DateFormatter("%y-%m"))
pyplot.show()
