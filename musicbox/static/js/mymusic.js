$(document).ready(function(){
    // audio element
    var audio = $("audio#hidden-song")[0];
    // music list:
    var songNum = 0;

    {% for song in playlist.song_set.all reversed %}
    <tr class="clickable-row">
      <td data-songid="{{song.id}}" class="hidden-xs-down">{{forloop.counter}}</td>
      <td>{{song.song_name}}</td>
      <td>{{song.artist_name}}</td>
      <td>{{song.album_name}}</td>
      <td class="hidden-sm-down"><a href="http://music.163.com/#/song?id={{ song.netease_id}}" target="_blank">Netease</a></td>
    </tr>
    {% endfor %}


    var SongInfo = [
      {% for song in playlist.song_set.all reversed %}
      {
        "title" : {{song.song_name}},
        "artist" : {{song.artist_name}},
        "source" : {{song.mp3_url}}
      },
      {% endfor %}
    ];

    // generate playlist html
    var songTotal = SongInfo.length;
    // alert(songTotal);

    var listHtml = "";
    for (var i=0; i<songTotal; i++){
      listHtml += '<li value="' + i + '" ><span>' + SongInfo[i].artist +' - '+SongInfo[i].title + '</span></li>';
    }
    $( "ul.music-playlist" ).html(listHtml);

    // autoplay first song
    audio.src = SongInfo[0].source;
    audio.play();
    // $(".music-info").show();
    $(".music-info").html("<marquee>Now Playing: "+SongInfo[0].title+" - "+SongInfo[0].artist+"</marquee>");

    // click songs in playlist to play it
    $( ".music-playlist li" ).click(function() {
      songNum = $( this ).val();
      audio.src = SongInfo[songNum].source;
      audio.play();
      // $(".music-info").show();
      $(".music-info").html("<marquee>Now Playing: "+SongInfo[songNum].title+" - "+SongInfo[songNum].artist+"</marquee>");
    });

    // play music
    $( "#musicPlay" ).click(function() {
      // audio.src = "../../music/" + songSource[1];
      audio.play();
    });
    // pause music
    $( "#musicPause" ).click(function() {
      audio.pause();
    });
    $( "#musicList" ).click(function() {
        $(".music-playlist-wrapper").toggle();
    });
    $( "#musicRandom" ).click(function() {
      songNum = parseInt(Math.random() * songTotal);
      audio.src = SongInfo[songNum].source;
      audio.play();
      $(".music-info").html("<marquee>Now Playing: "+SongInfo[songNum].title+" - "+SongInfo[songNum].artist+"</marquee>");
    });

    // continue playing next song if current song is ended
    audio.addEventListener('ended',function(){
      songNum = songNum == songTotal-1 ? 0 : songNum+1;
      audio.src = SongInfo[songNum].source;
      audio.play();
      // $(".music-info").show();
      $(".music-info").html("<marquee>Now Playing: "+SongInfo[songNum].title+" - "+SongInfo[songNum].artist+"</marquee>");
    },false);


});
