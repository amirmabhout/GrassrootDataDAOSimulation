import autogen
from typing import Dict, Any, List
from liquidity_pool import LiquidityPool
import pandas as pd
import inspect

class BaseAutoAgent:
    def __init__(self, name: str, initial_ddt: float, initial_xdai: float, **kwargs):
        self.name = name
        self.ddt = initial_ddt
        self.xdai = initial_xdai
        self.ddt_spent = 0
        self.transaction_history = []
    
    def record_transaction(self, action: str, ddt: float, xdai: float):
        self.transaction_history.append({
            'agent': self.name,
            'action': action,
            'ddt': ddt,
            'xdai': xdai,
            'ddt_balance': self.ddt,
            'xdai_balance': self.xdai
        })

class ThePie:
    """The Pie accumulates all spent dDT from the ecosystem"""
    def __init__(self):
        self.total_ddt = 0
        self.transactions = []
        self.distribution_ratios = {
            'casual_user': 0.2,   # 20% of 70% distributed
            'active_user': 0.4,   # 40% of 70% distributed
            'power_user': 0.4     # 40% of 70% distributed
        }
        
    def receive_ddt(self, amount: float, from_agent: str):
        self.total_ddt += amount
        self.transactions.append({
            'from': from_agent,
            'amount': amount,
            'total_after': self.total_ddt
        })
    
    def distribute_rewards(self, agents):
        if self.total_ddt == 0:
            return
            
        # Calculate total distribution (70% of pie)
        total_distribution = self.total_ddt * 0.7
        self.total_ddt -= total_distribution
        
        # Group agents by type
        agent_groups = {
            'casual_user': [],
            'active_user': [],
            'power_user': []
        }
        
        for agent in agents:
            agent_type = agent.name.split('_')[0]
            if agent_type in agent_groups:
                agent_groups[agent_type].append(agent)
        
        # Distribute to each group according to ratios
        for agent_type, ratio in self.distribution_ratios.items():
            if agent_groups[agent_type]:
                group_share = total_distribution * ratio
                per_agent_share = group_share / len(agent_groups[agent_type])
                
                for agent in agent_groups[agent_type]:
                    agent.receive_pie_share(per_agent_share)

class DegenAgent(BaseAutoAgent):
    def __init__(self, name: str, liquidity_pool: LiquidityPool, the_pie: ThePie, config: Dict[str, Any]):
        super().__init__(name=name,
                        initial_ddt=config['initial_ddt'],
                        initial_xdai=config['initial_xdai'])
        self.liquidity_pool = liquidity_pool
        self.the_pie = the_pie
        self.reinvest_rate = config['reinvest_rate']
        
    async def step(self):
        # If this is our first step, provide liquidity and sell remaining dDT
        if not self.transaction_history:
            # Provide initial liquidity (10 dDT and 10 xDAI)
            if self.ddt >= 10 and self.xdai >= 10:
                self.liquidity_pool.add_liquidity(10, 10)
                self.ddt -= 10
                self.xdai -= 10
                self.record_transaction('provide_liquidity', 10, 10)
                
                # Sell remaining 90 dDT
                if self.ddt >= 90:
                    xdai_received = self.liquidity_pool.sell_ddt(90)
                    self.ddt -= 90
                    self.xdai += xdai_received
                    self.record_transaction('sell_ddt', 90, xdai_received)
        
        # Collect fees from liquidity provision
        fees = self.liquidity_pool.collect_fees(self.name)
        if fees > 0:
            # Reinvest 50% of fees into liquidity pool
            reinvest_amount = fees * self.reinvest_rate
            if reinvest_amount > 0:
                self.liquidity_pool.add_liquidity(reinvest_amount, reinvest_amount)
                self.record_transaction('reinvest_fees', reinvest_amount, reinvest_amount)
            
            # Keep remaining 50% as xDAI profit
            self.xdai += fees * (1 - self.reinvest_rate)

class OrganizationAgent(BaseAutoAgent):
    def __init__(self, name: str, liquidity_pool: LiquidityPool, the_pie: ThePie, config: Dict[str, Any]):
        super().__init__(name=name,
                        initial_ddt=0,  # Start with no dDT
                        initial_xdai=config['initial_xdai'])
        self.liquidity_pool = liquidity_pool
        self.the_pie = the_pie
        self.daily_ddt_buy = config['daily_ddt_buy']  # Amount of dDT to buy and spend daily
    
    async def step(self):
        # Organizations always try to buy their daily amount and spend it immediately
        current_price = self.liquidity_pool.get_price()
        xdai_needed = self.daily_ddt_buy * current_price
        
        if self.xdai >= xdai_needed:
            ddt_received = self.liquidity_pool.buy_ddt(xdai_needed)
            if ddt_received > 0:
                self.xdai -= xdai_needed
                # Immediately spend the bought dDT
                self.the_pie.receive_ddt(ddt_received, self.name)
                self.record_transaction('buy_and_spend_ddt', ddt_received, xdai_needed)

