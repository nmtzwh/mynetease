from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.views import generic
from django.template.loader import render_to_string

# cache to store simple variables
from django.core.cache import cache
from django.utils import timezone
from .models import Playlist, Song
import json

# netease api
import ast
import musicbox.api
import musicbox.player
netease = musicbox.api.NetEase()
musicPlayer = musicbox.player.Player()

# new api from https://github.com/Mellcap/MellPlayer
import musicbox.newApi
api_new = musicbox.newApi.Netease()

def changeUrlInPlaylist(playlist):
    # get song id in a playlist
    ids = []
    for song in playlist.song_set.all():
        ids.append(song.netease_id)
    # get new urls
    data = api_new.song_detail_new(ids)
    song_details = api_new.parse_info(data=data, parse_type='song_detail_new')
    # change url in list
    for song in playlist.song_set.all():
        mp3Url = song_details.get(song.netease_id, None)['song_url']
        if mp3Url != None and song.mp3_url != mp3Url:
            song.mp3_url = mp3Url
            song.save()
    return playlist

# def initPlaylistId():
#     pid = Playlist.objects.order_by('-create_date')[0].id
#     cache.set('playlist_now', pid, None)
#     cache.set('playlists', Playlist.objects.order_by('-create_date'), None)

# class IndexView(generic.ListView):
#     initPlaylistId();
#     template_name = 'musicbox/index.html'
#     context_object_name = 'latest_playlist'
#     def get_queryset(self):
#         """Return the last five created playlists."""
#         return Playlist.objects.order_by('-create_date')
def index(request):
    pid = Playlist.objects.order_by('-create_date')[0].id
    cache.set('playlist_now', pid, None)
    cache.set('playlists', Playlist.objects.order_by('-create_date'), None)
    context = {
        'playlist': changeUrlInPlaylist(get_object_or_404(Playlist, pk=cache.get('playlist_now'))),
        'playlists': cache.get('playlists')
    }
    return render(request, 'musicbox/playlist.html', context)

class SonginfoView(generic.DetailView):
    model = Song
    template_name = 'musicbox/songinfo.html'

# def index(request):
#     latest_playlist = Playlist.objects.order_by('-create_date')[:5]
#     context = {
#         'latest_playlist': latest_playlist,
#     }
#     return render(request, 'musicbox/index.html', context)
#
# def playlist(request, playlist_id):
#     playlist = get_object_or_404(Playlist, pk=playlist_id)
#     return render(request, 'musicbox/playlist.html', {'playlist': playlist})
#
#
# def songinfo(request, song_id):
#     song = get_object_or_404(Song, pk=song_id)
#     # response = "You're looking at the information of song %s."
#     return render(request, 'musicbox/songinfo.html', {'song':song})

def playlist(request, playlist_id):
    playlist = get_object_or_404(Playlist, pk=playlist_id)
    cache.set('playlist_now', playlist_id, None)
    playlists = cache.get('playlists')
    playlist = changeUrlInPlaylist(playlist)
    return render(request, 'musicbox/playlist.html', {'playlist': playlist, 'playlists': playlists})

################################################################################
def play(request):
    playlist = get_object_or_404(Playlist, pk=cache.get('playlist_now'))
    if request.GET['song_id'] != '0':
        try:
            selected_song = playlist.song_set.get(pk=request.GET['song_id'])
        except (KeyError, Song.DoesNotExist):
            # Redisplay the question voting form.
            return render(request, 'musicbox/playlist.html', {
                'playlist': playlist,
                'error_message': "You didn't select a song.",
            })
        else:
            # print selected_song
            url_list = []
            url_list.append(selected_song.mp3_url)
            # append other songs in list
            other_song = playlist.song_set.all().exclude(pk=request.GET['song_id'])
            for song in other_song[::-1]:
                url_list.append(song.mp3_url)
            # play with system player
            musicPlayer.playUrl(url_list)
            return render(request, 'musicbox/playlist.html', {
                'playlist': playlist,
                'playlists': cache.get('playlists'),
            })         # return HttpResponseRedirect(reverse('musicbox:playlist', args=(selected_song.id,)))
    else: # not specify starting song
        url_list = []
        other_song = playlist.song_set.all()
        for song in other_song[::-1]:
            url_list.append(song.mp3_url)
        # play with system player
        musicPlayer.playUrl(url_list)
        return render(request, 'musicbox/playlist.html', {
            'playlist': playlist,
            'playlists': cache.get('playlists'),
        })



def stop(request):
    playlist = get_object_or_404(Playlist, pk=cache.get('playlist_now'))
    musicPlayer.stop()
    return render(request, 'musicbox/playlist.html', {
        'playlist': playlist,
        'playlists': cache.get('playlists'),
    })

################################################################################
# get song information from netease api
def getSongInfo(searchStr):
    data = netease.search(searchStr)
    song_ids = []
    if 'songs' in data['result']:
        if 'mp3Url' in data['result']['songs']:
            songs = data['result']['songs']
        # if search song result do not has mp3Url
        # send ids to get mp3Url
        else:
            for i in range(0, len(data['result']['songs'])):
                song_ids.append(data['result']['songs'][i]['id'])
            songs = netease.songs_detail(song_ids)
        songinfo =  netease.dig_info(songs, 'songs')
    else:
        songinfo = []
    return songinfo

