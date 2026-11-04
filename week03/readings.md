# Week 3 readings: sources and notes

## Required

### Kasparov, “The Chess Master and the Computer”

Garry Kasparov, “The Chess Master and the Computer,” *The New York Review of Books*, February 11, 2010. [Read the article](https://www.nybooks.com/articles/2010/02/11/the-chess-master-and-the-computer/).

**One line for Lab 03:** Code runs the seven SEC steps and the four roles in a fixed order; the Strategy Manager model names a failing part, and code sends that part to its role for at most one repair.

Kasparov’s account of advanced chess and the 2005 freestyle tournament makes process design central: people can improve results by coordinating human judgment with machine calculation. The useful lesson for this desk is to make the handoffs and checks clear, not to treat a model call as the whole process.

### CrewAI Flows, first page

Official documentation: [CrewAI Flows](https://docs.crewai.com/en/concepts/flows) and [CrewAI LLM configuration](https://docs.crewai.com/en/concepts/llms). This project uses CrewAI's Flow and `Process.sequential`. The current package requires Python below 3.14, so the project uses an isolated Python 3.13 environment.

**Choice:** CrewAI, the framework used in Francis & Zhang. The Flow fixes application-level order; `Process.sequential` runs each role crew's task in order. Python 3.13 is used because current CrewAI does not support the installed Python 3.14 interpreter.

## Optional

### Anthropic, “Building effective agents”

Anthropic, “Building effective agents” (2024). [Read the article](https://www.anthropic.com/research/building-effective-agents).

**One line:** The Strategy Manager follows the orchestrator-workers pattern; the Verifier follows the evaluator-optimizer pattern because it checks a completed result after generation.

### Francis & Zhang (2026), Section 3.1

Francis, A., & Zhang, C. X. (2026). “Can AI match professional analysts? Evidence from a multi-agent system.” *Finance Research Letters*, 103, 110127. [Publisher record](https://doi.org/10.1016/j.frl.2026.110127).

**One line:** A coordinating manager chooses which specialist to call next, when to call it, and what context to send; the graph makes those choices in code before the run starts.

## Copyright and source files

The article and publisher papers remain at their official source. This repository stores the citations and original study notes above. It does not redistribute full articles or paywalled papers.
