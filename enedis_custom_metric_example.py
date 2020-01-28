"""
Example of custom metric script.
The custom metric script must contain the definition of custom_metric_function and a main function
that reads the two csv files with pandas and evaluate the custom metric.
"""

def custom_metric_function(dataframe_1, dataframe_2):
    """
        Example of custom metric function.

    Args
        dataframe_1: Pandas Dataframe
            This dataframe was obtained by reading a csv file with following instruction:
            dataframe_1 = pd.read_csv(CSV_1_FILE_PATH, index_col=0, sep=',')

        dataframe_2: Pandas Dataframe
            This dataframe was obtained by reading a csv file with following instruction:
            dataframe_2 = pd.read_csv(CSV_2_FILE_PATH, index_col=0, sep=',')

    Returns
        score: Float
            The metric evaluated with the two dataframes. This must not be NaN.
    """
    result = dataframe_1.merge(dataframe_2, left_index=True, right_index=True, how='left')
    result.fillna(100)

    if 'RES1_BASE' in dataframe_2.columns:
        RMSERES1 = ((result.RES1_BASE_x - result.RES1_BASE_y) ** 2).mean() ** .5
    else:
        RMSERES1 = 1000

    if 'RES11_BASE' in dataframe_2.columns:
        RMSERES11 = ((result.RES11_BASE_x - result.RES11_BASE_y) ** 2).mean() ** .5
    else:
        RMSERES11 = 1000

    if 'RES2_HC' in dataframe_2.columns:
        RMSERES2_HC = ((result.RES2_HC_x - result.RES2_HC_y) ** 2).mean() ** .5
    else:
        RMSERES2_HC = 1000

    if 'RES2_HP' in dataframe_2.columns:
        RMSERES2_HP = ((result.RES2_HP_x - result.RES2_HP_y) ** 2).mean() ** .5
    else:
        RMSERES2_HP = 1000

    if 'PRO1_BASE' in dataframe_2.columns:
        RMSEPRO1 = ((result.PRO1_BASE_x - result.PRO1_BASE_y) ** 2).mean() ** .5
    else:
        RMSEPRO1 = 1000

    if 'PRO2_HC' in dataframe_2.columns:
        RMSEPRO2_HC = ((result.PRO2_HC_x - result.PRO2_HC_y) ** 2).mean() ** .5
    else:
        RMSEPRO2_HC = 1000

    if 'PRO2_HP' in dataframe_2.columns:
        RMSEPRO2_HP = ((result.PRO2_HP_x - result.PRO2_HP_y) ** 2).mean() ** .5
    else:
        RMSEPRO2_HP = 1000

    score = round(
        10. / 11 * (
            (RMSEPRO2_HP / 0.1855 + RMSEPRO2_HC / 0.2878 + RMSEPRO1 / 0.2140) * 1 +
            (RMSERES2_HP / 0.1659 + RMSERES2_HC / 0.2 + RMSERES11 / 0.1456 + RMSERES1 / 0.1028) * 2),
        3)

    return score


if __name__ == '__main__':
    import pandas as pd
    CSV_FILE_1 = 'testing_output.csv'
    CSV_FILE_2 = 'testing_benchmark.csv'
    df_1 = pd.read_csv(CSV_FILE_1, index_col=0, sep=',')
    df_2 = pd.read_csv(CSV_FILE_2, index_col=0, sep=',')
    print(custom_metric_function(df_1, df_2))
