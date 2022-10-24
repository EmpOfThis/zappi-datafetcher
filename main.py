import credentials
from requests.auth import HTTPDigestAuth
import requests
import datetime
import json
from pytz import timezone
import csv


CSV_FILE = "data.csv"
csvHeaders = ["time", "energyPhase1(kWh)", "energyPhase2(kWh)", "energyPhase3(kWh)", "exportedEnergy(kWh)","exportedPrice(EUR)","importedEnergy(kWh)", "importedPrice(EUR)","chargingCosts123(EUR)", "currentEnergyPrice(EUR/kWh)"]
with open(CSV_FILE, 'w') as file:
    writer = csv.writer(file)
    writer = writer.writerow(csvHeaders)

endpoints = ["h1b", "h2b", "h3b", "exp", "imp"]
#h1b, h2b and h3b are the three charging phases, exp is the energy export endpoint and imp is the import energy endpoint
ZAPPI_URL = "https://s18.myenergi.net/cgi-jdayhour-Z"
ENERGY_URL = "https://api.energyzero.nl/v1/energyprices?interval=4&usageType=1"
btwIncluded = "false"
amsterdam = timezone("Europe/Amsterdam")

def getZappiDataMonth(startMonth, endMonth):
    # Get Max value for a day in given month
    beginDate = "01" + startMonth
    endMonthList = list(endMonth)
    month = endMonth[0] + endMonth[1]

    year = endMonthList[2] + endMonthList[3]+ endMonthList[4] + endMonthList[5]
    
    if(month == 12):
        endDate = "0101" + str(int(year) + 1)

    else:
        endDate = "01" + str(int(month) + 1).zfill(2) + str(int(year))
    getZappiData(beginDate, endDate)
    return

#https://s18.myenergi.net/cgi-jdayhour-ZserialZappi-2022-3-22
def getZappiData(inputStartDate, inputEndDate):
    startDate = datetime.datetime.strptime(inputStartDate, "%d%m%Y").date()
    finishDate = datetime.datetime.strptime(inputEndDate, "%d%m%Y").date()
    difference = finishDate - startDate
    daysToGo = difference.days
    if daysToGo > 120:
        print(f"Will try this, not certain if data available from back then")
    if daysToGo < 0:
        print(f"The startdate is later then the finishdate, that isnt possible")
        return

    currentDate = startDate
    startMomentUTC = str(datetime.datetime(startDate.year, startDate.month, startDate.day, 0,0).isoformat("T")) + ".000Z"
    finishMomentUTC = str(datetime.datetime(finishDate.year, finishDate.month, finishDate.day, 0,0).isoformat("T")) + ".000Z"
    prices = getEnergyPrices(startMomentUTC, finishMomentUTC) 
    for dayInPeriod in range(daysToGo):   
        url = ZAPPI_URL + credentials.serialZappi + "-" + str(currentDate)
        response = requests.get(url, auth=HTTPDigestAuth(credentials.serialHub, credentials.password))
        chargeHourly = json.loads(response.text)["U16262940"]
        buildCSV(endpoints, chargeHourly, prices, dayInPeriod, currentDate)
        print(f"Done calculating for {currentDate}.")
        currentDate += datetime.timedelta(days=1)
        
    #Minus one day because the for-loop adds one day on the last line that is not calculated    
    print(f"CSV built with data from {startDate} to {currentDate - datetime.timedelta(days=1)}.")


def buildCSV(endpoints, chargeHourly, prices, dayInPeriod, currentDate):
    for hour in range(24):
        dateString = currentDate.strftime("%d/%m/%Y")
        time = dateString + " "+  str(hour).zfill(2) + ":00"
        resultHour = [time]
        priceThisHour = prices[dayInPeriod * 24 + hour]["price"]
        chargePrice = 0
        
        #An endpoint refers to what the calculation is related to: charging, importing, exporting etc.
        for endpoint in endpoints:
            energy, price = linkOneHour(endpoint, chargeHourly, priceThisHour, hour)
            if endpoint in ["h1b", "h2b", "h3b"]:
                resultHour.append(energy)
                chargePrice += price
            else:
                resultHour.extend([energy,price])
        
        resultHour.extend([chargePrice, priceThisHour])
        with open(CSV_FILE, 'a', newline='') as file:
            writer = csv.writer(file)
            writer = writer.writerow(resultHour)



def linkOneHour(zappiEndpoint, chargeHourly, priceThisHour, hour):
    kWh = 3600000
    if zappiEndpoint in chargeHourly[hour]:
        energy = chargeHourly[hour][zappiEndpoint] / kWh
        price = energy * priceThisHour
        
        return energy, price
    else:
        return 0, 0
    

def getEnergyPrices(fromDate, tillDate):
    #tillDate is the last day of the range + 1, because of how the energyAPI serves the data
    parameters = {"fromDate":fromDate,"tillDate":tillDate,"inclBtw":btwIncluded}
    response = requests.get(ENERGY_URL, params=parameters)
    pricesPerHour = json.loads(response.text)["Prices"]
    return pricesPerHour


#Inputformat startdate is :ddmmyyyy
#getZappiData("01062022", "02062022")

#GetZappiDataMonth(Eerste maand, laatste maand.)
#Voor het hele jaar: getZappiDataMonth("012022", "122022")
getZappiDataMonth("042022", "042022")