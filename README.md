# Ray Tracing-Based LoRaWAN Gateway Placement for Reliable Connectivity in Amazonian Regions
Network planning is an important task in wireless communications, as it helps network operators avoid unnecessary costs. In the context of the internet of things, using long-range wide-area network technologies in the Amazon rainforest, a key challenge is ensuring reliable communication between end-devices and gateways (GWs). In this sense, this reliability is strongly affected by channel conditions. Thus, during the planning phase, choosing the appropriate channel model is an important decision for accurate simulations. Given this
motivation, in this work, we propose an optimization model to evaluate the impact of different types of channels on coverage and packet delivery ratio in a forest scenario. We used channels
from ray tracing, empirical, and stochastic approaches to assess how decisions made during the network planning phase, in terms of the channel used, affect GW placement and, specifically,
the percentage of end-devices covered and the reliability of the communication system. Our results show that GW placement based on site-independent channels can overestimate the number
of gateways required to meet the network requirements, whereas using site-specific channels allows us to satisfy the same requirements with fewer GWs.
 
## Compiling ns-3 LoRaWAN
The first step to use our framework, is compiling the ns-3 LoRaWAN module. You can follow the steps defined in this [link](https://github.com/signetlabdei/lorawan) to do this. 

## :writing_hand: Installing the Python environment for optimization
Afte compile the ns-3 module, you need to configure python environment for Sionna RT. To do so, you need to execute the following command to install the conda environment

```bash
conda env create -f environemnt.yml
```


## Generating stochastic or emprical channel using ns3-LoRaWAN
To generate stochastic or empirical channel models, you should move the source code `lorawan_general_energy_simulation.cc` to the `ns-3-dev/scratch`. After that in the ns-3-dev/scratch folder, you should run the following command:

```bash
./ns3 run scratch/lorawan_general_energy_simulation.cc -- --spreadingFactor=7 --channelType=cost --scenario=forest
```

The available flags are:
- `--spreadingFactor`: The number of spreading factor, vary between [7, 12].
- `--channelType`: Type of channel to used. The options are log-distance, Okumura-Hata, COST-231, Nakagami, two ray, 3gpp-UMa, WI (x3D), WI (Full 3D), Sionna. To use one of these channel you should use the following options: `log`, `okumura`, `cost`, `nakagami` `twoRay`, `threegpp`, `rural`, `wix`, `wif`, `sionna`.
- `--simulationTime`: Time of the simulation.
- `--scenario`: Type of grid organization used. The availabe options are: `etoile`, `forest`, and `canyon`.

## :gear Gateway placement optimization
In order to perform a gateway placement optimization, with a fixed threshold you can use the following command:

```python
python3 gateway_positioning -c okumura -t -120
```

In this case, an optimization process will running with a scenario with Okumura-Hata channel and a power threshold of -120 dBm. Furthermore, the following flags can use to change the behavior of the optimization:

`--channel`: Type of channel can be `okumura`, `cost`, `rural`, `log`, `wif`, `wix`.

`--threshold`: Power threshold in dBm.

If you would like to perform an optimization using an interval of power threshold, you can use the following command:

```python
python3 multi_rho_gateway_positions -c cost --max-rho -80 --min-rho -150
```

In this case, the power threshold interval consider a minimum power of -150 dBm and maximum power of -80, with a COST-231 channel. Furthermore, the following flags can use to change the behavior of the optimization:

`--channel`: Type of channel can be `okumura`, `cost`, `rural`, `log`, `wif`, `wix`.

`--threshold`: Power threshold in dBm.

`--max-rho`: Maximum threshold power.

`--min-rho`: Minimum threshold power.

## :bar_chart: Result plots
`plot_position.py`: Plot the grid with each position obtained from the optimization model.

`plot_pdr.py`: Plot packet delivery ratio (PDR) bar char for different channel models.

`plot_time.py`: Plot bar chart related to the simulation time to obtain physical-level metrics for different channel models.

`plot_multi_threshold.py`: Plot line chart related to the number of gateways suggested for different received power thresholds.

`plot_ed_grid.py`: Plot the end-devices grid organization across different scenarios.

`plot_tradeoff.py`: Script to generate a scatter plot for depicting the relationship between the MSE of received power (considering WI received power as ground truth) and the simulation time.

`plot_receiver_power.py`: Script to plot the CDF of received power of all end-devices across different channel models.
