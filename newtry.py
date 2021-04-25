from covid import Covid

covid = Covid(source="worldometers")
covid.get_data()
countries = covid.list_countries()
print(countries)
active = covid.get_total_active_cases()
confirmed = covid.get_total_confirmed_cases()
recovered = covid.get_total_recovered()
deaths = covid.get_total_deaths()
print(active,confirmed,recovered,deaths)