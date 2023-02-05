# AudioNote
<img width="100%" alt="audionote_logo" src="https://user-images.githubusercontent.com/36128807/216830511-4a49ba77-9499-4fb7-80b5-434d3bfa0f90.jpg">

AudioNote is a powerful and efficient meeting assistant that transforms your words into actionable text. With its advanced speech-to-text technology, powered by facebook's wav2vec2, it accurately records and transcribes your meetings. Say goodbye to manual note-taking and hello to effortless and accurate meeting summaries with AudioNote.

## Table of Contents
- [AudioNote](#audionote)
  - [Table of Contents](#table-of-contents)
  - [Known Issues](#known-issues)
  - [Installation](#installation)
    - [Prerequisites](#prerequisites)
    - [Instructions](#instructions)
  - [Usage](#usage)
  - [Deactivating the Virtual Environment](#deactivating-the-virtual-environment)
  - [Contribution guidelines](#contribution-guidelines)
  - [License](#license)

## Known Issues
Currently, the recording only works through microphone input and not system audio.

This project is currently in a development stage and may contain bugs. 
Feedback and contributions are welcome. However, keep in mind that the code may be subject to change.


## Installation
### Prerequisites
- Python 3.6 or higher
- Pip package manager [https://pip.pypa.io/en/stable/installing/](https://pip.pypa.io/en/stable/installing/)
It is recommended to use a virtual environment to install the required packages. If you are not familiar with virtual environments, you can read more about them [here](https://docs.python.org/3/library/venv.html).
### Instructions
1. Create a virtual environment:
```sh
python3 -m venv audionote
```

2. Activate the virtual environment:
```sh
source audionote/bin/activate
```

3. Upgrade pip:
```sh
pip install --upgrade pip
```

4. Install the required packages:
```sh
pip install -r requirements.txt
```

## Usage
To run the app:
```sh
python audionote.py
```

## Deactivating the Virtual Environment
To stop running the virtual environment:
```sh
deactivate
```

## Contribution guidelines
If you want to contribute to AudioNote, please note the following guidelines:
- Please make sure that your code is well documented and easy to understand.
- Please make sure that your code is well tested.
- Please make sure that your code is well formatted.

We use Github issues for tracking requests and bugs. Please see Github Discuss for general questions and discussion, and please direct specific questions to Stack Overflow.
The AudioNote project strives to abide by generally accepted best practices in open-source software development.

## License
AudioNote is licensed under the MIT License. See [LICENSE](LICENSE) for the full license text.
