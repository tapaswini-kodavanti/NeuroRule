# NeuroRule: Rule-Based Neural Network Distillation

An automated, end-to-end framework to evolve explainable rule-set models from neural networks. 

This repository orchestrates the complete experimental pipeline: automatically handling input/output schema generation, dataset splitting, base model weight ingestion, synthetic data generation, and active JSON configuration construction.

---

## 🛠️ Installation & Environment Setup

To ensure exact package versions and dependencies are matched, set up the environment using Conda:

```bash
# 1. Clone the repository
git clone [https://github.com/tapaswini-kodavanti/neurorule.git](https://github.com/tapaswini-kodavanti/neurorule.git)
cd neurorule

# 2. Create the environment from the provided environment file
conda env create -f environment.yml

# 3. Activate the environment
conda activate neurorule
```

---

## 🚀 Quickstart

Run the orchestration script directly from the project root. The pipeline automatically ingests your data, sets up internal path namespaces, infers schema parameters, and boots the evolutionary search engine.

```bash
python run_neurorule.py \
  --dataset diabetes \
  --interval 0.80 \
  --data diabetes.csv \
  --target-names Diabetes_binary \
  --synthetic
```

---

## 📋 Command Line Interface Options

The `run_neurorule.py` entry point accepts the following arguments:

### Core Pipeline Flags

| Flag | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `--dataset` | `str` | **Yes** | Target namespace for folder organization (e.g., `diabetes`, `heart_disease`, `bc`). |
| `--interval` | `float` | **Yes** | Split threshold tier indicator (e.g., `0.80`, `0.95`). |
| `--synthetic` | `flag` | No | Enables generation and training using synthetic data extracted from the base model. |

### Path Options

| Flag | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `--data` | `str` | `None` | Path to raw or preprocessed dataset (`.csv`). |
| `--weights` | `str` | `None` | Path to custom pre-trained base model weights (`.pth`). If omitted, a dummy architecture will be automatically trained. |

### Domain Options

| Flag | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `--target-names` | `str ...` | `None` | Space-separated list of classification target labels (e.g., `--target-names Diabetes_binary` or `--target-names class_0 class_1 class_2`). |

---

## 🔄 Example Use Cases

### 1. Ingest Custom External Weights & Data
If you have your own pre-trained network weights and a dataset:

```bash
python run_neurorule.py \
  --dataset heart_disease \
  --interval 0.85 \
  --data ~/data/heart.csv \
  --weights ~/checkpoints/model_v1.pth \
  --target-names healthy diagnosed
```

### 2. Run Baseline Benchmark (Auto-Train Dummy Base Network)
If you do not provide weights, the pipeline automatically spins up a baseline dummy architecture, trains it, and caches the resulting weights:

```bash
python run_neurorule.py \
  --dataset bc \
  --interval 0.80 \
  --target-names malignant benign
```

---

## 📂 Output Locations

Once the pipeline execution finishes, you can locate all resulting rule structures and candidate models here:

```text
neurorule/
└── candidate-solutions/    # Candidate solutions and best-performing extracted rules
```

Runtime execution configs and dataset caches are stored under:
* **Generated Config:** `configs/nested/tmp_active_config.json`
* **Cached Data & Weights:** `data/{dataset}/datasets/{interval}/` and `data/{dataset}/models/{interval}/`

[Paper](https://apps.cs.utexas.edu/apps/tech-reports/208654)