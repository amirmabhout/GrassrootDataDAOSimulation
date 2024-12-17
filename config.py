# Configuration
CONFIG = {
    'SIM_CONFIG': {
        'total_steps': 2000,  # Changed from 100 to 300
        'entry_steps': 5,  # Add agents every 5 steps
        'agents_per_entry': 10,  # Total agents to add per entry
        'fee_rate': 0.003,
        'proportions': {
            'degen_user': 0.40,    # 40% degens
            'organization': 0.05,   # 5% orgs
            'power_user': 0.05,    # 5% power users
            'active_user': 0.30,    # 30% active users
            'casual_user': 0.20     # 20% casual users
        }
    },
    'AGENT_CONFIGS': {
        'degen_user': {
            'count': 4,  # Start with 40% of initial 10
            'initial_ddt': 100,
            'initial_xdai': 10,
            'reinvest_rate': 0.5
        },
        'organization': {
            'count': 1,  # Start with 5% of initial 10
            'initial_ddt': 0,
            'initial_xdai': 1000,  # Changed from 1000000 to 1000
            'daily_ddt_buy': 2
        },
        'power_user': {
            'count': 1,  # Start with 5% of initial 10
            'initial_ddt': 100,
            'initial_xdai': 100,
            'daily_spend': 2,
            'max_buy_price': 2.0
        },
        'active_user': {
            'count': 3,  # Start with 30% of initial 10
            'initial_ddt': 100,
            'initial_xdai': 0,
            'daily_spend': 1
        },
        'casual_user': {
            'count': 2,  # Start with 20% of initial 10
            'initial_ddt': 100,
            'initial_xdai': 0,
            'daily_spend': 0.1,
            'sell_threshold': 1.0
        }
    }
}
