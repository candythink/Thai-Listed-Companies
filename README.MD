## UPDATE : 2024-10-08
# Thai Listed Companies JSON Data

## Overview
This repository contains a JSON file (`ListedCompanies.json`) that includes data on various listed companies. The data is structured and can be used for various purposes like data analysis, research, or educational projects.

## Data Format
The  JSON file is structured with key-value pairs representing different attributes of the listed companies.

## How to Use
You can use the data directly from this repository by fetching it through GitHub's raw content feature or by cloning the repository to your local machine.

Make sure you have Pandas installed in your Python environment. You can install it using pip if you don't have it already:
```bash
pip install pandas
```
```python
import pandas as pd

# URL to the raw JSON file on GitHub
json_file_path = 'https://raw.githubusercontent.com/candythink/Thai-Listed-Companies/main/ThaiListedCompanies.json'

# Read the JSON Lines file into a pandas DataFrame
df = pd.read_json(json_file_path, lines=True)

# Display the DataFrame
print(df)
```

### Fetching Data Directly
```bash
curl 'https://raw.githubusercontent.com/candythink/Thai-Listed-Companies/main/ThaiListedCompanies.json' 
```

![sample](https://raw.githubusercontent.com/candythink/Thai-Listed-Companies/sample-pic/pics/sample1.png)

### Cloning the Repository
```bash
git clone https://github.com/candythink/Thai-Listed-Companies.git
```

## Dependencies
No specific dependencies are required to use the data in this file.

## Contributing
Contributions to this dataset are welcome. Please feel free to submit pull requests or open issues to discuss potential changes or additions.

---

Enjoy using the Listed Companies JSON data for your projects!
