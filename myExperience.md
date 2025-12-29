# My Experience Working on this project

i was assigned 2 problems, A1.0 (this one) and B1.3 (calander mgmt system)
i selected A1.0 since i felt i could showcase my skillset better in this.

---
## Problem statement
we are given an image (of glasses), we have to pass the image to the llm and return a structured file (json) that contains attributes, confidece score and remarks by LLM on why such schore was provided

---

## Key Challenges
The hardest part of this project was not building the API or the UI, but controlling the behavior of a vision-enabled LLM.
Also, i could not run flagship models, as i did'nt have hardware
So i selected the smallest vision models and  went ahead with it.

WHY?? :
  
  - improving the results from smaller models will guarantee that when i use flagship models, performace WILL DEFINETLY be boosted.
  - Running smaller models is faster and cheaper 
  
Some of the major challenges were:
- Resource constraints (lack of proper hardware)
- Preventing hallucinated attributes or business interpretations (providing prompt and images often excede the model's context window)
- Handling ambiguous or partially visible visual cues gracefully (specially for smaller models, this was a major challenge)
- Managing slow inference times when using small, CPU-bound vision models (This is still a problem)
- Dealing with invalid image URLs, SSL issues, and timeouts

- DNS issues: I recently tried to change the DNS on my network from 8.8.8.8 -> another server on my network, failed in this project and now DNS lookups take too long

This required careful prompt design and aggressive schema validation.
---

## Important Technical Decisions
Several key decisions shaped the final system:

- **Schema-first design**: I defined strict Pydantic schemas upfront and validated all model outputs against them to ensure consistency.
- **Strong prompt constraints**: Prompts were written as rule-based instructions rather than descriptive requests to reduce variability.
- **Separation of concerns**: Image fetching, model inference, caching, API handling, and UI logic were all kept modular.
- **Caching via hashing**: I introduced URL-based hashing and Supabase-backed caching to avoid recomputation and improve latency.
- **Async backend**: FastAPI async endpoints were used to prevent blocking during long-running inference calls.

These decisions prioritized reliability and clarity over raw performance.

---

## Prolems
Due to limited local hardware, I used smaller vision-capable models (4B range), which introduced higher latency and uncertainty in outputs. Instead of optimizing aggressively for speed, I focused on output correctness, reproducibility, and clear failure handling.

GPU support inside Docker was not fully configured, which influenced deployment choices and runtime performance.


---

## What I Would Improve With More Time
Given more time and resources, I would:
- Implement true image-content hashing instead of URL hashing
- Add image input feature (rather than just image_urls)
- Add multi-image aggregation per product
- Improve confidence calibration and uncertainty scoring
- Optimize batch processing and parallel inference


