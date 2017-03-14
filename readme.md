## Music Box for raspberry pi

### new api 2017.03.14

1. using new api(mp3_url) from [mellplayer](https://github.com/Mellcap/MellPlayer);
2. refresh playlist with new url, leave other methods untouched;


### fixes 2017.02.04

todos

+ response to error links (mp3_url), ~~which may result from 128k/320k sources~~;
+ add song view, render javascript array;
+ silent at start;
+ random play;
+ title and artist indicator;
+ no album name in mobile mode;
+ touch screen 'active' class: `<body ontouchstart="">`;

Deployment....


### updates 2017.02.03

1. use web browser to play the music;
2. mp3_url change -> 'http://m' to 'http://p' (magic in API);
3. javascript array to store music infomation instead of database queries;
