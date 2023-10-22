# Baroque - Quantum

BaroqueQuantum is a package for Qiskit developers that aims to streamline the development process by encapsulating complex or obscured Qiskit functionalities and by providing commonly used functions and string constants.

## Installation

BaroqueQuantum is not offered on PIP at the moment. Install into the project environment by hand.

## Usage
Welcome to Baroque!
Here's how you use it:
        Add Baroque to your global path for ease of use.
        Here's the generic outline of a Baroque command:

        Baroque -i [input_file] -c [compare_file] -o [output_file] -b [backend] -r [routing_algorithm] --<metric_test>

        Out of all the arguments there, only input file and backend are necessary.
        However, most arguments can have default values be specified.

Additional Commands:
        You can use any of these commands after the 'Baroque' keyword:
        --set_default_<something> <value>
                This is how you set default values.
                Where <something> is replaced by input_file, compare_file, output_file, backend, or routing.
        --show_defaults
                This will print all defaults you have set.
        --reset_all
                This will reset all default values you have set.
        --set_API_key <key>
                Use this to set the API key you will use for using IBMQ simulators and machines.

Available Metrics:
        --metricCountGate=<gate string>
                Count the occurrences of a specific gate.
        --metricDiffGate=<gate string>
                Find the difference in occurrences of a specific between two circuits.
        --metricDiffDepth
                Find the difference in depth between two circuits.
        --metricCircuitDepth
                Find the depth of the circuit.
        --metricRaw
                Display raw data about the simulation.

        (gate strings have been defined as per IBM standards)

Good luck :3


## Contributing

Baroque is currently not open source for development on the master branch. Feel free to edit on your own IDE environment. GitHub coming soon.

## Authors

Harrison Barnes - BaroqueQuantum
Lucas Romero - Updating Baroque
Sean Bonaventure - HERR.py

## License

[MIT](https://choosealicense.com/licenses/mit/)