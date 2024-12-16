import autogen
from typing import Dict, Any, List
from liquidity_pool import LiquidityPool
import pandas as pd

class BaseAutoAgent:
    def __init__(self, name: str, initial_tokens: float, initial_dollars: float, **kwargs):
        self.name = name
        self.tokens = initial_tokens
        self.dollars = initial_dollars
        self.tokens_spent = 0
        self.transaction_history = []
    
    def record_transaction(self, action: str, tokens: float, dollars: float):
        self.transaction_history.append({
            'agent': self.name,
            'action': action,
            'tokens': tokens,
            'dollars': dollars,
            'tokens_balance': self.tokens,
            'dollars_balance': self.dollars
        })

class ThePie:
    """The Pie accumulates all spent tokens from the ecosystem"""
    def __init__(self):
        self.total_tokens = 0
        self.transactions = []
    
    def receive_tokens(self, amount: float, from_agent: str):
        self.total_tokens += amount
        self.transactions.append({
            'from': from_agent,
            'amount': amount,
            'total_after': self.total_tokens
        })

class DegenAgent(BaseAutoAgent):
    def __init__(self, name: str, liquidity_pool: LiquidityPool, config: Dict[str, Any]):
        super().__init__(name=name, 
                        initial_tokens=config['initial_tokens'],
                        initial_dollars=config['initial_dollars'])
        self.liquidity_pool = liquidity_pool
        self.lp_tokens = 0
        self.has_provided_liquidity = False
        self.has_dumped_tokens = False
        self.reinvest_rate = config['reinvest_rate']
        self.fees_earned = 0
        
        # Provide initial liquidity with 10% of tokens
        initial_liq = config['initial_liquidity']
        self.lp_tokens = self.liquidity_pool.add_liquidity(initial_liq, initial_liq)
        self.tokens -= initial_liq
        self.dollars -= initial_liq
        self.record_transaction('provide_liquidity', initial_liq, initial_liq)
        self.has_provided_liquidity = True
    
    async def step(self):
        current_price = self.liquidity_pool.get_price()
        
        # Calculate fees earned since last step
        new_fees = self.liquidity_pool.get_fees_earned(self.lp_tokens) - self.fees_earned
        self.fees_earned += new_fees
        
        # Reinvest portion of fees into liquidity
        if new_fees > 0:
            reinvest_amount = new_fees * self.reinvest_rate
            if reinvest_amount > 0:
                tokens_to_add = reinvest_amount / current_price
                if self.tokens >= tokens_to_add and self.dollars >= reinvest_amount:
                    new_lp_tokens = self.liquidity_pool.add_liquidity(tokens_to_add, reinvest_amount)
                    self.lp_tokens += new_lp_tokens
                    self.tokens -= tokens_to_add
                    self.dollars -= reinvest_amount
                    self.record_transaction('reinvest_fees', tokens_to_add, reinvest_amount)
        
        # Dump remaining tokens if haven't done so yet
        if not self.has_dumped_tokens and self.tokens > 0:
            tokens_to_sell = self.tokens  # Sell all remaining tokens
            dollars_received = self.liquidity_pool.sell_tokens(tokens_to_sell)
            if dollars_received > 0:
                self.tokens = 0  # All tokens sold
                self.dollars += dollars_received
                self.record_transaction('dump_tokens', tokens_to_sell, dollars_received)
                self.has_dumped_tokens = True

class OrgAgent(BaseAutoAgent):
    def __init__(self, name: str, liquidity_pool: LiquidityPool, the_pie: ThePie, config: Dict[str, Any]):
        super().__init__(name=name,
                        initial_tokens=config['initial_tokens'],
                        initial_dollars=config['initial_dollars'])
        self.liquidity_pool = liquidity_pool
        self.the_pie = the_pie
        self.daily_token_buy = config['daily_token_buy']
    
    async def step(self):
        # Organizations always try to buy their daily amount
        current_price = self.liquidity_pool.get_price()
        dollars_needed = self.daily_token_buy * current_price
        
        if self.dollars >= dollars_needed:
            tokens_received = self.liquidity_pool.buy_tokens(dollars_needed)
            if tokens_received > 0:
                self.dollars -= dollars_needed
                self.tokens += tokens_received
                self.record_transaction('buy', tokens_received, dollars_needed)
                
                # Immediately spend the tokens
                self.the_pie.receive_tokens(tokens_received, self.name)
                self.tokens -= tokens_received
                self.record_transaction('spend_to_pie', tokens_received, 0)

