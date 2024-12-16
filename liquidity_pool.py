class LiquidityPool:
    def __init__(self, initial_tokens: float, initial_dollars: float, fee_rate: float = 0.003):
        self.token_reserve = initial_tokens
        self.dollar_reserve = initial_dollars
        self.total_lp_tokens = 0
        self.fee_rate = fee_rate
        self.total_fees = 0
        
    def get_price(self) -> float:
        if self.token_reserve == 0:
            return 1.0
        return self.dollar_reserve / self.token_reserve
    
    def get_total_liquidity(self) -> float:
        return self.dollar_reserve * 2
    
    def add_liquidity(self, tokens: float, dollars: float) -> float:
        if self.total_lp_tokens == 0:
            lp_tokens = (tokens * dollars) ** 0.5
            self.total_lp_tokens = lp_tokens
        else:
            token_ratio = tokens / self.token_reserve
            dollar_ratio = dollars / self.dollar_reserve
            ratio = min(token_ratio, dollar_ratio)
            lp_tokens = ratio * self.total_lp_tokens
            
        self.token_reserve += tokens
        self.dollar_reserve += dollars
        return lp_tokens
    
    def remove_liquidity(self, lp_tokens: float) -> tuple[float, float]:
        ratio = lp_tokens / self.total_lp_tokens
        tokens_out = self.token_reserve * ratio
        dollars_out = self.dollar_reserve * ratio
        
        self.token_reserve -= tokens_out
        self.dollar_reserve -= dollars_out
        self.total_lp_tokens -= lp_tokens
        
        return tokens_out, dollars_out
    
    def buy_tokens(self, dollars_in: float) -> float:
        if dollars_in <= 0 or self.token_reserve == 0:
            return 0
            
        fee = dollars_in * self.fee_rate
        dollars_in_with_fee = dollars_in - fee
        self.total_fees += fee
        
        # Calculate tokens out using constant product formula
        tokens_out = self.token_reserve * (1 - (self.dollar_reserve / (self.dollar_reserve + dollars_in_with_fee)))
        
        self.token_reserve -= tokens_out
        self.dollar_reserve += dollars_in
        
        return tokens_out
    
    def sell_tokens(self, tokens_in: float) -> float:
        if tokens_in <= 0:
            return 0
            
        # Calculate dollars out using constant product formula
        dollars_out = self.dollar_reserve * (1 - (self.token_reserve / (self.token_reserve + tokens_in)))
        fee = dollars_out * self.fee_rate
        dollars_out_with_fee = dollars_out - fee
        self.total_fees += fee
        
        self.token_reserve += tokens_in
        self.dollar_reserve -= dollars_out
        
        return dollars_out_with_fee
    
    def get_fees_earned(self, lp_tokens: float) -> float:
        """Calculate fees earned by a specific LP token holder"""
        if self.total_lp_tokens == 0:
            return 0
        return (lp_tokens / self.total_lp_tokens) * self.total_fees