class PowerUserAgent(BaseAutoAgent):
    def __init__(self, name: str, liquidity_pool: LiquidityPool, the_pie: ThePie, config: Dict[str, Any]):
        super().__init__(name=name,
                        initial_ddt=config['initial_ddt'],
                        initial_xdai=config['initial_xdai'])
        self.liquidity_pool = liquidity_pool
        self.the_pie = the_pie
        self.daily_spend = config['daily_spend']
        self.max_price = 2.0  # Maximum price willing to pay per dDT
    
    def receive_pie_share(self, amount: float):
        # Power users keep their pie share for service usage
        self.ddt += amount
        self.record_transaction('receive_pie_share', amount, 0)
    
    async def step(self):
        # Always try to spend daily_spend amount of dDT
        if self.ddt >= self.daily_spend:
            # Use own dDT supply first
            self.ddt -= self.daily_spend
            self.the_pie.receive_ddt(self.daily_spend, self.name)
            self.record_transaction('spend_ddt', self.daily_spend, 0)
        else:
            # Need to buy dDT from market
            current_price = self.liquidity_pool.get_price()
            if current_price <= self.max_price:
                xdai_needed = self.daily_spend * current_price
                if self.xdai >= xdai_needed:
                    ddt_received = self.liquidity_pool.buy_ddt(xdai_needed)
                    if ddt_received > 0:
                        self.xdai -= xdai_needed
                        self.ddt += ddt_received
                        self.record_transaction('buy_ddt', ddt_received, xdai_needed)
                        
                        # Spend the bought dDT
                        self.ddt -= self.daily_spend
                        self.the_pie.receive_ddt(self.daily_spend, self.name)
                        self.record_transaction('spend_ddt', self.daily_spend, 0)

class ActiveUserAgent(BaseAutoAgent):
    def __init__(self, name: str, liquidity_pool: LiquidityPool, the_pie: ThePie, config: Dict[str, Any]):
        super().__init__(name=name,
                        initial_ddt=config['initial_ddt'],
                        initial_xdai=0)
        self.liquidity_pool = liquidity_pool
        self.the_pie = the_pie
        self.daily_spend = config['daily_spend']
    
    def receive_pie_share(self, amount: float):
        # Active users immediately sell their pie share
        xdai_received = self.liquidity_pool.sell_ddt(amount)
        if xdai_received > 0:
            self.xdai += xdai_received
            self.record_transaction('sell_pie_share', amount, xdai_received)
    
    async def step(self):
        # Only spend dDT if we have enough
        if self.ddt >= self.daily_spend:
            self.ddt -= self.daily_spend
            self.the_pie.receive_ddt(self.daily_spend, self.name)
            self.record_transaction('spend_ddt', self.daily_spend, 0)

class CasualUserAgent(BaseAutoAgent):
    def __init__(self, name: str, liquidity_pool: LiquidityPool, the_pie: ThePie, config: Dict[str, Any]):
        super().__init__(name=name,
                        initial_ddt=config['initial_ddt'],
                        initial_xdai=0)
        self.liquidity_pool = liquidity_pool
        self.the_pie = the_pie
        self.daily_spend = config['daily_spend']  # 0.1 dDT per day
    
    def receive_pie_share(self, amount: float):
        # Casual users immediately sell their pie share
        xdai_received = self.liquidity_pool.sell_ddt(amount)
        if xdai_received > 0:
            self.xdai += xdai_received
            self.record_transaction('sell_pie_share', amount, xdai_received)
    
    async def step(self):
        # First spend daily dDT for compute
        if self.ddt >= self.daily_spend:
            self.ddt -= self.daily_spend
            self.the_pie.receive_ddt(self.daily_spend, self.name)
            self.record_transaction('spend_ddt', self.daily_spend, 0)
            
            # Immediately sell excess dDT (0.9)
            excess_ddt = self.daily_spend * 9  # 0.9 = 0.1 * 9
            if self.ddt >= excess_ddt:
                xdai_received = self.liquidity_pool.sell_ddt(excess_ddt)
                if xdai_received > 0:
                    self.ddt -= excess_ddt
                    self.xdai += xdai_received
                    self.record_transaction('sell_excess_ddt', excess_ddt, xdai_received)

