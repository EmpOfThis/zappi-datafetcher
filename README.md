# zappi-datafetcher
Python 3 script to fetch information from Zappi servers, and combine this information with actual energy prices from the energyzero API, used by the Dutch 'ANWB energie' program. 'ANWB energie' is an energy provider that uses variable tarrifs, changing every hour based on the market price of energy.
Requires a Zappi charger.

**Setup**

The 'main.py' file should be used together with a 'credentials.py' file, having the following format:
```
serialHub:str = "HubSerialNumberHere"
serialZappi:str = "ZappiSerialNumberHere" 
password:str = "APIpasswordHere"
```
The APIpassword/key can be set up in the Zappi app

**Output**

The python file writes its data in a .CSV file, named 'data.csv'
The following headers will be printed in the .csv file, with their values per hour:
- time, date + hh:mm:ss;
- energy charged by Phase 1, 2 and 3 (kWh), seperated;
- exportedEnergy(kWh);
- exportedPrice(EUR): the total price of the energy exported;
- importedEnergy(kWh);
- importedPrice(EUR);	
- chargingCosts for Phase 1, 2, and 3 (kWh), bundeled;	
- energy price in the hour specified by time;

