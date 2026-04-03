"""Seed Qdrant with real AI papers (bypasses arxiv rate-limit)."""
import httpx

papers = [
    {
        "title": "ReAct: Synergizing Reasoning and Acting in Language Models",
        "abstract": "We explore the use of LLMs to generate both reasoning traces and task-specific actions in an interleaved manner, allowing for greater synergy between the two: reasoning traces help the model induce, track, and update action plans as well as handle exceptions, while actions allow it to interface with external sources such as knowledge bases or environments to gather additional information.",
        "url": "https://arxiv.org/abs/2210.03629",
        "published": "2022-10-06T00:00:00+00:00",
        "categories": ["cs.AI", "cs.LG"],
        "source": "arxiv",
        "authors": ["Shunyu Yao", "Jeffrey Zhao", "Dian Yu"],
    },
    {
        "title": "Toolformer: Language Models Can Teach Themselves to Use Tools",
        "abstract": "We introduce Toolformer, a model trained to decide which APIs to call, when to call them, what arguments to pass, and how to best incorporate the results into future token prediction. This is done in a self-supervised way, requiring nothing more than a handful of demonstrations for each API.",
        "url": "https://arxiv.org/abs/2302.04761",
        "published": "2023-02-09T00:00:00+00:00",
        "categories": ["cs.LG", "cs.AI"],
        "source": "arxiv",
        "authors": ["Timo Schick", "Jane Dwivedi-Yu"],
    },
    {
        "title": "AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation",
        "abstract": "AutoGen is an open-source framework for building LLM applications using multiple conversable agents that can collaborate to solve tasks. AutoGen agents are customizable, conversable, and can operate in various modes that employ combinations of LLMs, human inputs, and tools.",
        "url": "https://arxiv.org/abs/2308.08155",
        "published": "2023-08-16T00:00:00+00:00",
        "categories": ["cs.AI", "cs.MA"],
        "source": "arxiv",
        "authors": ["Qingyun Wu", "Gagan Bansal", "Jieyu Zhang"],
    },
    {
        "title": "LLM-Powered Autonomous Agents: A Survey",
        "abstract": "Large language model (LLM) based autonomous agents have shown remarkable capabilities in a wide range of tasks including planning, reasoning, and tool use. This survey presents a comprehensive review of the architectures, capabilities, and applications of LLM-powered autonomous agents.",
        "url": "https://arxiv.org/abs/2308.11432",
        "published": "2023-08-22T00:00:00+00:00",
        "categories": ["cs.AI"],
        "source": "arxiv",
        "authors": ["Lei Wang", "Chen Ma", "Xueyang Feng"],
    },
    {
        "title": "CAMEL: Communicative Agents for Mind Exploration of Large Language Model Society",
        "abstract": "We explore the potential of building scalable techniques to facilitate autonomous cooperation among communicative agents and provide insight into their cognitive processes. To address challenges in autonomous cooperation, we propose a role-playing framework.",
        "url": "https://arxiv.org/abs/2303.17760",
        "published": "2023-03-31T00:00:00+00:00",
        "categories": ["cs.AI", "cs.MA"],
        "source": "arxiv",
        "authors": ["Guohao Li", "Hasan Abed Al Kader Hammoud"],
    },
    {
        "title": "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks",
        "abstract": "We explore a general-purpose fine-tuning recipe for retrieval-augmented generation (RAG) models which combine pre-trained parametric and non-parametric memory for language generation. Our RAG models retrieve documents with a dense retrieval approach, then generate with a seq2seq model.",
        "url": "https://arxiv.org/abs/2005.11401v1",
        "published": "2020-05-22T00:00:00+00:00",
        "categories": ["cs.CL", "cs.AI"],
        "source": "arxiv",
        "authors": ["Patrick Lewis", "Ethan Perez", "Aleksandra Piktus"],
    },
    {
        "title": "Generative Agents: Interactive Simulacra of Human Behavior",
        "abstract": "We introduce generative agents, computational software agents that simulate believable human behavior. We describe an architecture that extends a large language model to store a complete record of the agent experience using natural language, to synthesize those memories over time into higher-level reflections.",
        "url": "https://arxiv.org/abs/2304.03442",
        "published": "2023-04-07T00:00:00+00:00",
        "categories": ["cs.AI", "cs.HC"],
        "source": "arxiv",
        "authors": ["Joon Sung Park", "Joseph C. OBrien", "Carrie J. Cai"],
    },
    {
        "title": "HuggingGPT: Solving AI Tasks with ChatGPT and its Friends in HuggingFace",
        "abstract": "We introduce HuggingGPT, a system that connects ChatGPT with the machine learning community to solve AI tasks. Using ChatGPT as a controller to manage existing AI models, HuggingGPT can tackle tasks across different modalities and domains.",
        "url": "https://arxiv.org/abs/2303.17580",
        "published": "2023-03-30T00:00:00+00:00",
        "categories": ["cs.AI", "cs.CL"],
        "source": "arxiv",
        "authors": ["Yongliang Shen", "Kaitao Song", "Xu Tan"],
    },
    {
        "title": "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models",
        "abstract": "We explore how generating a chain of thought, a series of intermediate reasoning steps, significantly improves the ability of large language models to perform complex reasoning. This simple method is universally applicable to any sufficiently large LLM.",
        "url": "https://arxiv.org/abs/2201.11903",
        "published": "2022-01-28T00:00:00+00:00",
        "categories": ["cs.AI", "cs.CL"],
        "source": "arxiv",
        "authors": ["Jason Wei", "Xuezhi Wang", "Dale Schuurmans"],
    },
    {
        "title": "TaskBench: Benchmarking Large Language Models for Task Automation",
        "abstract": "We introduce TaskBench to evaluate the capability of LLMs for task automation including tool use and multi-step reasoning. We construct task graphs to represent the decomposition of complex tasks and evaluate LLMs on their ability to invoke tools and chain them correctly.",
        "url": "https://arxiv.org/abs/2311.18760",
        "published": "2023-11-30T00:00:00+00:00",
        "categories": ["cs.AI", "cs.CL"],
        "source": "arxiv",
        "authors": ["Yuren Mao", "Xuemei Dong", "Xuan Feng"],
    },
    {
        "title": "AgentBench: Evaluating LLMs as Agents",
        "abstract": "Large language models (LLMs) are becoming increasingly smart and autonomous, targeting real-world pragmatic decision making as agents. We present AgentBench, a multi-dimensional evolving benchmark to evaluate LLM-as-Agent across a diverse set of environments.",
        "url": "https://arxiv.org/abs/2308.03688",
        "published": "2023-08-07T00:00:00+00:00",
        "categories": ["cs.AI", "cs.LG"],
        "source": "arxiv",
        "authors": ["Xiao Liu", "Hao Yu", "Hanchen Zhang"],
    },
    {
        "title": "MetaGPT: Meta Programming for a Multi-Agent Collaborative Framework",
        "abstract": "We introduce MetaGPT, a meta-programming framework incorporating efficient human workflows into LLM-based multi-agent collaborations. MetaGPT encodes Standardized Operating Procedures (SOPs) into prompt sequences to coordinate with multiple agents and enable structured and structured outputs.",
        "url": "https://arxiv.org/abs/2308.00352",
        "published": "2023-08-01T00:00:00+00:00",
        "categories": ["cs.AI", "cs.MA", "cs.SE"],
        "source": "arxiv",
        "authors": ["Sirui Hong", "Mingchen Zhuge", "Jonathan Chen"],
    },
]

if __name__ == "__main__":
    ok, fail = 0, 0
    for p in papers:
        try:
            r = httpx.post("http://localhost:8000/ingest/single", json=p, timeout=30)
            r.raise_for_status()
            d = r.json()
            print(f"  OK  {d['id'][:12]}  {p['title'][:55]}")
            ok += 1
        except Exception as e:
            print(f"  ERR {p['title'][:40]}: {e}")
            fail += 1
    print(f"\nSeeded: {ok} OK / {fail} failed")
