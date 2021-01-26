import pandas as pd
import plotly.express as px


def simple_time_series(fig_df: pd.DataFrame,
                       VIZ_PARAMS: dict):
    if len(fig_df) > 0:
        fig = px.line(fig_df,
                      x='time',
                      y='value',
                      **VIZ_PARAMS
                      )
    else:
        fig = None
    return fig
