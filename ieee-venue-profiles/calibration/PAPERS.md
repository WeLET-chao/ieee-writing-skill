# Venue profile calibration corpus

Index for **IEEE venue-profile calibration** — not the consumer manuscript `paper/literature/`.

Papers here are used to empirically tune `profiles/*.json` (five pillars). Do not mix with LDO/CAD project literature unless a paper is also cited in the manuscript.

## Workflow

1. Search: `../scripts/run_venue_calibration_search.py`
2. Download: `../scripts/download_venue_corpus.sh`
3. Analyze: `analyze-research-paper` → `literature/<slug>/analysis.md`
4. Extract: fill `literature/<slug>/venue_signals.json` (see `VENUE_SIGNAL_EXTRACT.md`)
5. Synthesize: `../scripts/synthesize_profile_signals.py`
6. Patch profiles: agent edits `profiles/<id>.json` from synthesis report

## Table

| Title | Authors | Year | Venue | Profile | Category | DOI | Analysis | PDF |
|-------|---------|------|-------|---------|----------|-----|----------|-----|
| EEsizer: LLM-Based AI Agent for Sizing of Analog and Mixed Signal Circuit | C. Liu, D. Chitnis | 2025 | IEEE TCAS-I | ieee-tcas-i-journal | venue-calibration,tcas-i-journal | 10.1109/tcsi.2025.3646359 | | [IEEE Xplore](https://ieeexplore.ieee.org/document/11318860) |
| Atelier: An Automated Analog Circuit Design Framework via Multiple Large Language Model-Based Agents | J. Shen, Z. Chen, J. Zhuang et al. | 2026 | IEEE TCAD | ieee-tcad-journal | venue-calibration,tcad-journal | 10.1109/TCAD.2025.3573228 | | [IEEE Xplore](https://ieeexplore.ieee.org/document/11012698) |
| AnaCraft: Duel-Play Probabilistic-Model-Based Reinforcement Learning for Sample-Efficient PVT-Robust Analog Circuit Sizing Optimization | M. Ahmadzadeh, J. Lappas, N. Wehn et al. | 2026 | IEEE TCAD | ieee-tcad-journal | venue-calibration,tcad-journal | 10.1109/TCAD.2025.3582175 | | [IEEE Xplore](https://ieeexplore.ieee.org/document/11063353) |
| VTSMOC: An Efficient Voronoi Tree Search Boosted Multiobjective Bayesian Optimization With Constraints for High-Dimensional Analog Circuit Synthesis | A. Zhao, R. Lyu, X. Zhao et al. | 2025 | IEEE TCAD | ieee-tcad-journal | venue-calibration,tcad-journal | 10.1109/TCAD.2024.3455932 | | [IEEE Xplore](https://ieeexplore.ieee.org/document/10667666) |
| Multiobjective Optimization for Common-Centroid Placement of Analog Transistors | S. Maji, H. Park, G. Hong et al. | 2025 | IEEE TCAD | ieee-tcad-journal | venue-calibration,tcad-journal | 10.1109/TCAD.2024.3520521 | | [IEEE Xplore](https://ieeexplore.ieee.org/document/10807298) |
| RoSE-Opt: Robust and Efficient Analog Circuit Parameter Optimization With Knowledge-Infused Reinforcement Learning | W. Cao, J. Gao, T. Ma et al. | 2025 | IEEE TCAD | ieee-tcad-journal | venue-calibration,tcad-journal | 10.1109/TCAD.2024.3435692 | | [IEEE Xplore](https://ieeexplore.ieee.org/document/10614385) |
| Multiagent Based Reinforcement Learning (MA-RL): An Automated Designer for Complex Analog Circuits | J. Bao, J. Zhang, Z. Huang et al. | 2024 | IEEE TCAD | ieee-tcad-journal | venue-calibration,tcad-journal | 10.1109/TCAD.2024.3398554 | | [IEEE Xplore](https://ieeexplore.ieee.org/document/10525204) |
| Low-Voltage CMOS Capacitor-Less LDOs: Bulk-Driven Versus Gate-Driven Comparative Study | Ó. Pereira-Rial, J. Carrillo, P. López | 2024 | IEEE TCAS-I | ieee-tcas-i-journal | venue-calibration,tcas-i-journal | 10.1109/tcsi.2024.3440842 | | [IEEE Xplore](https://ieeexplore.ieee.org/document/10638180) |
| Analysis of Shunt LDO With Physical Security to Power/EM Side-Channel Attacks | J. Yang, A. Ghosh, D. Das et al. | 2026 | IEEE TCAS-I | ieee-tcas-i-journal | venue-calibration,tcas-i-journal | 10.1109/tcsi.2026.3659934 | | [IEEE Xplore](https://ieeexplore.ieee.org/document/11381585) |
| Knowledge-Aided Automated Synthesis for Broadband Power Amplifier With Transformer-Coupled Resonators | Z. Huang, X. Li, Y. Li et al. | 2024 | IEEE TCAS-I | ieee-tcas-i-journal | venue-calibration,tcas-i-journal | 10.1109/tcsi.2024.3440636 | | [IEEE Xplore](https://ieeexplore.ieee.org/document/10636785) |
| Shallow Neural Network-Based Error Compensation of a Non-Linear SAR ADC Sampling Stage | M. Molendijk, R. van Veldhoven, A. Young et al. | 2026 | IEEE TCAS-I | ieee-tcas-i-journal | venue-calibration,tcas-i-journal | 10.1109/tcsi.2025.3645475 | | [IEEE Xplore](https://ieeexplore.ieee.org/document/11339226) |
| Compact Single-Ended Transceivers Demonstrating Flexible Generation of 1/N-Rate Receiver Front-Ends for Short-Reach Links | M. Lee, J. Cho, J. Choi et al. | 2024 | IEEE TCAS-I | ieee-tcas-i-journal | venue-calibration,tcas-i-journal | 10.1109/tcsi.2023.3332391 | | [IEEE Xplore](https://ieeexplore.ieee.org/document/10324471) |
| Probabilistic Compute-in-Memory Design for Efficient Markov Chain Monte Carlo Sampling | Y. Fu, D. Shi, A. Fan et al. | 2024 | IEEE TCAS-I | ieee-tcas-i-journal | venue-calibration,tcas-i-journal | 10.1109/tcsi.2023.3337529 | | [IEEE Xplore](https://ieeexplore.ieee.org/document/10347275) |
| Self-Compensating StrongARM Latch for High-Speed Energy-Efficient True Random Number Generators | X. Huang, M. Islam | 2026 | IEEE TCAS-I | ieee-tcas-i-journal | venue-calibration,tcas-i-journal | 10.1109/tcsi.2025.3643984 | | [IEEE Xplore](https://ieeexplore.ieee.org/document/11329127) |
| Second-Order Transimpedance Amplifiers in Mixer-First Receivers: Design for Optimum Blocker Tolerance | K. Shi, A. Abidi, H. Darabi | 2023 | IEEE TCAS-I | ieee-tcas-i-journal | venue-calibration,tcas-i-journal | 10.1109/tcsi.2023.3244925 | | [IEEE Xplore](https://ieeexplore.ieee.org/document/10065583) |
| (Invited Paper) AnaFlow: Agentic LLM-based Workflow for Reasoning-Driven Explainable and Sample-Efficient Analog Circuit Sizing | M. Ahmadzadeh, K. Chen, G. Gielen | 2025 | ICCAD | ieee-conference-short | venue-calibration,conference-short | 10.1109/iccad66269.2025.11240818 | | [IEEE Xplore](https://ieeexplore.ieee.org/document/11240818) |
| ADO-LLM: Analog Design Bayesian Optimization with In-Context Learning of Large Language Models | Y. Yin, Y. Wang, B. Xu et al. | 2024 | ICCAD | ieee-conference-short | venue-calibration,conference-short | 10.1145/3676536.3676816 | | [arXiv](https://arxiv.org/pdf/2406.18770) |
| PPAAS: PVT and Pareto Aware Analog Sizing via Goal-conditioned Reinforcement Learning | S. Kim, Z. Wang, S. Lee et al. | 2025 | ICCAD | ieee-conference-short | venue-calibration,conference-short | 10.1109/iccad66269.2025.11240795 | | [IEEE Xplore](https://ieeexplore.ieee.org/document/11240795) |
| AnalogXpert: Automating Analog Topology Synthesis by Incorporating Circuit Design Expertise into Large Language Models | H. Zhang, S. Sun, Y. Lin et al. | 2025 | ISEDA | ieee-conference-short | venue-calibration,conference-short | 10.1109/iseda65950.2025.11100627 | | [IEEE Xplore](https://ieeexplore.ieee.org/document/11100627) |
| Multi-Objective Optimization of Analog Circuits Using Reinforcement Learning | H. Taşkıran, E. Sağlıcan, E. Afacan | 2025 | SMACD | ieee-conference-short | venue-calibration,conference-short | 10.1109/smacd65553.2025.11092100 | | [IEEE Xplore](https://ieeexplore.ieee.org/document/11092100) |
| Advanced Analog Design Optimization: Comparison Between Reinforcement Learning and Heuristic Algorithms | M. Chevalier, S. Trochut, R. Guizzetti et al. | 2024 | SMACD | ieee-conference-short | venue-calibration,conference-short | 10.1109/smacd61181.2024.10745428 | | [IEEE Xplore](https://ieeexplore.ieee.org/document/10745428) |
| Design and Optimization of Low-Dropout Voltage Regulator Using Relational Graph Neural Network and Reinforcement Learning in Open-Source SKY130 Process | Z. Li, A. Carusone | 2023 | ICCAD | ieee-conference-short | venue-calibration,conference-short | 10.1109/iccad57390.2023.10323720 | | [IEEE Xplore](https://ieeexplore.ieee.org/document/10323720) |
| Reinforcement Learning for Analog Sizing Optimization | M. Chevalier, S. Trochut, R. Guizzetti et al. | 2023 | SMACD | ieee-conference-short | venue-calibration,conference-short | 10.1109/smacd58065.2023.10192204 | | [IEEE Xplore](https://ieeexplore.ieee.org/document/10192204) |
| Automated Design of Analog Circuits Using Reinforcement Learning | K. Settaluri, Z. Liu, R. Khurana et al. | 2022 | IEEE TCAD | ieee-tcad-journal | venue-calibration,tcad-journal | 10.1109/TCAD.2021.3120547 | | [IEEE Xplore](https://ieeexplore.ieee.org/document/9576505) |
| Analog Integrated Circuit Topology Synthesis With Deep Reinforcement Learning | Z. Zhao, L. Zhang | 2022 | IEEE TCAD | ieee-tcad-journal | venue-calibration,tcad-journal | 10.1109/TCAD.2022.3153437 | | [IEEE Xplore](https://ieeexplore.ieee.org/document/9718525) |
| Deep Reinforcement Learning for Analog Circuit Sizing | Z. Zhao, L. Zhang | 2020 | ISCAS | ieee-conference-short | venue-calibration,conference-short | 10.1109/iscas45731.2020.9181149 | | [IEEE Xplore](https://ieeexplore.ieee.org/document/9181149) |
<!-- Add new rows above this line (newest year first) -->
