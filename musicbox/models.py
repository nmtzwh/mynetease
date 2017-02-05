from django.db import models
from django.utils.encoding import python_2_unicode_compatible

import datetime
from django.utils import timezone

# Create your models here.
@python_2_unicode_compatible  # only if you need to support Python 2
class Playlist(models.Model):
    # playlist_id = models.IntegerField()
    label = models.CharField(max_length=200)
    comment = models.CharField(max_length=200)
    create_date = models.DateTimeField('date created')
    def __str__(self):
        return self.label
    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=10) <= self.create_date <= now

@python_2_unicode_compatible  # only if you need to support Python 2
class Song(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    song_name = models.CharField(max_length=200)
    artist_name = models.CharField(max_length=200)
    album_name = models.CharField(max_length=200)
    mp3_url = models.CharField(max_length=200)
    netease_id = models.IntegerField()
    def __str__(self):
        return self.song_name


# drop table if exists playlist;
# create table playlist (
#   playlist_id integer primary key autoincrement,
#   label text not null,
#   comment text
# );
#
# drop table if exists song;
# create table song (
#   song_id integer primary key autoincrement,
#   in_playlist integer not null,
#   netease_id integer not null,
#   song_name text not null,
#   artist_name text not null,
#   album_name text not null,
#   mp3_url text not null
# );
