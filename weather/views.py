from django.shortcuts import render
import requests
from datetime import datetime, timedelta

def index(request):
    context = {}
    if request.method == "POST" or request.method == "GET":
        city = request.POST.get('city')
        weather_url = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=39ee5a833609367c79395571fa3fd47f"
        forecast_url = "http://api.openweathermap.org/data/2.5/forecast?q={}&units=metric&appid=39ee5a833609367c79395571fa3fd47f"
        
        if city:
            weather_data = requests.get(weather_url.format(city)).json()
            forecast_data = requests.get(forecast_url.format(city)).json()
            if weather_data.get('cod') == 200 and forecast_data.get('cod') == "200":
                # Current weather
                context = {
                    'city' : city,
                    'temperature' : weather_data['main']['temp'],
                    'description' : weather_data['weather'][0]['description'],
                    'icon' : weather_data['weather'][0]['icon'],
                    'humidity' : weather_data['main']['humidity'],
                }
                # 3-day forecast
                forecast_list = []
                now = datetime.now()
                end_time = now + timedelta(days=3)
                for item in forecast_data['list']:
                    dt = datetime.fromtimestamp(item['dt'])
                    if now < dt < end_time:
                        forecast_list.append({
                            'date': dt.strftime('%a %d %b %H:%M'),
                            'temp': item['main']['temp'],
                            'desc': item['weather'][0]['description'],
                            'icon': item['weather'][0]['icon'],
                        })
                context['forecast'] = forecast_list

                # Recent search history (session-based)
                history = request.session.get('history', [])
                if city and city.lower() not in [h.lower() for h in history]:
                    history = ([city] + history)[:5]  # Keep last 5 searches
                    request.session['history'] = history
                context['history'] = history
            else:
                context = {
                    'error': f"City '{city}' not found. Please enter a valid city name."
                }
                # Show history even on error
                context['history'] = request.session.get('history', [])
        else:
            # Show history if no city searched yet
            context['history'] = request.session.get('history', [])

    return render(request, "index.html", context)