class MostActiveUserAgent(BaseAutoAgent):
    def __init__(self, name: str, liquidity_pool: LiquidityPool, the_pie: ThePie, config: Dict[str, Any]):
        super().__init__(name=name,
                        initial_tokens=config['initial_tokens'],
                        initial_dollars=config['initial_dollars'])
        self.liquidity_pool = liquidity_pool
        self.the_pie = the_pie
        self.daily_spend = config['daily_spend']
    
    async def step(self):
        # Simply spend tokens if available
        if self.tokens >= self.daily_spend:
            self.tokens -= self.daily_spend
            self.the_pie.receive_tokens(self.daily_spend, self.name)
            self.record_transaction('spend_to_pie', self.daily_spend, 0)

class LeastActiveUserAgent(BaseAutoAgent):
    def __init__(self, name: str, liquidity_pool: LiquidityPool, the_pie: ThePie, config: Dict[str, Any]):
        super().__init__(name=name,
                        initial_tokens=config['initial_tokens'],
                        initial_dollars=config['initial_dollars'])
        self.liquidity_pool = liquidity_pool
        self.the_pie = the_pie
        self.daily_spend = config['daily_spend']
        self.keep_tokens = config['keep_tokens']
    
    async def step(self):
        # First spend daily amount if available
        if self.tokens >= self.daily_spend:
            self.tokens -= self.daily_spend
            self.the_pie.receive_tokens(self.daily_spend, self.name)
            self.record_transaction('spend_to_pie', self.daily_spend, 0)
            
            # Then sell excess tokens if we have more than we want to keep
            if self.tokens > self.keep_tokens:
                tokens_to_sell = self.tokens - self.keep_tokens
                dollars_received = self.liquidity_pool.sell_tokens(tokens_to_sell)
                if dollars_received > 0:
                    self.tokens -= tokens_to_sell
                    self.dollars += dollars_received
                    self.record_transaction('sell_excess', tokens_to_sell, dollars_received)

class PowerUserAgent(BaseAutoAgent):
    def __init__(self, name: str, liquidity_pool: LiquidityPool, the_pie: ThePie, config: Dict[str, Any]):
        super().__init__(name=name,
                        initial_tokens=config['initial_tokens'],
                        initial_dollars=config['initial_dollars'])
        self.liquidity_pool = liquidity_pool
        self.the_pie = the_pie
        self.daily_spend = config['daily_spend']
    
    async def step(self):
        # Try to spend tokens if available
        if self.tokens >= self.daily_spend:
            self.tokens -= self.daily_spend
            self.the_pie.receive_tokens(self.daily_spend, self.name)
            self.record_transaction('spend_to_pie', self.daily_spend, 0)
        # If we don't have enough tokens, try to buy some
        elif self.tokens < self.daily_spend:
            current_price = self.liquidity_pool.get_price()
            dollars_needed = self.daily_spend * current_price
            
            if self.dollars >= dollars_needed:
                tokens_received = self.liquidity_pool.buy_tokens(dollars_needed)
                if tokens_received > 0:
                    self.dollars -= dollars_needed
                    self.tokens += tokens_received
                    self.record_transaction('buy', tokens_received, dollars_needed)
                    
                    # Now try to spend
                    if self.tokens >= self.daily_spend:
                        self.tokens -= self.daily_spend
                        self.the_pie.receive_tokens(self.daily_spend, self.name)
                        self.record_transaction('spend_to_pie', self.daily_spend, 0)

class DataDAOGroupChat:
    def __init__(self, config: Dict[str, Any]):
        self.liquidity_pool = LiquidityPool(
            initial_tokens=config['SIM_CONFIG']['initial_pool_tokens'],
            initial_dollars=config['SIM_CONFIG']['initial_pool_dollars'],
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
            'lp_token_reserve': [],
            'lp_dollar_reserve': [],
            'the_pie_tokens': [],
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
            'most_active_user': MostActiveUserAgent,
            'least_active_user': LeastActiveUserAgent
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
            if step == steps_before_orgs:
                self._add_org_agents(self.config['AGENT_CONFIGS']['org_agent'])
            
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
                self.data['lp_token_reserve'].append(self.liquidity_pool.token_reserve)
                self.data['lp_dollar_reserve'].append(self.liquidity_pool.dollar_reserve)
                self.data['the_pie_tokens'].append(self.the_pie.total_tokens)
                self.data['active_degens'].append(self.total_degens)
                
                print(f"Current token price: ${self.liquidity_pool.get_price():.2f}")
                print(f"The Pie tokens: {self.the_pie.total_tokens:.2f}")
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
            agent = OrgAgent(
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
