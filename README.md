# SELForge
![Logo SelForge](images/logo_selforge.jpg)

&#x20;&#x20;

## What is SEL Forge?

SEL Forge is a Python library designed for automated interventions in protection relays and other intelligent devices from Schweitzer Engineering Laboratories (SEL). It utilizes Telnet to access these devices, perform queries, and modify parameters.
The goal of SEL Forge is to provide the necessary tools for developing systems that automate tasks in SEL devices efficiently and reliably.

## Contents

- SEL 700 relays (SEL-751, SEL-751A, SEL-787)


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

```

## Licence

This project is licensed under the MIT License.

## Autor

Developed by [Elisandro Peixoto](https://github.com/ElisandroPeixoto).
