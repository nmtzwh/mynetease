from django.conf.urls import url

from . import views

app_name = 'musicbox'
urlpatterns = [
    # index
    url(r'^$', views.index, name='index'),
    # playlist, ex: /musicbox/5/
    url(r'^(?P<playlist_id>[0-9]+)/$', views.playlist, name='playlist'),
    # songinfo, ex: /musicbox/5/songinfo/
    url(r'^(?P<pk>[0-9]+)/songinfo/$', views.SonginfoView.as_view(), name='songinfo'),
    # play song in list
    url(r'^(?P<playlist_id>[0-9]+)/play/$', views.play, name='play'),
    # search song via netease music
    url(r'^search/$', views.search, name='search'),
    url(r'^addsongs/$', views.addsongs, name='addsongs'),
    # controls
    url(r'^play/$', views.play, name='play'),
    url(r'^stop/$', views.stop, name='stop'),
    url(r'^deleteSong/$', views.deleteSong, name='deleteSong'),
    # playlists
    url(r'^addplaylist/$', views.addplaylist, name='addplaylist'),
    url(r'^searchPlaylist/$', views.searchPlaylist, name='searchPlaylist'),
    url(r'^playlist/$', views.changePlaylist, name='changePlaylist'),
]
