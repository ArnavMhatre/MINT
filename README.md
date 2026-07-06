# MINT: Machine Intelligence for the Nest Thermostat

![Project Poster](poster/IDPRO_Poster_Final.pdf)

## Project Overview
Most "smart" thermostats heavily rely on learning rigid user schedules while ignoring dynamic environmental factors like home insulation and system response times. This project introduces a data-driven approach that pairs **Machine Learning** with a **steady-state mathematical model** to optimize both user comfort and HVAC energy efficiency. 

By analyzing weather patterns and indoor sensor data, our system predicts comfort-aware, energy-optimal temperature setpoints.

---

## Features & Architecture
* **Mathematical Steady-State Model:** Incorporates physical system behavior, utilizing indoor air and wall temperatures to model real-time thermodynamic user comfort.
* **Random Forest ML Model:** Processes engineered features from raw sensor data to make high-accuracy comfort predictions and optimize temperature setpoints.

---

## Repository Structure
```text
├── datasets/
│   ├── collected/        # Raw data (e.g., April/March logs)
│   ├── downloaded/       # Weather & external temperature logs
│   └── made/             # Processed datasets (e.g., comfort labels)
├── deliverables/
│   └── image_b2569c.jpg  # Final presentation poster
├── images/               # Generated performance plots & figures
├── notebooks_rough/      # Experimental steady-state notebooks
├── Random_Forest_Model.ipynb  # Primary ML pipeline
└── our_steady_state_model.py  # Core thermodynamic equations