class DataDAOGroupChat:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.liquidity_pool = LiquidityPool(
            fee_rate=config['SIM_CONFIG']['fee_rate'],
            initial_ddt=0,  # Start with empty pool
            initial_xdai=0
        )
        self.the_pie = ThePie()
        self.agents = []
        
        # Entry configuration
        self.entry_steps = config['SIM_CONFIG']['entry_steps']
        self.agents_per_entry = config['SIM_CONFIG']['agents_per_entry']
        self.proportions = config['SIM_CONFIG']['proportions']
        
        # Track total agents by type
        self.total_agents = {
            'degen_user': 0,
            'organization': 0,
            'power_user': 0,
            'active_user': 0,
            'casual_user': 0
        }
        
        # Add initial agents based on config
        for agent_type, config in config['AGENT_CONFIGS'].items():
            if config['count'] > 0:
                self._add_agents(agent_type, config['count'])
        
        # Store simulation data
        self.price_history = []
        self.lp_ddt_reserve_history = []
        self.lp_xdai_reserve_history = []
        self.xdai_balances_history = {agent_type: [] for agent_type in self.total_agents.keys()}
        self.agents_history = {agent_type: [] for agent_type in self.total_agents.keys()}

    def _add_agents(self, agent_type: str, count: int):
        """Add specified number of agents of given type"""
        if count <= 0:
            return
            
        config = self.config['AGENT_CONFIGS'][agent_type]
        agent_classes = {
            'degen_user': DegenAgent,
            'organization': OrganizationAgent,
            'power_user': PowerUserAgent,
            'active_user': ActiveUserAgent,
            'casual_user': CasualUserAgent
        }
        
        for i in range(count):
            agent_class = agent_classes[agent_type]
            agent = agent_class(
                f"{agent_type}_{self.total_agents[agent_type]}",
                self.liquidity_pool,
                self.the_pie,
                config
            )
            self.agents.append(agent)
            self.total_agents[agent_type] += 1

    async def simulate(self, steps: int):
        """Run the simulation for specified number of steps"""
        for step in range(steps):
            print(f"Step {step + 1}/{steps}")
            
            # Add new agents every entry_steps
            if step % self.entry_steps == 0:
                # Calculate new total after adding agents_per_entry
                current_total = sum(self.total_agents.values())
                new_total = current_total + self.agents_per_entry
                
                # Calculate target numbers for each type
                targets = {
                    agent_type: round(new_total * prop)
                    for agent_type, prop in self.proportions.items()
                }
                
                # Add agents to reach targets
                for agent_type, target in targets.items():
                    to_add = max(0, target - self.total_agents[agent_type])
                    if to_add > 0:
                        self._add_agents(agent_type, to_add)
            
            # Execute step for each agent
            for agent in self.agents:
                await agent.step()
            
            # Distribute pie rewards every step
            self.the_pie.distribute_rewards(self.agents)
            
            # Store simulation data
            self.price_history.append(self.liquidity_pool.get_price())
            self.lp_ddt_reserve_history.append(self.liquidity_pool.ddt_reserve)
            self.lp_xdai_reserve_history.append(self.liquidity_pool.xdai_reserve)
            
            # Store average xDAI balances for each agent type
            for agent_type in self.total_agents.keys():
                agents_of_type = [agent for agent in self.agents if agent.name.startswith(agent_type)]
                if agents_of_type:
                    avg_xdai = sum(agent.xdai for agent in agents_of_type) / len(agents_of_type)
                    self.xdai_balances_history[agent_type].append(avg_xdai)
                else:
                    self.xdai_balances_history[agent_type].append(0)
            
            for agent_type in self.total_agents:
                self.agents_history[agent_type].append(self.total_agents[agent_type])
            
            # Print status every 10 steps
            if (step + 1) % 10 == 0:
                total = sum(self.total_agents.values())
                print(f"\nStep {step + 1} Summary:")
                print(f"Current token price: ${self.liquidity_pool.get_price():.2f}")
                
                print("\nAgent Distribution:")
                for agent_type, count in self.total_agents.items():
                    percentage = (count / total * 100) if total > 0 else 0
                    target_percentage = self.proportions[agent_type] * 100
                    diff = percentage - target_percentage
                    print(f"Active {agent_type}s: {count} ({percentage:.1f}% vs target {target_percentage:.1f}%, diff: {diff:+.1f}%)")
                
                # Print average xDAI holdings for each agent type
                print("\nAverage xDAI Holdings per Agent:")
                for agent_type in self.total_agents.keys():
                    agents_of_type = [agent for agent in self.agents if agent.name.startswith(agent_type)]
                    if agents_of_type:
                        avg_xdai = sum(agent.xdai for agent in agents_of_type) / len(agents_of_type)
                        print(f"{agent_type}: {avg_xdai:.2f} xDAI")
                    else:
                        print(f"{agent_type}: 0.00 xDAI")
                print("")

    def get_simulation_data(self) -> pd.DataFrame:
        data = {
            'price': self.price_history,
            'lp_dDT_reserve': self.lp_ddt_reserve_history,
            'lp_xDAI_reserve': self.lp_xdai_reserve_history,
        }
        # Add agent counts
        for agent_type in self.total_agents.keys():
            data[f'active_{agent_type}s'] = self.agents_history[agent_type]
            data[f'xdai_{agent_type}'] = self.xdai_balances_history[agent_type]
        
        return pd.DataFrame(data)

