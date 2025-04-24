import json
from dotenv import load_dotenv
from agent import Agent
load_dotenv()


# Define the contest flow
def contest(agent1: Agent, agent2: Agent, question: str):
    # QA phase
    print("\n"+"-"*10+"<< Q&A >>"+"-"*10)
    print(f"\033[4mQuestion:\033[0m {question}\n")
    qa_response1 = agent1.chat(question)
    print(f"\033[4mAgent 1: {agent1.llm_name}\033[0m\n{qa_response1}\n")

    qa_response2 = agent2.chat(question)
    print(f"\033[4mAgent 2: {agent2.llm_name}\033[0m\n{qa_response2}\n")

    # Evaluation phase
    print("-"*10+"<< Evaluations >>"+"-"*10)
    print(f"\033[4mEvaluation from Agent 1 to Agent 2:\033[0m")
    eval_response1 = agent1.chat("Evaluate this response: "+qa_response2)
    try:
        eval_response1 = json.loads(eval_response1)
        agent2_scored = eval_response1.get("score", "N/A")
        print(f"Score: {agent2_scored}\n")
        print(f"Explanation: {eval_response1.get('explanation', 'N/A')}")
    except json.JSONDecodeError:
        print("Invalid JSON!")

    print(f"\n\033[4mEvaluation from Agent 2 to Agent 1:\033[0m")
    eval_response2 = agent2.chat("Evaluate this response: "+qa_response1)
    try:
        eval_response2 = json.loads(eval_response2)
        agent1_scored = eval_response2.get("score", "N/A")
        print(f"Score: {agent1_scored}\n")
        print(f"Explanation: {eval_response2.get('explanation', 'N/A')}")
    except json.JSONDecodeError:
        print("Invalid JSON!")
    
    # Comparsion phase
    print("\n"+"-"*10+"<< Final Result >>"+"-"*10)
    if agent2_scored > agent1_scored:
        print(f"\033[4mAgent 2 provided a better answer (score: {agent2_scored}):\033[0m\n{qa_response2}\n")
    elif agent1_scored > agent2_scored:
        print(f"\033[4mAgent 1 provided a better answer (score: {agent1_scored}):\033[0m\n{qa_response1}\n")
    elif agent2_scored == agent1_scored:
        print(f"Tie!\nAgent 1 scored {agent1_scored}, Agent 2 scored {agent2_scored}\n")


if __name__ == "__main__":
    try:
        first_agent_name = input("Assign the first agent (model name): ")
        second_agent_name = input("Assign the second agent (model name): ")
        question = input("Question to Agents: ")
    except:
        raise("Invalid Input")

    # Generate AI agents and initialze them
    agent1 = Agent(first_agent_name, 100)
    agent2 = Agent(second_agent_name, 101)

    # Start the competition
    contest(agent1, agent2, question)