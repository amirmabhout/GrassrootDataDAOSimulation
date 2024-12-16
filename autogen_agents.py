import autogen
from typing import Dict, Any, List
from liquidity_pool import LiquidityPool
import pandas as pd

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
    
    def receive_ddt(self, amount: float, from_agent: str):
        self.total_ddt += amount
        self.transactions.append({
            'from': from_agent,
            'amount': amount,
            'total_after': self.total_ddt
        })

class DegenAgent(BaseAutoAgent):
    def __init__(self, name: str, liquidity_pool: LiquidityPool, config: Dict[str, Any]):
        super().__init__(name=name, 
                        initial_ddt=config['initial_ddt'],
                        initial_xdai=config['initial_xdai'])
        self.liquidity_pool = liquidity_pool
        self.lp_ddt = 0
        self.has_provided_liquidity = False
        self.has_dumped_ddt = False
        self.reinvest_rate = config['reinvest_rate']
        self.fees_earned = 0
        
        # Provide initial liquidity with 10% of dDT
        initial_liq = config['initial_liquidity']
        self.lp_ddt = self.liquidity_pool.add_liquidity(initial_liq, initial_liq)
        self.ddt -= initial_liq
        self.xdai -= initial_liq
        self.record_transaction('provide_liquidity', initial_liq, initial_liq)
        self.has_provided_liquidity = True
    
    async def step(self):
        current_price = self.liquidity_pool.get_price()
        
        # Calculate fees earned since last step
        new_fees = self.liquidity_pool.get_fees_earned(self.lp_ddt) - self.fees_earned
        self.fees_earned += new_fees
        
        # Reinvest portion of fees into liquidity
        if new_fees > 0:
            reinvest_amount = new_fees * self.reinvest_rate
            if reinvest_amount > 0:
                ddt_to_add = reinvest_amount / current_price
                if self.ddt >= ddt_to_add and self.xdai >= reinvest_amount:
                    new_lp_ddt = self.liquidity_pool.add_liquidity(ddt_to_add, reinvest_amount)
                    self.lp_ddt += new_lp_ddt
                    self.ddt -= ddt_to_add
                    self.xdai -= reinvest_amount
                    self.record_transaction('reinvest_fees', ddt_to_add, reinvest_amount)
        
        # Dump remaining dDT if haven't done so yet
        if not self.has_dumped_ddt and self.ddt > 0:
            ddt_to_sell = self.ddt  # Sell all remaining dDT
            xdai_received = self.liquidity_pool.sell_ddt(ddt_to_sell)
            if xdai_received > 0:
                self.ddt = 0  # All dDT sold
                self.xdai += xdai_received
                self.record_transaction('dump_ddt', ddt_to_sell, xdai_received)
                self.has_dumped_ddt = True

class OrganizationAgent(BaseAutoAgent):
    def __init__(self, name: str, liquidity_pool: LiquidityPool, the_pie: ThePie, config: Dict[str, Any]):
        super().__init__(name=name,
                        initial_ddt=config['initial_ddt'],
                        initial_xdai=config['initial_xdai'])
        self.liquidity_pool = liquidity_pool
        self.the_pie = the_pie
        self.daily_ddt_buy = config['daily_ddt_buy']
    
    async def step(self):
        # Organizations always try to buy their daily amount
        current_price = self.liquidity_pool.get_price()
        xdai_needed = self.daily_ddt_buy * current_price
        
        if self.xdai >= xdai_needed:
            ddt_received = self.liquidity_pool.buy_ddt(xdai_needed)
            if ddt_received > 0:
                self.xdai -= xdai_needed
                self.ddt += ddt_received
                self.record_transaction('buy', ddt_received, xdai_needed)
                
                # Immediately spend the dDT
                self.the_pie.receive_ddt(ddt_received, self.name)
                self.ddt -= ddt_received
                self.record_transaction('spend_to_pie', ddt_received, 0)

class PowerUserAgent(BaseAutoAgent):
    def __init__(self, name: str, liquidity_pool: LiquidityPool, the_pie: ThePie, config: Dict[str, Any]):
        super().__init__(name=name,
                        initial_ddt=config['initial_ddt'],
                        initial_xdai=config['initial_xdai'])
        self.liquidity_pool = liquidity_pool
        self.the_pie = the_pie
        self.daily_spend = config['daily_spend']
    
    async def step(self):
        # Try to spend dDT if available
        if self.ddt >= self.daily_spend:
            self.ddt -= self.daily_spend
            self.the_pie.receive_ddt(self.daily_spend, self.name)
            self.record_transaction('spend_to_pie', self.daily_spend, 0)
        # If we don't have enough dDT, try to buy some
        elif self.ddt < self.daily_spend:
            current_price = self.liquidity_pool.get_price()
            xdai_needed = self.daily_spend * current_price
            
            if self.xdai >= xdai_needed:
                ddt_received = self.liquidity_pool.buy_ddt(xdai_needed)
                if ddt_received > 0:
                    self.xdai -= xdai_needed
                    self.ddt += ddt_received
                    self.record_transaction('buy', ddt_received, xdai_needed)
                    
                    # Now try to spend
                    if self.ddt >= self.daily_spend:
                        self.ddt -= self.daily_spend
                        self.the_pie.receive_ddt(self.daily_spend, self.name)
                        self.record_transaction('spend_to_pie', self.daily_spend, 0)

