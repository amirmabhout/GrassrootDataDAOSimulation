from typing import Dict, Any
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def get_env_float(key: str, default: float) -> float:
    return float(os.getenv(key, default))

def get_env_int(key: str, default: int) -> int:
    return int(os.getenv(key, default))

# Configuration
CONFIG = {
    'SIM_CONFIG': {
        'initial_pool_tokens': get_env_float('INITIAL_POOL_TOKENS', 1000),
        'initial_pool_dollars': get_env_float('INITIAL_POOL_DOLLARS', 1000),
        'total_steps': get_env_int('TOTAL_STEPS', 100),
        'steps_before_orgs': get_env_int('STEPS_BEFORE_ORGS', 30),
        'fee_rate': get_env_float('FEE_RATE', 0.003),
        'degen_entry_price': get_env_float('DEGEN_ENTRY_PRICE', 0.05),
        'max_degens': get_env_int('MAX_DEGENS', 40)
    },
    'AGENT_CONFIGS': {
        'degen_user': {
            'count': get_env_int('DEGEN_COUNT', 5),
            'initial_tokens': get_env_float('DEGEN_INITIAL_TOKENS', 100),
            'initial_dollars': get_env_float('DEGEN_INITIAL_DOLLARS', 10),
            'initial_liquidity': get_env_float('DEGEN_INITIAL_LIQUIDITY', 10),
            'reinvest_rate': get_env_float('DEGEN_REINVEST_RATE', 0.5)
        },
        'org_agent': {
            'count': get_env_int('ORG_COUNT', 5),
            'initial_tokens': 0,
            'initial_dollars': get_env_float('ORG_INITIAL_DOLLARS', 1000000),
            'daily_token_buy': get_env_float('ORG_DAILY_TOKEN_BUY', 2)
        },
        'power_user': {
            'count': get_env_int('POWER_USER_COUNT', 5),
            'initial_tokens': get_env_float('POWER_USER_INITIAL_TOKENS', 100),
            'initial_dollars': get_env_float('POWER_USER_INITIAL_DOLLARS', 1000),
            'daily_spend': get_env_float('POWER_USER_DAILY_SPEND', 2)
        },
        'most_active_user': {
            'count': get_env_int('MOST_ACTIVE_COUNT', 30),
            'initial_tokens': get_env_float('MOST_ACTIVE_INITIAL_TOKENS', 100),
            'initial_dollars': get_env_float('MOST_ACTIVE_INITIAL_DOLLARS', 100),
            'daily_spend': get_env_float('MOST_ACTIVE_DAILY_SPEND', 1)
        },
        'least_active_user': {
            'count': get_env_int('LEAST_ACTIVE_COUNT', 20),
            'initial_tokens': get_env_float('LEAST_ACTIVE_INITIAL_TOKENS', 100),
            'initial_dollars': get_env_float('LEAST_ACTIVE_INITIAL_DOLLARS', 100),
            'daily_spend': get_env_float('LEAST_ACTIVE_DAILY_SPEND', 1),
            'keep_tokens': get_env_float('LEAST_ACTIVE_KEEP_TOKENS', 20)
        }
    }
}
