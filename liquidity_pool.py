class LiquidityPool:
    def __init__(self, initial_ddt: float, initial_xdai: float, fee_rate: float = 0.003):
        self.ddt_reserve = initial_ddt
        self.xdai_reserve = initial_xdai
        self.total_lp_tokens = 0
        self.fee_rate = fee_rate
        self.total_fees = 0
        
    def get_price(self) -> float:
        if self.ddt_reserve == 0:
            return 1.0
        return self.xdai_reserve / self.ddt_reserve
    
    def get_total_liquidity(self) -> float:
        return self.xdai_reserve * 2
    
    def add_liquidity(self, ddt: float, xdai: float) -> float:
        if self.total_lp_tokens == 0:
            lp_tokens = (ddt * xdai) ** 0.5
            self.total_lp_tokens = lp_tokens
        else:
            ddt_ratio = ddt / self.ddt_reserve
            xdai_ratio = xdai / self.xdai_reserve
            ratio = min(ddt_ratio, xdai_ratio)
            lp_tokens = ratio * self.total_lp_tokens
            
        self.ddt_reserve += ddt
        self.xdai_reserve += xdai
        return lp_tokens
    
    def remove_liquidity(self, lp_tokens: float) -> tuple[float, float]:
        ratio = lp_tokens / self.total_lp_tokens
        ddt_out = self.ddt_reserve * ratio
        xdai_out = self.xdai_reserve * ratio
        
        self.ddt_reserve -= ddt_out
        self.xdai_reserve -= xdai_out
        self.total_lp_tokens -= lp_tokens
        
        return ddt_out, xdai_out
    
    def buy_ddt(self, xdai_in: float) -> float:
        if xdai_in <= 0 or self.ddt_reserve == 0:
            return 0
            
        fee = xdai_in * self.fee_rate
        xdai_in_with_fee = xdai_in - fee
        self.total_fees += fee
        
        # Calculate ddt out using constant product formula
        ddt_out = self.ddt_reserve * (1 - (self.xdai_reserve / (self.xdai_reserve + xdai_in_with_fee)))
        
        self.ddt_reserve -= ddt_out
        self.xdai_reserve += xdai_in
        
        return ddt_out
    
    def sell_ddt(self, ddt_in: float) -> float:
        if ddt_in <= 0:
            return 0
            
        # Calculate xdai out using constant product formula
        xdai_out = self.xdai_reserve * (1 - (self.ddt_reserve / (self.ddt_reserve + ddt_in)))
        
        fee = xdai_out * self.fee_rate
        xdai_out_with_fee = xdai_out - fee
        self.total_fees += fee
        
        self.ddt_reserve += ddt_in
        self.xdai_reserve -= xdai_out
        
        return xdai_out_with_fee
    
    def get_fees_earned(self, lp_tokens: float) -> float:
        """Calculate fees earned by a specific LP token holder"""
        if self.total_lp_tokens == 0:
            return 0
        return (lp_tokens / self.total_lp_tokens) * self.total_fees
