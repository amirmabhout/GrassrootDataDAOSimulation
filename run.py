import asyncio
import matplotlib.pyplot as plt
from autogen_agents import DataDAOGroupChat
from config import CONFIG

async def main():
    # Initialize simulation
    dao_chat = DataDAOGroupChat(CONFIG)
    
    # Run simulation
    await dao_chat.simulate(
        steps=CONFIG['SIM_CONFIG']['total_steps'],
        steps_before_orgs=CONFIG['SIM_CONFIG']['steps_before_orgs']
    )
    
    # Get simulation data
    sim_data = dao_chat.get_simulation_data()
    agent_data = dao_chat.get_agent_data()
    
    # Plot results
    plt.figure(figsize=(12, 8))
    
    # Price over time
    plt.subplot(2, 2, 1)
    plt.plot(sim_data['price'])
    plt.title('dDT Price Over Time')
    plt.xlabel('Step')
    plt.ylabel('Price (xDAI)')
    
    # LP dDT Reserve over time
    plt.subplot(2, 2, 2)
    plt.plot(sim_data['lp_dDT_reserve'])
    plt.title('LP dDT Reserve Over Time')
    plt.xlabel('Step')
    plt.ylabel('dDT')
    
    # LP xDAI Reserve over time
    plt.subplot(2, 2, 3)
    plt.plot(sim_data['lp_xDAI_reserve'])
    plt.title('LP xDAI Reserve Over Time')
    plt.xlabel('Step')
    plt.ylabel('xDAI')
    
    # The Pie dDT over time
    plt.subplot(2, 2, 4)
    plt.plot(sim_data['the_pie_dDT'])
    plt.title('The Pie dDT Over Time')
    plt.xlabel('Step')
    plt.ylabel('dDT')
    
    plt.tight_layout()
    plt.savefig('simulation_results.png')
    plt.close()
    
    # Save transaction data
    agent_data.to_csv('transaction_history.csv', index=False)
    sim_data.to_csv('simulation_data.csv', index=False)

if __name__ == "__main__":
    asyncio.run(main())
