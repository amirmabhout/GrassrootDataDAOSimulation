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
        'initial_pool_ddt': get_env_float('INITIAL_POOL_DDT', 1000),
        'initial_pool_xdai': get_env_float('INITIAL_POOL_XDAI', 1000),
        'total_steps': get_env_int('TOTAL_STEPS', 100),
        'steps_before_orgs': get_env_int('STEPS_BEFORE_ORGS', 30),
        'fee_rate': get_env_float('FEE_RATE', 0.003),
        'degen_entry_price': get_env_float('DEGEN_ENTRY_PRICE', 0.05),
        'max_degens': get_env_int('MAX_DEGENS', 40)
    },
    'AGENT_CONFIGS': {
        'degen_user': {
            'count': get_env_int('DEGEN_COUNT', 5),
            'initial_ddt': get_env_float('DEGEN_INITIAL_DDT', 100),
            'initial_xdai': get_env_float('DEGEN_INITIAL_XDAI', 10),
            'initial_liquidity': get_env_float('DEGEN_INITIAL_LIQUIDITY', 10),
            'reinvest_rate': get_env_float('DEGEN_REINVEST_RATE', 0.5)
        },
        'organization': {
            'count': get_env_int('ORG_COUNT', 5),
            'initial_ddt': 0,
            'initial_xdai': get_env_float('ORG_INITIAL_XDAI', 1000000),
            'daily_ddt_buy': get_env_float('ORG_DAILY_DDT_BUY', 2)
        },
        'power_user': {
            'count': get_env_int('POWER_USER_COUNT', 5),
            'initial_ddt': get_env_float('POWER_USER_INITIAL_DDT', 100),
            'initial_xdai': get_env_float('POWER_USER_INITIAL_XDAI', 1000),
            'daily_spend': get_env_float('POWER_USER_DAILY_SPEND', 2)
        },
        'active_user': {
            'count': get_env_int('ACTIVE_USER_COUNT', 30),
            'initial_ddt': get_env_float('ACTIVE_USER_INITIAL_DDT', 100),
            'initial_xdai': get_env_float('ACTIVE_USER_INITIAL_XDAI', 100),
            'daily_spend': get_env_float('ACTIVE_USER_DAILY_SPEND', 1)
        },
        'casual_user': {
            'count': get_env_int('CASUAL_USER_COUNT', 20),
            'initial_ddt': get_env_float('CASUAL_USER_INITIAL_DDT', 100),
            'initial_xdai': get_env_float('CASUAL_USER_INITIAL_XDAI', 100),
            'daily_spend': get_env_float('CASUAL_USER_DAILY_SPEND', 1),
            'keep_ddt': get_env_float('CASUAL_USER_KEEP_DDT', 20)
        }
    }
}
