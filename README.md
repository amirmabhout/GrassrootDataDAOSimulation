# GrassrootDataDAO Simulation

## What is a Grassroot dataDAO?

A grassroots dataDAO enables a group of individuals to pool data from the same verifiable source, and tokenize compute access to this shared data pool. Members contribute data and, based on their data's Contribution Weight—a function of the data's quality and quantity—are permitted to lock any amount of their personal Circles tokens ($CRC), up to a maximum proportional to that weight. In return for locking their tokens, they mint dataDAO tokens (also known as Group tokens in the Circles protocol), which grant them access to run computations on the dataDAO's data pool.

When members use dataDAO tokens to access computations as part of services, these tokens are stored in a smart contract called The Pie. The Pie accumulates the spent tokens, and dataDAO members can claim their share of the pie.

### Key Terms
- **Data Pool**: The collection of datasets contributed by all dataDAO members.
- **Contribution Weight**: A calculated value representing each member's data contribution, factoring in both the quality (confidence, credibility, etc) and quantity (amount in Kb, knowledge triplets, etc) of the data provided.
- **The Pie**: A smart contract that stores dataDAO tokens spent on computing services using the Data Pool.
- **dataDAO Tokens $dDT**: Issued to members when they lock their personal $CRC, up to a maximum proportional to their Contribution Weight. These tokens grant compute access to the Data Pool.

![image](https://github.com/user-attachments/assets/e759dc56-83a1-4e9c-a42d-7967f5560a2b)



### Data Ownership, Privacy and Governance
To ensure data ownership, access control, and privacy, it is up to the dataDAO operators to choose the appropriate technologies and protocols best suited for the AI services running on the data pool. These setups can gradually be governed by the dataDAO members, allowing for collaborative decision-making. Each member should be able to provide granular access control, specifying use cases where they permit or restrict their data from being included in computation services or being removed altogether from the data pool.

## Project Overview

This project simulates a grassroot dataDAO ecosystem where individuals contribute data to a shared pool and receive data tokens in return. The simulation models the complex interactions between different types of participants stakeholders.

The simulation explores how these different motivations and behaviors impact the token economy, particularly focusing on:
- Price discovery through market interactions
- Balance between token minting (data contribution) and token spending (compute usage)

### Agent Types

- **Degen Users**: Data contributors focused on quick returns. They contribute data to mint $dDT which they typically sell in the market to cash out. A small portion (10%) of these users also provide liquidity to the pool, benefiting from trading fees while waiting for optimal exit prices. These users rarely use the actual compute services.

- **Organizations**: Large entities (like AI companies or research institutions) with significant capital who purchase $dDT solely to access the dataDAO's compute services. They represent the primary demand side of the ecosystem, regularly buying $dDT from the market for service usage.

- **Power Users**: Active participants who use the dataDAO's services more than they contribute data. While they do contribute data and mint $dDT, their compute usage exceeds their minted amount, requiring them to regularly purchase additional $dDT from the market.

- **Active Users**: Regular participants who consistently contribute data and use compute services, representing the core user base of the dataDAO. They maintain a balanced approach between contribution and usage.

- **Casual Users**: Occasional participants who contribute minimal data, mint $dDT, and might later sell their $dDT in the market. They show irregular patterns of engagement with the ecosystem.

## Simulation Components

### Key Metrics Tracked

The simulation monitors several key indicators of ecosystem health:

- **Token Price Dynamics**: Shows the market's valuation of compute access to the data pool in xDAI
- **Liquidity Pool Reserves**: Tracks the availability of dDT and xDAI for trading
- **The Pie Accumulation**: Measures the growth of the ecosystem fund from compute service usage
- **Agent Interactions**: Records all dDT transactions, liquidity provisions, and compute service usage

## Getting Started

### Prerequisites

- Python 3.x
- Required packages (install via pip):
  ```bash
  pip install -r requirements.txt
  ```

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/grassrootDataDAO.git
   cd grassrootDataDAO
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp env.example .env
   ```
   Edit `.env` file to customize simulation parameters if desired.

### Running the Simulation

Run the simulation with:
```bash
python run.py
```

The simulation will generate:
- `simulation_results.png`: Visualization of key metrics
- `simulation_data.csv`: Time series data of simulation metrics
- `transaction_history.csv`: Detailed record of agent transactions

## Configuration

The simulation is highly configurable through environment variables. Key parameters include:

### Simulation Settings
- `INITIAL_POOL_TOKENS`: Initial liquidity pool token amount
- `INITIAL_POOL_DOLLARS`: Initial liquidity pool dollar amount
- `TOTAL_STEPS`: Number of simulation steps
- `STEPS_BEFORE_ORGS`: When organizations enter the ecosystem
- `FEE_RATE`: Liquidity provider fee rate
- `DEGEN_ENTRY_PRICE`: Price threshold for new degen entry
- `MAX_DEGENS`: Maximum number of degen agents

### Agent Settings
Each agent type (Degen, Org, Power User, etc.) has configurable parameters for:
- Initial token and dollar amounts
- Daily transaction rates
- Reinvestment rates
- Population counts

See `env.example` for all available configuration options.

## Results Interpretation

The simulation generates four key plots:
1. Token Price Over Time
2. LP Token Reserve Over Time
3. LP Dollar Reserve Over Time
4. The Pie Tokens Over Time

These metrics help understand:
- Price stability and trends
- Liquidity depth and changes
- Ecosystem fund growth
- Overall system health

## Contributing

Contributions are welcome! Feel free to:
- Fork the repository
- Create a feature branch
- Submit a Pull Request

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Built with PyAutoGen for agent simulation
