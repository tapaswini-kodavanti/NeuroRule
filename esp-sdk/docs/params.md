# JSON file

An ESP experiment is configured using an **experiment parameters** json file. Experiment parameters contain 3 main
 sections:
 
- Neural network parameters
- Evolution parameters
- LEAF parameters

# Neural Net parameters

Describe the topology of neural network candidates. Contains 3 sections:
- Inputs
- Hidden layers
- Outputs

## inputs

The list of input layers. Each input layer is described with the following attributes:

- **name**: unique name
- **size**: number of units (neurons)
- **values**: `[float]` if the values are number. The list of categorical values, in order, if the input corresponds
 to a one hot vector encoding categorical data. In that case the size of the list must match the `size` parameter of
 the layer.

## hidden_layers

The list of hidden layers. Each hidden layer is described with the following attributes:

- **layer_name**: unique name
- **layer_type**: Keras layer type. Only `Dense` is supported.
- **layer_params**: Keras layer parameters. For `Dense` layers:
    - units: number of units (neurons)
    - activation: [Keras activation function name](https://keras.io/activations/)
    - use_bias: `true` to use bias nodes, `false` otherwise

## outputs

The list of output layers. Each output layer is described with the following attributes:

- **name**: unique name
- **size**: number of units (neurons)
- **values**: `[float]` if the values are number. The list of categorical values, in order, if the output corresponds
 to a one hot vector encoding categorical data. In that case the size of the list must match the `size` parameter of
 the layer.
- **activation**: [Keras activation function name](https://keras.io/activations/)
- **use_bias**: `true` to use bias nodes, `false` otherwise

## Example

```json
{
    "network": {
        "inputs": [
            {
                "name": "Observations",
                "size": 8,
                "values": [
                    "float"
                ]
            }
        ],
         "hidden_layers": [
            {"layer_name": "hidden_1",
             "layer_type": "Dense",
             "layer_params": {
                 "units": 128,
                 "activation": "tanh",
                 "use_bias": true
                 }
             }
        ],
        "outputs": [
            {
                "name": "Action",
                "size": 4,
                "activation": "softmax",
                "use_bias": true,
                "values": [
                    "Do nothing",
                    "Fire left orientation engine",
                    "Fire main engine",
                    "Fire right orientation engine"
                ]
            }
        ]
    }
}
```

# Evolution parameters

The evolution parameters control how new generations of **candidates** are evolved. A candidate corresponds to a
 **Prescriptor**, i.e. a neural network that takes **context** inputs and outputs **actions**.

## nb_generations

Specifies for how many generations evolution should run. The training process stops once the last generation has
 been evaluated

## population_size

Specifies the number of candidates per generation.

## nb_elites

Specifies the number of candidates that are directly copied over to the next generation. They are the best
 performing ones, so they are called "elites". Elites are used to keep some interesting genetic material from one
 generation to another, as otherwise there is no guarantee the offspring of a generation performs better that its
  parents. 

A nb_elites of 0 means **no** candidate is carried over to the next generation.  

## parent_selection

Specifies how parents are selected for a given evaluated generation. Possible values:

- **tournament** (default): Tournament Selection with replacement. The 2 parents can be the same, effectively allowing
 cloning.
        Selects 2 individuals from the passed list. Compares them and keeps the one with the highest fitness.
        Selects 2 individuals again from the same list. Compares them and keeps the one with the highest fitness.
- **tournament_distinct**: Tournament Selection. Returns 2 distinct individuals.
        Selects 4 individuals from the passed list. Compare them 2 by 2, and return the ones
        with the highest fitness.
- **proportion**: Selects 2 individuals from the passed list using a probability based on
        their fitness. The higher the fitness of a candidate, the higher its
        chances of being selected.  
        For instance, with a population of 5 candidates with the following
        fitnesses: 3, 2, 2, 2, 1:  
        The sum of the fitnesses is 10.  
        Candidate 1 has 3/10 chances of being selected for reproduction  
        Candidate 2 has 2/10 chances  
        Candidate 5 has 1/10 chances  
        ONLY works for non zero, all positive or all negative fitnesses.

## fitness
Specifies which metrics should be used as fitness for parent selection. This is a list with only 1 entry for single
 objective optimization, or more entries for multi-objectives. Each entry is a dictionary with the following keys:

- **metric_name**: the name of the metric to use
- **maximize**: `true` if a higher value is better than a lower one. `false` to minimize, i.e a smaller value is
 better than a big one.
- **target** (optional): the target the optimization should reach ideally. Used only for plotting (displays a target
 line in the objective plot) and for early stopping.

## remove_population_pct
Specifies the natural selection threshold, as a percentage of the population. 0.8 means 80% of the population
 is discarded when creating a new population, and only the remaining 20% are used as parents. 0.8 is a good default
 value. A higher value means a quicker convergence towards the most fit candidates, which means diversity will
  disappear quickly in a few generations. A lower value means less natural selection pressure and more diversity. 

## crossover
Specifies how to combine 2 parent candidates into a new 'child' candidate. Can be a single choice or a list. If
 it's a list, one item of the list will be chosen randomly. Choices:

- **uniform_weight** (default): creates a new set of weights from the parents weights, uniformly choosing each
  weight from either parent. Adds the string `~CUW~` between the 2 parent ids to the `origin` of the candidate.
- **k_points**: **Note**: specify `k`, as an integer. Creates a new set of model weights from the parents weights.
    The genetic material is cut in n-points and crossed over. For instance `3_points` means the genetic material of
     each parent is cut in 3 places and the child's genetic material comes alternatively from each parent for each
      segment. See [k-point crossover](https://en.wikipedia.org/wiki/Crossover_(genetic_algorithm)#Two-point_and_k-point_crossover).
      Adds the string `~CkPW~` between the 2 parent ids to the `origin` of the candidate.
- **clone_daddy**: creates a clone of the first parent only. Useful to effectively disable crossover and rely only
 on mutations. Adds the string `~CCD~` between the 2 parent ids to the `origin` of the candidate.

## mutation_probability

The probability for each individual weight of a candidate to be mutated.

## mutation_type
Specifies what kind of mutation is applied when mutations occur for a candidate. Mutations
 apply at the weight level. Can be a single choice or a list. If it's a list, one item of the list will be chosen
  randomly when applying mutations. Choices:
 
- **gaussian_noise_percentage** (default): adds a percentage of the weight to the weight. The percentage is chosen
 from a normal distribution centered on 0 with standard deviation = mutation_factor param. Adds the string `#MGNP` to
  the `origin` of the candidate
- **gaussian_noise_fixed**: adds a fixed amount of Gaussian noise to the weight. The noise is chosen from a normal
 distribution centered on 0 with standard deviation = mutation_factor param. Adds the string `#MGNF` to the
  `origin` of the candidate
- **uniform_reset**: uniformly re-initializes the weight to a new random weight. Adds the string `#MUR` to the
  `origin` of the candidate.
- **none**: doesn't change the weights

## mutation_factor

The parameter to use when applying mutations according to `mutation_type`.

## initialization_distribution

Specifies how to initialize the weights for the random candidates of the first generation. Choices:

- **orthogonal** (default): uses an orthogonal matrix to initialize the weights of the input layers, and a normal
 distribution centered on 0, standard deviation 1 for the output layers 
- **uniform**: randomly draws weights from a uniform distribution between `-initialization_range` and
 `+initialization_range`
- **normal**: randomly draws weights from a normal distribution centered on 0 with standard deviation
 = `initialization_range`
- **cauchy**: randomly draws weights from a cauchy distribution

## initialization_range

The parameter to use for weights initialization distributions.

## Example
```json
{
    "evolution": {
        "nb_generations": 500,
        "population_size": 100,
        "nb_elites": 5,
        "parent_selection": "tournament",
        "fitness" : [
            { "metric_name": "margin", "maximize": true },
            { "metric_name": "volume", "maximize": true }
        ],
        "remove_population_pct": 0.8,
        "mutation_type": "gaussian_noise_percentage",
        "mutation_probability": 0.1,
        "mutation_factor": 0.1,
        "initialization_distribution": "orthogonal",
        "initialization_range": 1
    }
}
```

# LEAF parameters

## esp_host
Specifies the URL or ip address of the ESP service

## esp_port
Specifies the port of the ESP service

## representation
Specifies the type of representation to use for the genetic material of the candidates. Corresponds to the
 bytes that are exchanged between the ESP SDK an the ESP service. Choices:

- **NNWeights** (default): (faster) a candidate is represented by a list of weights and biases for each layer of the
 neural network described in the `network` section of the experiment parameters. A single instance of a Keras `Model
 ` object is created, and its weights are updated before each candidate evaluation.
- **KerasNN**: (slower) a candidate is the serialized bytes of a Keras `Model` neural network object. 
- **RuleSet**: (future) a candidate is a set of rules (not supported yet).

## experiment_id
Specifies the name to use for this experiment. A folder with this named will be created in the `persistence_dir`
folder, and a new timestamp folder will be created in it each time the experiment is run. Also used for checkpoint
 ids. 

## reevaluate_elites
`true` if elites should be re-evaluated each time, `false`  if their fitness can be kept from one
 generation to another. Set to `false` if candidate evaluation is deterministic to speed up evaluation.

## version
Not used

## persistence_dir
Name of the folder to use to persist experiment results.

## candidates_to_persist
Specifies which candidates should be persisted to the `persistence_dir` folder for each generation. Choices:

- **best** (default): persists only the best candidate
- **elites**: persist the "elite" candidates
- **all**: persist all candidates
- **none**: do not persist any candidate
- **pareto**: persist each candidate on the pareto front (for multi-objective experiments only)

## Example

```json
{
    "LEAF": {
        "esp_host": "v1.esp.evolution.ml",
        "esp_port": 50051,
        "representation": "NNWeights",
        "experiment_id":"My_first_ESP_experiment",
        "reevaluate_elites": false,
        "version": "0.0.1",
        "persistence_dir": "trained_agents/",
        "candidates_to_persist": "best"
    }
}
```
