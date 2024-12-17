import asyncio
import matplotlib.pyplot as plt
from autogen_agents import DataDAOGroupChat
from config import CONFIG

async def main():
    # Initialize the simulation
    sim = DataDAOGroupChat(CONFIG)
    
    # Run the simulation
    await sim.simulate(CONFIG['SIM_CONFIG']['total_steps'])
    
    # Get simulation data
    sim_data = sim.get_simulation_data()
    
    # Create figure with subplots
    plt.figure(figsize=(15, 10))
    
    # Price over time
    plt.subplot(2, 2, 1)
    plt.plot(sim_data['price'])
    plt.title('dDT Price Over Time')
    plt.xlabel('Step')
    plt.ylabel('Price (xDAI)')
    
    # LP Reserves over time
    plt.subplot(2, 2, 2)
    plt.plot(sim_data['lp_dDT_reserve'], label='dDT')
    plt.plot(sim_data['lp_xDAI_reserve'], label='xDAI')
    plt.title('LP Reserves Over Time')
    plt.xlabel('Step')
    plt.ylabel('Amount')
    plt.legend()
    
    # xDAI balances over time
    plt.subplot(2, 2, 3)
    agent_types = ['degen_user', 'organization', 'power_user', 'active_user', 'casual_user']
    for agent_type in agent_types:
        plt.plot(sim_data[f'xdai_{agent_type}'], label=agent_type)
    plt.title('Average xDAI Holdings per Agent Type')
    plt.xlabel('Step')
    plt.ylabel('xDAI per Agent')
    plt.legend()
    
    # Agent counts over time
    plt.subplot(2, 2, 4)
    for agent_type in agent_types:
        plt.plot(sim_data[f'active_{agent_type}s'], label=agent_type)
    plt.title('Agent Counts Over Time')
    plt.xlabel('Step')
    plt.ylabel('Count')
    plt.legend()
    
    plt.tight_layout()
    
    # Save the plot
    plt.savefig('simulation_results.png', dpi=300, bbox_inches='tight')
    
    # Display the plot
    plt.show()

if __name__ == "__main__":
    asyncio.run(main())
