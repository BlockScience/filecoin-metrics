# import libraries
from sqlalchemy import create_engine
import pandas as pd

# supress scientific notation
pd.set_option('display.float_format', lambda x: '%.5f' % x)

# load connection string
CONN_STRING_PATH = 'sentinel_conn_string_andrew.txt'

with open(CONN_STRING_PATH, 'r') as fid:
    conn_string = fid.read()
    
# create database connection.
connection = create_engine(conn_string, pool_recycle=3600).connect()


QUERY = """
SELECT 
date_trunc('day', 
to_timestamp(height_to_unix(d.height))) AS timestamp,
AVG(CAST(gas_fee_cap AS FLOAT)) AS mean_gas_fee_cap,
AVG(CAST(gas_premium AS FLOAT))  as mean_gas_premium,
AVG(CAST(gas_limit AS FLOAT))  as mean_gas_limit,
AVG(CAST(gas_used AS FLOAT))  as mean_gas_used,
AVG(CAST(parent_base_fee AS FLOAT))  as mean_parent_base_fee,
AVG(CAST(base_fee_burn AS FLOAT))  as mean_base_fee_burn,
AVG(CAST(over_estimation_burn AS FLOAT))  as mean_over_estimation_burn,
AVG(CAST(gas_refund AS FLOAT))  as mean_gas_refund,
AVG(CAST(gas_burned AS FLOAT))  as mean_gas_burned
FROM derived_gas_outputs d
WHERE
to_timestamp(height_to_unix(d.height)) BETWEEN '2021-01-01' AND '2021-07-31'
GROUP BY
timestamp
"""
derived_gas_outputs_day = (pd.read_sql(QUERY, connection))

QUERY = """
SELECT 
date_trunc('day', 
to_timestamp(height_to_unix(cr.height))) AS timestamp,
AVG(CAST(cr.cum_sum_baseline AS FLOAT)) AS mean_cum_sum_baseline,
AVG(CAST(cr.cum_sum_realized AS FLOAT)) AS mean_cum_sum_realized,
AVG(CAST(cr.effective_baseline_power AS FLOAT)) AS mean_effective_baseline_power,
AVG(CAST(cr.effective_network_time AS FLOAT)) AS mean_effective_network_time,
AVG(CAST(cr.new_baseline_power AS FLOAT)) AS mean_new_baseline_power,
AVG(CAST(cr.new_reward AS FLOAT)) AS mean_new_reward,
AVG(CAST(cr.new_reward_smoothed_position_estimate AS FLOAT)) AS mean_new_reward_smoothed_position_estimate,
AVG(CAST(cr.new_reward_smoothed_velocity_estimate AS FLOAT)) AS mean_new_reward_smoothed_velocity_estimate,
AVG(CAST(cr.total_mined_reward AS FLOAT)) AS mean_total_mined_reward,
AVG(CAST(cp.miner_count AS FLOAT)) AS mean_miner_count,
AVG(CAST(cp.participating_miner_count AS FLOAT)) AS mean_participating_miner_count,
AVG(CAST(cp.qa_smoothed_position_estimate AS FLOAT)) AS mean_qa_smoothed_position_estimate,
AVG(CAST(cp.qa_smoothed_velocity_estimate AS FLOAT)) AS mean_qa_smoothed_velocity_estimate,
AVG(CAST(cp.total_pledge_collateral AS FLOAT)) AS mean_total_pledge_collateral,
AVG(CAST(cp.total_qa_bytes_committed AS FLOAT)) AS mean_total_qa_bytes_committed,
AVG(CAST(cp.total_qa_bytes_power AS FLOAT)) AS mean_total_qa_bytes_power,
AVG(CAST(cp.total_raw_bytes_committed AS FLOAT)) AS mean_total_raw_bytes_committed,
AVG(CAST(cp.total_raw_bytes_power AS FLOAT)) AS mean_total_raw_bytes_power,
AVG(CAST(ce.burnt_fil AS FLOAT)) AS mean_burnt_fil,
AVG(CAST(ce.circulating_fil AS FLOAT)) AS mean_circulating_fil,
AVG(CAST(ce.locked_fil AS FLOAT)) AS mean_locked_fil,
AVG(CAST(ce.mined_fil AS FLOAT)) AS mean_mined_fil,
AVG(CAST(ce.vested_fil AS FLOAT)) AS mean_vested_fil
FROM chain_rewards cr
LEFT JOIN chain_powers cp
ON cr.state_root = cp.state_root
LEFT JOIN chain_economics ce
ON cr.state_root = ce.parent_state_root
WHERE
to_timestamp(height_to_unix(cr.height)) BETWEEN '2021-01-01' AND '2021-07-31'
GROUP BY
timestamp
"""
chain_economics_day = (pd.read_sql(QUERY, connection))

# combine signals
combined_day = derived_gas_outputs_day.merge(chain_economics_day,how='left',on='timestamp')

# split into train and test
combined_day_test = combined_day.tail(10)
combined_day = combined_day.head(len(combined_day)-10)

del combined_day['timestamp']
combined_day.fillna(0,inplace=True)

# Extremely simplistic model for rough draft due to data issues.
df_constant_ewm = combined_day.ewm(alpha=0.5).mean()
df_constant_ewm_forcast=df_constant_ewm.tail(5)
df_constant_ewm_forcast