- OCI Costs from FOCUS Report - LastDay (Example: Running today, get data from yesterday)
  
📊 FOCUS Reports Backup Script
This script is designed to download and process OCI (Oracle Cloud Infrastructure) FOCUS reports. It retrieves daily report files, decompresses them, processes the data, and outputs relevant information in JSON format. The script also calculates and formats the total billed cost.

🛠️ Dependencies
Python 3.x
OCI library (oci) - Setup de default configuration ~/.oci/config
Standard Python libraries: os, csv, json, glob, gzip, datetime, locale

📝 Script Overview
Locale Setup

Sets the locale to pt_BR.UTF-8 for formatting numbers and currency in Brazilian Portuguese.
Directory Setup

Creates the /tmp/oci directory if it doesn't exist to store downloaded files temporarily.
OCI Configuration

Loads OCI configuration from the default configuration file and profile.
Date Configuration

Sets the date prefix for the previous day's reports.
Object Storage Client Initialization

Initializes the OCI Object Storage client.
Report Download

Lists and downloads report files from the OCI bucket for the previous day.
Saves downloaded files to the destination path.
CSV Processing

Decompresses .gz files.
Reads CSV files and filters relevant data fields.
Calculates the total billed cost.
JSON Output

Converts filtered data to JSON format and prints it.
Prints the total billed cost in Brazilian Reais (R$).

⚠️ Error Handling
The script includes basic error handling for OCI service errors during the report download phase. It will print the error message if any issues occur while retrieving object metadata.


- Process running

![focus-download](https://github.com/mauriciodeliz/oci-costs-csv-json/assets/25036372/4ba55f40-3d34-4dad-92d9-ba6729fc4fdd)


- Result
  
![image](https://github.com/mauriciodeliz/oci-costs-csv-json/assets/25036372/f54d27fc-1003-43ba-82a8-c64663aed3c4)


