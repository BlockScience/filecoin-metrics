from typing import Dict
from tqdm.auto import tqdm
import pandas as pd
from sqlalchemy.engine.base import Engine

from filecoin_metrics.utils import query_preprocess


def rate_missing_post_network_weekly(connection: Engine) -> pd.Series:
    QUERY = """
    select
    COUNT(*) filter (where mse."event" = 'SECTOR_FAULTED') as faulty_sectors,
    COUNT(*) as total_sectors,
    date_trunc('week', to_timestamp(height_to_unix(mse.height)))::TIMESTAMP as timestamp
    from miner_sector_events mse
    group by timestamp
    """

    query = query_preprocess(QUERY)

    df = pd.read_sql(query, connection).set_index("timestamp")

    s = df.faulty_sectors
    s.name = "faults_per_week"
    return s


def fraction_missing_post_network_weekly(connection: Engine) -> pd.Series:
    QUERY = """
    select
    COUNT(*) filter (where mse."event" = 'SECTOR_FAULTED') as faulty_sectors,
    COUNT(*) as total_sectors,
    date_trunc('week', to_timestamp(height_to_unix(mse.height)))::TIMESTAMP as timestamp
    from miner_sector_events mse
    group by timestamp
    """

    query = query_preprocess(QUERY)

    faulty_fraction = lambda df: df.faulty_sectors / df.total_sectors

    df = (
        pd.read_sql(query, connection)
        .set_index("timestamp")
        .assign(faulty_fraction=faulty_fraction)
    )

    s = df.faulty_fraction
    s.name = "mean_faulty_fraction"
    return s


def rate_missing_post_miner_weekly(connection: Engine) -> Dict[str, pd.Series]:
    QUERY = """
       select
       COUNT(*) filter (where mse."event" = 'SECTOR_FAULTED') as faulty_sectors,
       COUNT(*) as total_sectors,
       date_trunc('week', to_timestamp(height_to_unix(mse.height)))::TIMESTAMP as timestamp,
       miner_id
       from miner_sector_events mse
       group by timestamp, mse.miner_id
    """

    query = query_preprocess(QUERY)

    df = pd.read_sql(query, connection).set_index("timestamp")

    output = {}
    for (miner_id, miner_df) in tqdm(df.groupby("miner_id"), desc="miners"):
        s = miner_df.faulty_sectors.resample("1w").sum()
        s.name = "faults_per_week"
        output[miner_id] = s
    return output


def declare_fault_count_per_miner(connection: Engine) -> pd.Series:
    QUERY = """
    select 
    pm.to as miner_id,
    COUNT(*) as declare_fault_count
    from parsed_messages pm 
    where pm."method" = 'DeclareFaults'
    group by pm.to
    """

    query = query_preprocess(QUERY)

    df = pd.read_sql(query, connection).set_index("miner_id")
    s = df.declare_fault_count
    return s


def sector_activation_and_expiration_by_week(connection) -> pd.Series:
    QUERY = """
        with sector_states as ( 
            select 
            msi.*,
            max(msi.height) over (partition by msi.sector_id, msi.miner_id) as max_height
            from miner_sector_infos msi 
            where msi.activation_epoch > 0
            and msi.expiration_epoch > msi.height 
            order by max_height 
        )
        select 
        count(*) as sector_count,
        date_trunc('WEEK', to_timestamp(height_to_unix(ss.activation_epoch))) as activation_week,
        date_trunc('WEEK', to_timestamp(height_to_unix(ss.expiration_epoch))) as expiration_week
        from sector_states ss
        where ss.max_height = ss.height
        group by activation_week, expiration_week
        order by activation_week, expiration_week
        """

    df = (pd.read_sql(QUERY, connection)
          .assign(expiration_week=lambda df: pd.to_datetime(df.expiration_week, unit='s'))
          .assign(activation_week=lambda df: pd.to_datetime(df.activation_week, unit='s'))
          .set_index(['activation_week', 'expiration_week'])
          )

    s = df.sector_count

    return s


def renewal_count_per_epoch(connection) -> pd.Series:

    QUERY = """
            select 
        to_timestamp(height_to_unix(mse.height)) as timestamp,
        count(*) renewal_count
        from miner_sector_events mse 
        where mse."event" = 'SECTOR_EXTENDED'
        group by mse.height
        """

    df = (pd.read_sql(QUERY, connection)
          .set_index('timestamp')
          )

    s = df.renewal_count

    return s


def declare_fault_weekly(connection) -> pd.Series:
    QUERY = """
    select 
    COUNT(*) as declare_fault_count,
    date_trunc('week', to_timestamp(height_to_unix(pm.height))) as timestamp 
    from parsed_messages pm 
    where pm."method" = 'DeclareFaults'
    group by timestamp
    order by timestamp
        """

    df = (pd.read_sql(QUERY, connection)
          .set_index('timestamp')
          )

    s = df.declare_fault_count

    return s