class ActiveUserAgent(BaseAutoAgent):
    def __init__(self, name: str, liquidity_pool: LiquidityPool, the_pie: ThePie, config: Dict[str, Any]):
        super().__init__(name=name,
                        initial_ddt=config['initial_ddt'],
                        initial_xdai=config['initial_xdai'])
        self.liquidity_pool = liquidity_pool
        self.the_pie = the_pie
        self.daily_spend = config['daily_spend']
    
    async def step(self):
        # Simply spend dDT if available
        if self.ddt >= self.daily_spend:
            self.ddt -= self.daily_spend
            self.the_pie.receive_ddt(self.daily_spend, self.name)
            self.record_transaction('spend_to_pie', self.daily_spend, 0)

class CasualUserAgent(BaseAutoAgent):
    def __init__(self, name: str, liquidity_pool: LiquidityPool, the_pie: ThePie, config: Dict[str, Any]):
        super().__init__(name=name,
                        initial_ddt=config['initial_ddt'],
                        initial_xdai=config['initial_xdai'])
        self.liquidity_pool = liquidity_pool
        self.the_pie = the_pie
        self.daily_spend = config['daily_spend']
        self.keep_ddt = config['keep_ddt']
    
    async def step(self):
        # First spend daily amount if available
        if self.ddt >= self.daily_spend:
            self.ddt -= self.daily_spend
            self.the_pie.receive_ddt(self.daily_spend, self.name)
            self.record_transaction('spend_to_pie', self.daily_spend, 0)
            
            # Then sell excess dDT if we have more than we want to keep
            if self.ddt > self.keep_ddt:
                ddt_to_sell = self.ddt - self.keep_ddt
                xdai_received = self.liquidity_pool.sell_ddt(ddt_to_sell)
                if xdai_received > 0:
                    self.ddt -= ddt_to_sell
                    self.xdai += xdai_received
                    self.record_transaction('sell_excess', ddt_to_sell, xdai_received)

class DataDAOGroupChat:
    def __init__(self, config: Dict[str, Any]):
        self.liquidity_pool = LiquidityPool(
            initial_ddt=config['SIM_CONFIG']['initial_pool_ddt'],
            initial_xdai=config['SIM_CONFIG']['initial_pool_xdai'],
            fee_rate=config['SIM_CONFIG']['fee_rate']
        )
        
        self.the_pie = ThePie()
        self.agents = []
        self.config = config
        self.degen_entry_price = config['SIM_CONFIG']['degen_entry_price']
        self.max_degens = config['SIM_CONFIG']['max_degens']
        self.total_degens = config['AGENT_CONFIGS']['degen_user']['count']
        self._initialize_agents(config['AGENT_CONFIGS'])
        
        self.data = {
            'price': [],
            'lp_dDT_reserve': [],
            'lp_xDAI_reserve': [],
            'the_pie_dDT': [],
            'active_degens': []
        }
    
    def _initialize_agents(self, agent_configs: Dict[str, Any]):
        # Initialize degens first
        for i in range(agent_configs['degen_user']['count']):
            agent = DegenAgent(
                f"Degen_{i}", 
                self.liquidity_pool, 
                agent_configs['degen_user']
            )
            self.agents.append(agent)
        
        # Initialize other agents
        agent_types = {
            'power_user': PowerUserAgent,
            'active_user': ActiveUserAgent,
            'casual_user': CasualUserAgent
        }
        
        for agent_type, agent_class in agent_types.items():
            config = agent_configs[agent_type]
            for i in range(config['count']):
                agent = agent_class(
                    f"{agent_type}_{i}",
                    self.liquidity_pool,
                    self.the_pie,
                    config
                )
                self.agents.append(agent)
    
    async def simulate(self, steps: int, steps_before_orgs: int):
        for step in range(steps):
            print(f"Step {step + 1}/{steps}")
            
            # Add orgs after specified steps
            if steps_before_orgs > 0 and step == steps_before_orgs:
                self._add_org_agents(self.config['AGENT_CONFIGS']['organization'])
            
            # Check price and add degens if needed
            current_price = self.liquidity_pool.get_price()
            if current_price >= self.degen_entry_price and self.total_degens < self.max_degens:
                new_degens = min(2, self.max_degens - self.total_degens)  # Add 2 at a time
                if new_degens > 0:
                    self._add_degen_agents(new_degens)
                    print(f"Price ${current_price:.2f} above threshold! Adding {new_degens} new Degen agents")
            
            # Step all agents
            for agent in self.agents:
                await agent.step()
            
            # Record data every 10 steps
            if (step + 1) % 10 == 0:
                self.data['price'].append(self.liquidity_pool.get_price())
                self.data['lp_dDT_reserve'].append(self.liquidity_pool.ddt_reserve)
                self.data['lp_xDAI_reserve'].append(self.liquidity_pool.xdai_reserve)
                self.data['the_pie_dDT'].append(self.the_pie.total_ddt)
                self.data['active_degens'].append(self.total_degens)
                
                print(f"Current token price: ${self.liquidity_pool.get_price():.2f}")
                print(f"The Pie dDT: {self.the_pie.total_ddt:.2f}")
                print(f"Active Degens: {self.total_degens}")
    
    def _add_degen_agents(self, count: int):
        for i in range(count):
            agent = DegenAgent(
                f"Degen_{self.total_degens + i}",
                self.liquidity_pool,
                self.config['AGENT_CONFIGS']['degen_user']
            )
            self.agents.append(agent)
        self.total_degens += count
    
    def _add_org_agents(self, config: Dict[str, Any]):
        for i in range(config['count']):
            agent = OrganizationAgent(
                f"Org_{i}",
                self.liquidity_pool,
                self.the_pie,
                config
            )
            self.agents.append(agent)
    
    def get_simulation_data(self) -> pd.DataFrame:
        return pd.DataFrame(self.data)
    
    def get_agent_data(self) -> pd.DataFrame:
        all_transactions = []
        for agent in self.agents:
            all_transactions.extend(agent.transaction_history)
        return pd.DataFrame(all_transactions)
