import streamlit as st
st.title("Benford's Law Analysis Dashboard")
st.write("Upload a file to perform Benford Analysis")
uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx"])
import pandas as pd
import numpy as np
if uploaded_file is not None:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.write(df)
    column = st.selectbox("Select a column", df.columns)   
    st.write(df[column])
    numeric_columns = df.select_dtypes(include="number").columns
    filter_column = st.selectbox("Select a column to filter", numeric_columns)
    min_value = st.number_input("Minimum value", value=0.0)
    max_value = st.number_input("Maximum value", value=df[filter_column].max())
    filtered_df = df[(df[filter_column] >= min_value) & (df[filter_column] <= max_value)]
    category_columns = df.select_dtypes(include="object").columns
    category_column = st.selectbox("Select a category", category_columns)
    category_value = st.selectbox("Select a value", df[category_column].dropna().unique())
    filtered_df = filtered_df[filtered_df[category_column] == category_value]
    st.write(filtered_df)
    analysis_column = st.selectbox("Select a column for Benford Analysis", numeric_columns, index=list(numeric_columns).index("payment_amount") if "payment_amount" in numeric_columns else 0)
    amounts = pd.to_numeric(filtered_df[analysis_column], errors="coerce").abs()
    amounts = amounts.dropna()
    amounts = amounts[amounts > 0]
    first_digits = amounts.astype(str).str.replace(".", "", regex=False).str.lstrip("0").str[0]
    first_digits = first_digits[first_digits.isin(list("123456789"))]
    st.write(first_digits.value_counts().sort_index())
    first_digit_percent = first_digits.value_counts(normalize=True).reindex(list("123456789"), fill_value=0) * 100
    st.write(first_digit_percent)
    def benford_law(d):
        return np.log10(1 + 1/d) * 100
    for d in range(1, 10):
        st.write(d, benford_law(d))
    comparison = pd.DataFrame({
        "Actual (%)": first_digit_percent,
        "Benford (%)": [benford_law(d) for d in range(1,10)]
    }, index=[str(d) for d in range(1, 10)])    
    comparison["Difference"] = comparison["Actual (%)"] - comparison["Benford (%)"]
    st.write(comparison)
    st.bar_chart(comparison[["Actual (%)", "Benford (%)"]], stack=False)
    first_two_digits = amounts.map(lambda x: f"{x:.10f}".replace(".", "").lstrip("0")[:2])
    first_two_digits = first_two_digits[first_two_digits.str.len() == 2]
    first_two_digit_percent = first_two_digits.value_counts(normalize=True).sort_index() * 100
    st.write(first_two_digit_percent)
    two_digits = np.arange(10, 100)
    benford_two_digit = np.log10(1 + 1 / two_digits) * 100
    st.write(pd.DataFrame({"First Two Digits": two_digits, "Benford (%)": benford_two_digit}))

    two_digit_comparison = pd.DataFrame({
        "Actual (%)": first_two_digit_percent.reindex(
            [str(d) for d in two_digits], fill_value=0
        ). values,
        "Benford (%)": benford_two_digit
    }, index=two_digits) 
    two_digit_comparison["Difference"] = two_digit_comparison["Actual (%)"] - two_digit_comparison["Benford (%)"]    
    st.write(two_digit_comparison)
    st.subheader("First Two Digits: Actual vs. Benford")
    st.line_chart(two_digit_comparison[["Actual (%)", "Benford (%)"]])
    actual_cumulative = np.cumsum(two_digit_comparison["Actual (%)"] / 100)
    benford_cumulative = np.cumsum(two_digit_comparison["Benford (%)"] / 100)
    ks_statistic = np.max(np.abs(actual_cumulative - benford_cumulative))
    st.write("First Two Digits KS Statistic:", ks_statistic)
    n = len(first_two_digits)
    ks_critical = 1.36 / np.sqrt(n)
    st.write("KS Critical Value:", ks_critical)
    if ks_statistic > ks_critical:
        st.write("Result: Statistically different from Benford's Law")
    else:
        st.write("Result: Not statistically different from Benford's Law")
    first_actual_cumulative = np.cumsum(comparison["Actual (%)"] / 100)
    first_benford_cumulative = np.cumsum(comparison["Benford (%)"] / 100)
    first_ks = np.max(np.abs(first_actual_cumulative - first_benford_cumulative))
    st.write("First Digit KS Statistic:", first_ks)
    first_ks_critical = 1.36 / np.sqrt(len(first_digits))
    if first_ks > first_ks_critical:
        st.write("First Digit Result: Statistically different from Benford's Law")
    else:
        st.write("First Digit Result: Not statistically different from Benford's Law")
    st.subheader("Download Analysis Results")
    st.download_button(
        label="Download First Digit Analysis",
        data=comparison.to_csv(index=True),
        file_name="first_digit_analysis.csv",
        mime="text/csv"
    )
    st.download_button(
        label="Download First Two Digits Analysis",
        data=two_digit_comparison.to_csv(index=True),
        file_name="first_two_digits_analysis.csv",
        mime="text/csv"
    )
    summary = pd.DataFrame({
        "Test": ["First Digit", "First Two Digits"],
        "KS Statistic": [np.max(first_ks), ks_statistic],
        "Critical Value": [first_ks_critical, ks_critical]
    })
    summary["Result"] = np.where(
        summary["KS Statistic"] > summary["Critical Value"],
        "Statistically Different",
        "Not Statistically Different"
    )
    st.write("Statistical Analysis Summary")
    st.dataframe(summary)
    st.download_button(
        label="Download Summary",
        data=summary.to_csv(index=False),
        file_name="benford_analysis_summary.csv",
        mime="text/csv"
    )
    st.subheader("Descriptive Statistics")
    st.dataframe(amounts.describe())
    st.download_button(
        label="Download Descriptive Statistics",
        data=amounts.describe().to_csv(),
        file_name="descriptive_statistics.csv",
        mime="text/csv"
    )
