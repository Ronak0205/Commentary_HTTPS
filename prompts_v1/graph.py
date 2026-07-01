CLASSIFY_PROMPT = """
Look at this image and list every type of content it contains.
Respond with only the matching labels separated by commas, no other text:
TABLE if it contains a data table
BAR_CHART if it contains a bar chart, including stacked bar charts
PIE_CHART if it contains a pie chart
LINE_CHART if it contains a line chart
NONE if it contains none of the above
"""

TABLE_PROMPT = """
Extract the table from this image into JSON.
Use the table's actual column headers as keys.
Return a JSON object with a single key "table" containing a list of row objects.
Every value must be a plain number or a plain string, never an expression, never a percent sign attached to a number, never arithmetic.
If a cell is blank or unreadable, use null.
Return only valid JSON, no other text, no markdown fences.
"""

GRAPH_PROMPT = """
Extract every chart visible in this image into JSON. The image may contain more than one chart stacked vertically, each with its own title and legend; extract each one separately.

For each chart, first determine its structure by looking carefully at axes, bars, lines, and legend:

- "category": one bar or point per category, no time periods.
- "time_period_stacked": one bar per time period (for example YE22, YE23, Q1'2026), each bar divided into colored segments by category, y-axis is an absolute number.
- "time_period_percent_stacked": one bar per time period, each bar divided into colored segments by category, but the segments represent a share of 100% for that period rather than an absolute amount, y-axis range is 0 to 100%.
- "time_period_grouped": one bar per time period, but the categories are side-by-side bars next to each other rather than stacked on top of each other.
- "time_period_line": a single line or a few separate lines across time periods, not bars.
- "time_period_combo": bars and at least one line appear in the same chart together. This often means two different y-axes are in use, one on the left for the bars and one on the right for the line, look at both axis scales separately.

Return a JSON object with a single key "charts", a list of chart objects.
Each chart object has: chart_type, title, x_axis_label, y_axis_label, x_axis_type, periods, and series.

"periods" is the list of x-axis labels in order, for example ["YE22", "YE23", "YE24", "YE25", "Q1'2026"].
series is a list of objects, each with:
"name" (the legend/category label)
"axis" ("left" or "right", only needed when x_axis_type is "time_period_combo", otherwise omit this field)
"values" which is a list of numbers, in the same order as "periods", one number per period for that series.

Rules:
- If x_axis_type is "time_period_percent_stacked", each value must be the percent for that segment in that period's bar, and all segment values for a single period should sum to approximately 100.
- If a marker, dot, or label on the chart is a different color or style than the rest of its own series, still record its numeric value the same way, but add "highlighted_periods" to that series listing which period(s) looked visually distinct.
- Read exact values from printed data labels whenever visible. Only estimate from bar height or line position against the gridlines when no label is printed.
- Every numeric value must be a plain number, never an expression, never a percent sign attached to a number.
- Do not leave values empty or null just because they require reading a position on the chart, give your best estimate using the axis scale.
Return only valid JSON, no other text, no markdown fences.
"""

PIE_CHART_PROMPT = """
This image may contain one or more pie charts, and may also contain other charts above or below them.
Extract every pie chart you see, ignore any non-pie charts.

Return a JSON object with a single key "pie_charts", a list of pie chart objects.
Each pie chart object has: title, as_of_date, and slices.
slices is a list of objects, each with "name" (from the legend) and "percent" (the exact number printed next to that slice, without the percent sign).

Match each percent label to its slice using its position and the connecting line in the image, not by guessing from category size.
Every percent value must be a plain number, never an expression.
Do not invent or estimate a percent that is not visibly printed in the image.
Return only valid JSON, no other text, no markdown fences.
"""

BOTH_PROMPT = """
This image contains a table and one or more charts.
Extract everything into a single JSON object with two top level keys: "table" and "charts".

"table" is a list of row objects using the table's actual column headers as keys.

"charts" is a list of chart objects, one per chart visible in the image. For each chart, first determine its structure:
- "category": one bar/point per category, and those categories match the table's row names.
- "time_period_stacked": one bar per time period (for example YE22, Q1'2026), each divided into colored segments by category, y-axis is an absolute number.
- "time_period_percent_stacked": same as above but segments represent a 0-100% share rather than an absolute amount.
- "time_period_grouped": one bar per time period, categories shown as separate side-by-side bars rather than stacked.
- "time_period_combo": bars and at least one line in the same chart, often with two different y-axes, one left one right.

Each chart object has chart_type, title, x_axis_label, y_axis_label, x_axis_type, periods, and series.
"periods" is the list of x-axis labels in order (omit if x_axis_type is "category").
series is a list of objects, each with "name" (the legend/category label), optionally "axis" ("left" or "right", only for "time_period_combo"), and "values".

If x_axis_type is "category": also set "source_table_column" to the exact name of the table column whose values this chart is visualizing (look at the chart's axis scale and compare it to the table's columns to decide which one matches). "values" can then be left empty, it will be filled in automatically from that table column. If no table column matches the chart, read the values directly from the image instead and omit "source_table_column".
Otherwise: "values" is a list of numbers, same length and order as "periods", one number per period for that series. Read the segment height or line position for each period as closely as possible using the y-axis scale and gridlines, or use the printed data label if visible. Use 0, not null, if a period's value for that series is not visible or zero.

Only the most recent period's table data is guaranteed to exist in "table"; older periods shown in charts will not appear in the table, so for those you must read values from the chart itself.

Every numeric value anywhere in the output must be a plain number, never an expression like 5/2 or 5e+9/4, never a percent sign attached to a number.
If a table cell is blank or unreadable, use null.
Return only valid JSON, no other text, no markdown fences.
"""