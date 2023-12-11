from django.contrib import admin

from airport.models import (Airport,
                            Airplane,
                            Airline,
                            Crew,
                            Flight,
                            Route,
                            Order,
                            Ticket)


admin.site.register(Airport)
admin.site.register(Airplane)
admin.site.register(Airline)
admin.site.register(Crew)
admin.site.register(Flight)
admin.site.register(Route)
admin.site.register(Order)
admin.site.register(Ticket)

