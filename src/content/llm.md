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

## Single vs Multi‑Agent Architecture

A single LLM can handle many tasks on its own, integrating memory, web search and tools within a linear workflow. However, a **multi‑agent** architecture decomposes a complex problem into specialised roles. An orchestrator coordinates agents – each with its own instructions, LLM and tool access – to perform summarisation, research, verification, development, validation and deployment in parallel. Collaboration and competition among agents improves overall performance and reduces hallucination by cross‑checking results. Key benefits of multi‑agent systems include autonomy, decentralisation, scalability and adaptability.

![Single vs multi‑agent architecture](images/agent_architecture.png)
*Figure: In a single‑agent setup (top), one model handles all reasoning and retrieval. In a multi‑agent network (bottom), an orchestrator coordinates multiple agents with dedicated tasks and shared data stores. Source: AI Prep deck.*