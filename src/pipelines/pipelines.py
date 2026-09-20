from src.agents.agents import build_search_agent, build_reader_agent, writer_chain, critic_chain

def run_research_pipeline(topic : str) -> dict:

    state={}

    #Step 1: Search Agent
    print("\n"+"="*50+"\n")
    print("Step 1: Search Agent is working...")
    print("\n"+"="*50+"\n")

    search_agent=build_search_agent()
    search_results=search_agent.invoke({
        "messages" : [("user", f"Search for information on {topic}")]
    })
    state["search_results"]=search_results['messages'][-1].content

    print("\nsearch results: ", state["search_results"])

    #Step 2: Reader Agent
    print("\n"+"="*50+"\n")
    print("Step 2: Reader Agent is scraping top resources...")
    print("\n"+"="*50+"\n")

    reader_agent=build_reader_agent()
    reader_results=reader_agent.invoke({
        "messages" : [("user",
                       f"Based on the search results, scrape the top resources and extract relevant information for the topic: {topic},"
                       f"pick the most relevant information and summarize it in a concise manner.\n\n"
                       f"Search Results: {state['search_results'][:8000]}"
                       )]
    })
    state["scraped_content"]=reader_results['messages'][-1].content

    #Step 3: Writer Chain
    print("\nScraped content: \n", state['scraped_content'])

    print("\n"+"="*50+"\n")
    print("Step 3: Writer Chain is generating the research report...")
    print("\n"+"="*50+"\n")

    reseach_combined=(
        f"SEARCH RESULTS:\n{state['search_results']}\n\n"
        f"DETAILED SCRAPED CONTENT:\n{state['scraped_content']}"
    )
    state["research_report"]=writer_chain.invoke({
        "topic": topic,
        "research": reseach_combined
    })

    print("\nResearch Report: \n", state['research_report'])

    #Step 4: Critic Chain
    print("\n"+"="*50+"\n")
    print("Step 4: Critic Chain is evaluating the research report...")
    print("\n"+"="*50+"\n")

    state["report_evaluation"]=critic_chain.invoke({
        "report": state["research_report"]
    })

    print("\nReport Evaluation: \n", state['report_evaluation'])

    return state
