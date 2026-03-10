def select_chart(columns, data):
    if not columns or not data:
        return "bar"

    columns_lower = [str(c).lower() for c in columns]
    first_col = columns_lower[0] if columns_lower else ""

    # Rule 1: Date/Time first column -> ALWAYS Line Chart
    date_keywords = ["date", "month", "year", "week", "day", "time"]
    if any(k in first_col for k in date_keywords):
        return "line"

    # Rule 2: If rows > 10 and it's a category -> Bar Chart
    if len(data) > 10:
        return "bar"

    # Rule 3: Part-to-whole (e.g gender, channel) with small data length -> Pie Chart
    # Since we filter dates and length > 10 out, small categorical data naturally falls to Pie
    if len(columns) >= 2 and len(data) <= 3:
        return "pie"

    return "bar"

if __name__ == "__main__":
    print(select_chart(["Campaign_Type", "Total_Revenue"], [1, 2, 3]))
    print(select_chart(["Date", "Revenue"], [1, 2, 3]))
    print(select_chart(["Region", "Count"], [1, 2]))