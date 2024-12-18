# GrassrootDataDAO Simulation

## What is a Grassroot dataDAO?

A grassroots dataDAO enables a group of individuals to pool data from the same verifiable source, and tokenize compute access to this shared data pool. Members contribute data and, based on their data's Contribution Weight—a function of the data's quality and quantity—are permitted to lock any amount of their personal Circles tokens ($CRC), up to a maximum proportional to that weight. In return for locking their tokens, they mint dataDAO tokens (also known as Group tokens in the Circles protocol), which grant them access to run computations on the dataDAO's data pool.

When members use dataDAO tokens to access computations as part of services, these tokens are stored in a smart contract called The Pie. The Pie accumulates the spent tokens, and dataDAO members can claim their share of the pie.

### Key Terms
- **Data Pool**: The collection of datasets contributed by all dataDAO members.
- **Contribution Weight**: A calculated value representing each member's data contribution, factoring in both the quality (confidence, credibility, etc) and quantity (amount in Kb, knowledge triplets, etc) of the data provided.
- **The Pie**: A smart contract that stores dataDAO tokens spent on computing services using the Data Pool.
- **dataDAO Tokens $dDT**: Issued to members when they lock their personal $CRC, up to a maximum proportional to their Contribution Weight. These tokens grant compute access to the Data Pool.

![image](https://github.com/user-attachments/assets/9cce1c16-dea1-4486-8224-25b9f7743e05)



### Data Ownership, Privacy and Governance
To ensure data ownership, access control, and privacy, it is up to the dataDAO operators to choose the appropriate technologies and protocols best suited for the AI services running on the data pool. These setups can gradually be governed by the dataDAO members, allowing for collaborative decision-making. Each member should be able to provide granular access control, specifying use cases where they permit or restrict their data from being included in computation services or being removed altogether from the data pool.

## Project Overview

This project simulates a grassroot dataDAO ecosystem where individuals contribute data to a shared pool and receive data tokens in return. The simulation models the complex interactions between different types of participants stakeholders.

The simulation explores how these different motivations and behaviors impact the token economy, particularly focusing on:
- Price discovery through market interactions
- Balance between token minting (data contribution) and token spending (compute usage)

### Agent Types and Proportions

The simulation maintains specific proportions of different agent types throughout its runtime:

- **Degen Users (40%)**: Data contributors focused on quick returns. They initially provide liquidity (10 dDT, 10 xDAI) and immediately sell their remaining 90 dDT. They benefit from trading fees while providing liquidity to the ecosystem.

- **Organizations (5%)**: Large entities with significant capital (1000 xDAI initially) who purchase 2 dDT daily for compute services. They represent the primary demand side of the ecosystem.

- **Power Users (5%)**: Active participants who both contribute and heavily use services. They start with 100 dDT and 100 xDAI, and receive 40% of The Pie distribution which they keep for service usage rather than selling.

- **Active Users (30%)**: Regular participants who start with 100 dDT. They receive 40% of The Pie distribution which they immediately sell into the market as they don't need additional compute access.

- **Casual Users (20%)**: Occasional participants who start with 100 dDT. They spend 0.1 dDT daily and immediately sell the remaining 0.9 dDT. They receive 20% of The Pie distribution which they also sell immediately.

### The Pie Distribution

The Pie accumulates all spent dDT from compute service usage. Every simulation step:
- 70% of The Pie's accumulated dDT is distributed to stakeholders:
  - 40% to Power Users (who keep it for service usage)
  - 40% to Active Users (who sell it immediately)
  - 20% to Casual Users (who sell it immediately)
- 30% remains in The Pie for future governance decisions

### Agent Entry and Growth

New agents are added every 5 steps, with 10 agents per entry, maintaining the above proportions throughout the simulation. This creates a dynamic ecosystem that grows while preserving the intended stakeholder distribution.

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
- `TOTAL_STEPS`: Number of simulation steps (default: 2000)
- `ENTRY_STEPS`: Frequency of new agent entry (default: every 5 steps)
- `AGENTS_PER_ENTRY`: Number of agents added per entry (default: 10)
- `FEE_RATE`: Liquidity provider fee rate (default: 0.003)

### Agent Distribution
- Degen Users: 40% (Initial DDT: 100, Initial xDAI: 10)
- Organizations: 5% (Initial xDAI: 1000)
- Power Users: 5% (Initial DDT: 100, Initial xDAI: 100)
- Active Users: 30% (Initial DDT: 100)
- Casual Users: 20% (Initial DDT: 100)

Each agent type has specific behaviors and parameters that influence their interactions with the ecosystem.

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