class LiquidityPool:
    def __init__(self, fee_rate: float, initial_ddt: float = 0, initial_xdai: float = 0):
        self.ddt_reserve = initial_ddt
        self.xdai_reserve = initial_xdai
        self.fee_rate = fee_rate
        self.total_fees = 0
        self.lp_shares = {}  # Track LP shares by provider
        self.fees_collected = {}  # Track collected fees by provider
        
    def get_price(self) -> float:
        if self.ddt_reserve == 0:
            return 1.0  # Default price when pool is empty
        return self.xdai_reserve / self.ddt_reserve
        
    def add_liquidity(self, ddt_amount: float, xdai_amount: float) -> float:
        """Add liquidity to the pool and return LP shares"""
        if self.ddt_reserve == 0:  # First liquidity provider
            shares = ddt_amount
        else:
            shares = ddt_amount * (self.get_total_shares() / self.ddt_reserve)
            
        self.ddt_reserve += ddt_amount
        self.xdai_reserve += xdai_amount
        
        provider = inspect.stack()[1].frame.f_locals.get('self').name
        self.lp_shares[provider] = self.lp_shares.get(provider, 0) + shares
        self.fees_collected[provider] = 0
        
        return shares
        
    def get_total_shares(self) -> float:
        return sum(self.lp_shares.values())
        
    def collect_fees(self, provider: str) -> float:
        """Collect accumulated fees for a liquidity provider"""
        if provider not in self.lp_shares:
            return 0
            
        provider_share = self.lp_shares[provider] / self.get_total_shares()
        fees = self.total_fees * provider_share
        self.fees_collected[provider] = self.fees_collected.get(provider, 0) + fees
        self.total_fees = 0
        return fees
        
    def buy_ddt(self, xdai_amount: float) -> float:
        """Buy dDT with xDAI using constant product formula"""
        if self.ddt_reserve == 0 or xdai_amount == 0:
            return 0
            
        # Calculate dDT received after fees
        fee = xdai_amount * self.fee_rate
        xdai_with_fee = xdai_amount - fee
        
        # Update reserves
        k = self.ddt_reserve * self.xdai_reserve
        new_xdai_reserve = self.xdai_reserve + xdai_with_fee
        new_ddt_reserve = k / new_xdai_reserve
        ddt_out = self.ddt_reserve - new_ddt_reserve
        
        self.ddt_reserve = new_ddt_reserve
        self.xdai_reserve = new_xdai_reserve
        self.total_fees += fee
        
        return ddt_out
        
    def sell_ddt(self, ddt_amount: float) -> float:
        """Sell dDT for xDAI using constant product formula"""
        if self.xdai_reserve == 0 or ddt_amount == 0:
            return 0
            
        # Calculate xDAI received after fees
        k = self.ddt_reserve * self.xdai_reserve
        new_ddt_reserve = self.ddt_reserve + ddt_amount
        new_xdai_reserve = k / new_ddt_reserve
        xdai_out = self.xdai_reserve - new_xdai_reserve
        
        # Apply fee
        fee = xdai_out * self.fee_rate
        xdai_out -= fee
        
        self.ddt_reserve = new_ddt_reserve
        self.xdai_reserve = new_xdai_reserve
        self.total_fees += fee
        
        return xdai_out
