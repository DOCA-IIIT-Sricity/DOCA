from django.urls import path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.sessions import SessionMiddlewareStack
from . import consumers

application = ProtocolTypeRouter({

    'websocket': SessionMiddlewareStack(
        URLRouter(
            [
                #path('cities/',consumers.cities)
            ]
        )
    )

})
