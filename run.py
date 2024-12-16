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
    plt.title('Token Price Over Time')
    plt.xlabel('Step')
    plt.ylabel('Price ($)')
    
    # LP Token Reserve over time
    plt.subplot(2, 2, 2)
    plt.plot(sim_data['lp_token_reserve'])
    plt.title('LP Token Reserve Over Time')
    plt.xlabel('Step')
    plt.ylabel('Tokens')
    
    # LP Dollar Reserve over time
    plt.subplot(2, 2, 3)
    plt.plot(sim_data['lp_dollar_reserve'])
    plt.title('LP Dollar Reserve Over Time')
    plt.xlabel('Step')
    plt.ylabel('Dollars ($)')
    
    # The Pie tokens over time
    plt.subplot(2, 2, 4)
    plt.plot(sim_data['the_pie_tokens'])
    plt.title('The Pie Tokens Over Time')
    plt.xlabel('Step')
    plt.ylabel('Tokens')
    
    plt.tight_layout()
    plt.savefig('simulation_results.png')
    plt.close()
    
    # Save transaction data
    agent_data.to_csv('transaction_history.csv', index=False)
    sim_data.to_csv('simulation_data.csv', index=False)

if __name__ == "__main__":
    asyncio.run(main())
