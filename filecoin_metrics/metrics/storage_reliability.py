from typing import Dict
from tqdm.auto import tqdm
import pandas as pd
from sqlalchemy.engine.base import Engine


def rate_missing_post_network_weekly(connection: Engine) -> pd.Series:
    QUERY = """
    select
    COUNT(*) filter (where mse."event" = 'SECTOR_FAULTED') as faulty_sectors,
    COUNT(*) as total_sectors,
    to_timestamp(height_to_unix(mse.height))::TIMESTAMP as timestamp
    from miner_sector_events mse
    group by mse.height 
    """

    df = (pd.read_sql(QUERY, connection)
            .set_index('timestamp')
          )

    s = (df.faulty_sectors
           .resample('1w')
           .sum())

    s.name = 'faults_per_week'
    return s

def fraction_missing_post_network_weekly(connection: Engine) -> pd.Series:
    QUERY = """
    select
    COUNT(*) filter (where mse."event" = 'SECTOR_FAULTED') as faulty_sectors,
    COUNT(*) as total_sectors,
    to_timestamp(height_to_unix(mse.height))::TIMESTAMP as timestamp
    from miner_sector_events mse
    group by mse.height
    """

    faulty_fraction = lambda df: df.faulty_sectors / df.total_sectors

    df = (pd.read_sql(QUERY, connection)
            .set_index('timestamp')
            .assign(faulty_fraction=faulty_fraction)
          )

    s = (df.faulty_fraction
           .resample('1w')
           .mean())

    s.name = 'mean_faulty_fraction'
    return s


def rate_missing_post_miner_weekly(connection: Engine) -> Dict[str, pd.Series]:
    QUERY = """
       select
       COUNT(*) filter (where mse."event" = 'SECTOR_FAULTED') as faulty_sectors,
       COUNT(*) as total_sectors,
       to_timestamp(height_to_unix(mse.height))::TIMESTAMP as timestamp,
       miner_id
       from miner_sector_events mse
       group by mse.height, mse.miner_id
    """

    df = (pd.read_sql(QUERY, connection)
            .set_index('timestamp')
          )


    output = {}
    for (miner_id, miner_df) in tqdm(df.groupby('miner_id'),
                                     desc='miners'):
        s = (miner_df.faulty_sectors
             .resample('1w')
             .sum())
        s.name = 'faults_per_week'
        output[miner_id] = s
    return output
