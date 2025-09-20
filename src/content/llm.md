---
title: "How LLMs & AI Agents Think"
tagline: "Demystifying probabilistic models, emergent behavior and multi‑agent systems"
description: "Understanding how large language models work and how AI agent networks process information and make decisions."
---

## How Large Language Models Work

Large language models (LLMs) do not "think" like humans. Instead, they use *probabilistic modeling* to predict the most likely next word (token) given the words that came before. During training, an LLM observes billions of text snippets and learns statistical patterns in grammar, syntax, semantics and context. At inference time the model uses these patterns to generate coherent sentences by sampling from a probability distribution over possible continuations. Because LLMs are trained on a diverse corpus, they can adapt to new prompts by drawing on related examples.

Adding extra context – such as a document or search results – changes the probability landscape. With retrieval‑augmented generation (RAG), a vector store stores relevant knowledge and the model uses semantic search to fetch supporting documents. This retrieved context is appended to the prompt, enabling the LLM to answer questions more accurately and cite sources. Emergent abilities, such as reasoning and summarisation, arise when models scale up in size and data; behaviours not present in smaller models suddenly appear at larger scales. Conversely, two agents built from the same base model can behave quite differently if they have distinct training data, personas or memory priorities, a phenomenon sometimes called *divergent minds*.

![Illustration of how LLMs think and how this will change](images/how_llms.png)
*Figure: Visualising decision trees with and without additional context illustrates how retrieval‑augmented models re‑rank possible continuations. Source: AI Prep deck.*

## AI Agent Architectures: From Monolithic to Distributed Systems

Understanding how AI scales requires examining the evolution from single-agent to multi-agent architectures—a fundamental shift in how we design intelligent systems. Think of this evolution like the difference between a Swiss Army knife and a specialized toolbox: one tool trying to do everything versus multiple specialized tools working together.

### Single-Agent Architecture: The Digital Swiss Army Knife

Imagine an AI agent as a highly capable assistant working alone in a library. This monolithic AI agent operates as a unified system where one Large Language Model (LLM) handles all cognitive tasks within a single execution context—reading, analyzing, reasoning, and responding sequentially.

![Single AI Agent Architecture](images/ai_agent.png)
*Figure: A single AI agent manages all tasks through one LLM core. Like a skilled librarian working alone, it maintains memory, accesses information, and uses tools—but everything happens in sequence, creating bottlenecks when complexity increases.*

**Key Characteristics:**

- **Linear Processing**: Tasks are handled one after another, like reading a book from start to finish
- **Centralized Memory**: All information flows through one context window
- **Tool Integration**: One agent learns to use all available tools and data sources
- **Simplicity**: Easier to design, debug, and understand—but limited by single-threaded thinking

### Multi-Agent Orchestration: The Specialized Research Team

Now imagine transforming that lone librarian into an entire research department. Multi-agent architectures represent a paradigm shift toward distributed AI systems—like having a research director coordinating multiple specialists, each expert in their domain.

![Multi-Agent Orchestration](images/ai_agents.png)
*Figure: Multiple specialized AI agents work in parallel under an orchestrator's guidance. Like a research team where experts in different fields collaborate simultaneously, each agent has dedicated LLMs, memory systems, and tool access—enabling parallel processing and specialized expertise.*

**How This Changes Everything:**

- **Parallel Thinking**: Multiple agents can work simultaneously on different aspects of complex problems
- **Domain Expertise**: Instead of one generalist, you have specialists (a research agent, analysis agent, verification agent, synthesis agent)
- **Scalable Intelligence**: Add new agents for new capabilities without rebuilding the entire system

### Why Multi-Agent Systems Matter: The Technical Revolution

The shift from single-agent to multi-agent systems isn't just about adding more AI—it's about fundamentally changing how intelligent systems work. Here's why this matters for the future:

**Parallel Processing: From Sequential to Simultaneous**
Unlike sequential single-agent workflows, orchestrated systems enable true parallelization of cognitive tasks. Imagine the difference between one person solving a complex research problem step-by-step versus a team of experts working simultaneously on different aspects. This dramatically improves both throughput and response times.

**Specialization & Expertise: The Expert Advantage**
Each agent can be fine-tuned for specific domains (research, analysis, verification, synthesis) rather than requiring one generalist model to handle all tasks. Just as you wouldn't want a general practitioner performing brain surgery, specialized AI agents perform better in their domains than generalist models.

**Fault Tolerance & Redundancy: Built-in Backup Systems**
Distributed systems provide natural redundancy—if one agent fails or produces unreliable output, others can compensate or provide verification. This is like having multiple experts review important decisions, significantly reducing the risk of critical errors.

**Resource Optimization: Right-sized Intelligence**
Different agents can utilize different model sizes and computational resources based on task complexity, optimizing cost and performance. Simple tasks use lightweight models, complex reasoning uses powerful models—like having both calculators and supercomputers available as needed.

**Cross-Verification: The Wisdom of AI Crowds**
Multiple agents can independently process the same problem, enabling consensus mechanisms that reduce hallucination and improve accuracy through **ensemble inference**. When multiple AI experts agree on a conclusion, confidence in the result increases dramatically.

This architectural evolution mirrors the broader software industry's shift from monolithic applications to microservices—enabling AI systems to achieve unprecedented scale, reliability, and capability through distributed intelligence. The future of AI isn't about building one superintelligent agent, but about orchestrating networks of specialized agents that can tackle problems no single system could handle alone.