def search(request):
    playlist = get_object_or_404(Playlist, pk=cache.get('playlist_now'))
    try:
        songinfo = getSongInfo(request.POST['searchStr'])
    except:
        response = dict(error='error')
    else:
        response = dict(error='no')
        search_result = []
        for i in range(0, len(songinfo)):
            if songinfo[i]['mp3_url']:
                temp = dict(netease_id=songinfo[i]['song_id'], song_name=songinfo[i]['song_name'], artist_name=songinfo[i]['artist'],
                            album_name=songinfo[i]['album_name'], mp3_url=songinfo[i]['mp3_url'])
                search_result.append(temp)
        response['search_results'] = render_to_string('musicbox/ajaxSong.html', {'search_result': search_result})
        return HttpResponse(json.dumps(response))

def addsongs(request):
    playlist = get_object_or_404(Playlist, pk=cache.get('playlist_now'))
    for name in request.POST:
        song = request.POST[name]
        if 'song_name' in song:
            # convert to dictionary
            song = ast.literal_eval(song)
            # print song['song_name']
            playlist.song_set.create(song_name = song['song_name'],
                                     artist_name = song['artist_name'],
                                     album_name = song['album_name'],
                                     mp3_url = song['mp3_url'],
                                     netease_id = song['netease_id'])
    # generate mp3_urls for front-end
    songInfo = []
    playlist = changeUrlInPlaylist(playlist)
    for song in playlist.song_set.all():
        dict_temp = {"title" : song.song_name, "artist" : song.artist_name, "source" : song.mp3_url, "songid" : song.id, "status" : "live"}
        songInfo.append(dict_temp)
    songInfo.reverse()
    # multiple html parts
    response = dict(songlist=render_to_string('musicbox/ajaxSong.html', {'playlist':playlist}))
    response['urllist'] = json.dumps(songInfo)
    return HttpResponse(json.dumps(response))

def deleteSong(request):
    response = dict(song_id=request.GET['song_id'])
    response['error'] = True
    playlist = get_object_or_404(Playlist, pk=cache.get('playlist_now'))
    if request.GET['song_id'] != '0':
        try:
            selected_song = playlist.song_set.get(pk=request.GET['song_id'])
        except (KeyError, Song.DoesNotExist):
            # Redisplay the question voting form.
            return HttpResponse(json.dumps(response))
        else:
            # print selected_song
            selected_song.delete()
            response['error'] = False
            return HttpResponse(json.dumps(response))
    else: # not specify delete song
        return HttpResponse(json.dumps(response))

################################################################################
# add or search for existing playlists
def addplaylist(request):
    newlist = Playlist(label=request.POST['playlist_label'], comment=request.POST['playlist_comment'], create_date=timezone.now())
    newlist.save()
    # create empty playlist
    if request.POST['playlist_type'] == 'new':
        pass
    # add songs in user playlist to new list
    elif request.POST['playlist_type'] == 'user':
        data = netease.playlist_detail(request.POST['playlist_searchReId'])
        songs = netease.dig_info(data, 'songs')
        songs.reverse()
        for song in songs:
            newlist.song_set.create(song_name = song['song_name'],
                                     artist_name = song['artist'],
                                     album_name = song['album_name'],
                                     mp3_url = song['mp3_url'],
                                     netease_id = song['song_id'])
    # added and jump to playlist view
    cache.set('playlist_now', newlist.id, None)
    cache.set('playlists', Playlist.objects.order_by('-create_date'), None)
    return render(request, 'musicbox/playlist.html', {
        'playlist': newlist,
        'playlists': cache.get('playlists'),
    })

def getListInfo(searchStr):
    data = netease.search(searchStr, stype=1000)
    return netease.dig_info(data['result']['playlists'], 'top_playlists')

def searchPlaylist(request):
    # search playlist online
    error = None
    listinfo = []
    playlist_result = []
    # print request.GET['searchStrList']
    if not request.GET['searchStrList']:
        error = 'You have to enter some shit ...'
    else:
        listinfo = getListInfo(request.GET['searchStrList'])  # add search type in the future!!!
        if len(listinfo) == 0:
            error = 'Sorry, cannot find any playlist T^T'
    for i in range(0, len(listinfo)):
        temp = dict(playlist_netease_id=listinfo[i]['playlist_id'], creator_name=listinfo[i]['creator_name'], playlists_name=listinfo[i]['playlists_name'])
        playlist_result.append(temp)
    return render(request, 'musicbox/ajaxSearchPlaylist.html', {
        'playlists': playlist_result,
    })

# ajax change playlist
def changePlaylist(request):
    playlist = changeUrlInPlaylist(get_object_or_404(Playlist, pk=request.GET['pid']))
    cache.set('playlist_now', request.GET['pid'], None)
    playlists = cache.get('playlists')
    # generate mp3_urls for front-end
    songInfo = []
    for song in playlist.song_set.all():
        dict_temp = {"title" : song.song_name, "artist" : song.artist_name, "source" : song.mp3_url, "songid" : song.id, "status" : "live"}
        songInfo.append(dict_temp)
    songInfo.reverse()
    # multiple html parts
    response = dict(title=render_to_string('musicbox/ajaxTitle.html', {'playlist':playlist}))
    response['sidebar'] = render_to_string('musicbox/ajaxPlaylist.html', {'playlist':playlist, 'playlists':playlists})
    response['songlist'] = render_to_string('musicbox/ajaxSong.html', {'playlist':playlist})
    response['urllist'] = json.dumps(songInfo)
    return HttpResponse(json.dumps(response))
