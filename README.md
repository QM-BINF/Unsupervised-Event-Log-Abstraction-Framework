Unsupervised-ELA-Framework
============================

## Introduction

This repository contains the source code, simulation models, and event logs for the **Unsupervised Event Log Abstraction** project as submitted to Information Systems (version 2023/11/10).

## Usage

To run the project, you will need to have Python installed. You can install Python from the Python website: https://www.python.org/downloads/.

Once you have Python installed, you can clone this repository to your local machine:

    git clone https://github.com/gregvanhoudt/Unsupervised-ELA-Framework.git

Once the repository is cloned, you can navigate to the root directory of the project and install the required dependencies:

pip install -r requirements.txt
To run the main app, you can use the following command:

python app.py
This will start the app in a new terminal window.

## Simulation Models

The simulation models for the [Project Name] project are located in the BPSim subfolder. These models can be used to simulate different scenarios and generate event logs.

To run a simulation, you can use the following command:

python BPSim/simulate.py [model_name]
This will generate an event log in the Logs/.gz subfolder. The event log will be compressed in .xes.gz format.

## Event Logs

The event logs for the [Project Name] project are located in the Logs/.gz subfolder. These logs can be used to analyze the behavior of the system and identify potential bottlenecks.

To unzip an event log, you can use the following command:

gunzip Logs/.gz/[event_log_name].xes.gz
This will create an unzipped event log in the Logs subfolder.

## Contributing

We welcome contributions to the [Project Name] project. If you have any suggestions or bug reports, please feel free to create a new issue on GitHub.

License

The [Project Name] project is licensed under the MIT License: https://choosealicense.com/licenses/mit/.


