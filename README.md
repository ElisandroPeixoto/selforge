# SELForge
![Logo SelForge](images/logo_selforge.jpg)

&#x20;&#x20;

## What is SEL Forge?

SEL Forge is a Python library designed for automated interventions in protection relays and other intelligent devices from Schweitzer Engineering Laboratories (SEL). It utilizes an Ethernet connection and the Telnet Protocol to access these devices, perform queries, and modify parameters.
The goal of SEL Forge is to provide the necessary tools for developing systems that automate tasks in SEL devices efficiently and reliably.

## Contents

- SEL 700 relays (SEL-751, SEL-751A, SEL-787)
    - Read parameters, logic equations, hardware data
    - Write settings in the relay
    - Test Data Base (Test DB)

## Documentation
A more comprehensive documentation is being developed and will be published soon.

<div style="border-left: 5px solid orange; padding: 10px; background-color: #2a2a2a; color: white;">
<strong>⚠️ Warning</strong><br>
<i>This project has no affiliation with Schweitzer Engineering Laboratories (SEL). Furthermore, this library has not been rigorously tested on all SEL devices across a wide range of versions and use cases. Any use of this project should be conducted in a controlled environment and with full responsibility.
This project aims to research and learn about the features it explores.</i>
</div>


## Installation

To install the library, use the following command:

```bash
pip install selforge
```

## How to use

Basic Usage of the Library

```python
from selforge import SEL700

# Use example

# Instance the relay
relay = SEL700('192.168.0.10')

# Read the relay firmware
print(relay.readfirmware())

# Read the relay part number
print(relay.partnumber())

# Read logic parameters
print(relay.read_wordbit('SHO L SV01'))

# Read binary value from the Target Table
print(relay.read_target_value('ENABLED'))

```

A huge documentation is under development

## Licence

This project is licensed under the MIT License.

## Contact Info

Developed by [Elisandro Peixoto](https://github.com/ElisandroPeixoto).
