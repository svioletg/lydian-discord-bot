import time
import sys
import os
import json
import spotipy
import sclib
import colorama
from colorama import Fore, Back, Style
from palette import Palette
from fuzzywuzzy import fuzz
from spotipy import SpotifyClientCredentials
from datetime import datetime
from inspect import currentframe, getframeinfo
from ytmusicapi import YTMusic

_here = os.path.basename(__file__)

### TODO

# Personal debug logging
colorama.init(autoreset=True)
plt = Palette()

logtimeA = time.time()
logtimeB = time.time()

print_logs='quiet' not in sys.argv

def logln():
	cf = currentframe()
	if print_logs: print('@ LINE ', cf.f_back.f_lineno)

def log(msg):
	global logtimeA
	global logtimeB
	logtimeB = time.time()
	elapsed = logtimeB-logtimeA
	called_from = ' '+sys._getframe().f_back.f_code.co_name+':'
	if called_from==' <module>:': called_from=''
	logstring = f'{plt.file[_here]}[ {_here} ]{plt.reset}{plt.func}{called_from}{plt.reset} {msg}{plt.reset} {plt.timer} {round(elapsed,3)}s'
	if print_logs:
		print(logstring)
	logtimeA = time.time()

log('Imported.')

force_no_match=False
if 'fnm' in sys.argv: force_no_match=True
if force_no_match: log(f'{plt.warn}force_no_match is set to True.')

# Connect to youtube music API
ytmusic = YTMusic()

# Connect to spotify API
scred = json.loads(open('spotify_config.json').read())['spotify']
client_credentials_manager = SpotifyClientCredentials(client_id=scred['client_id'], client_secret=scred['client_secret'])
sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)

# Connect to soundcloud API
sc = sclib.SoundcloudAPI()

# For analyze()
keytable = {
	0: 'C major or A minor',
	1: 'C#/Db major or A#/Bb minor',
	2: 'D major or B minor',
	3: 'D#/Eb major or C minor',
	4: 'E major or C#/Db minor',
	5: 'F major or D minor',
	6: 'F#/Gb major or D#/Eb minor',
	7: 'G major or E minor',
	8: 'G#/Ab major or F minor',
	9: 'A major or F#/Gb minor',
	10: 'A#/Bb major or G minor',
	11: 'B major or G#/Ab minor',
}

# Define matching logic
def is_matching(reference,ytresult,**kwargs):
	title=reference['title']
	artist=reference['artist']
	album=reference['album']
	if 'ignore_album' in kwargs: matching_album = True; log('Ignoring album match.')
	else: matching_album = album.lower() in ytresult['album']['name'].lower()
	if 'ignore_artist' in kwargs: matching_artist = True; log('Ignoring artist match.')
	else: matching_artist = artist.lower() in ytresult['artists'][0]['name'].lower()
	matching_title = title.lower() in ytresult['title'].lower() or (title.split(' - ')[0].lower() in ytresult['title'].lower() and title.split(' - ')[1].lower() in ytresult['title'].lower())
	# Do not count tracks that are specific/alternate version,
	# unless said keyword matches the original Spotify title
	alternate_desired = any(i in title.lower() for i in ['remix', 'cover', 'version'])
	alternate_found = any(i in ytresult['title'].lower() for i in ['remix', 'cover', 'version'])
	alternate_check = False
	alternate_check = (alternate_desired and alternate_found) or (not alternate_desired and not alternate_found)
	return (matching_album) and (matching_artist) and (matching_title) and (alternate_check)

# Youtube
def search_ytmusic_album(title, artist, **kwargs):
	if force_no_match: log(f'{plt.warn}force_no_match is set to True.'); return None

	query=f'{title} {artist}'
	log('Starting album search...')
	album_results=ytmusic.search(query=query,limit=5,filter='albums')
	for i in album_results:
		title_match = fuzz.ratio(title,i['title'])>75
		artist_match = fuzz.ratio(artist,i['artists'][0]['name'])>75
		if title_match and artist_match:
			log('Match found.')
			return 'https://www.youtube.com/playlist?list='+ytmusic.get_album(i['browseId'])['audioPlaylistId']
	# This will only run if no match has been found
	log('No match found.')
	return None

def search_ytmusic_text(query, **kwargs):
	# For plain-text searching
	top_song=ytmusic.search(query=query,limit=1,filter='songs')[0]
	top_video=ytmusic.search(query=query,limit=1,filter='songs')[0]
	return top_song, top_video

def search_ytmusic(title, artist, album, **kwargs):
	global force_no_match
	unsure=False

	# Process kwargs
	reference={'title':title, 'artist':artist, 'album':album}
	query=f'{title} {album}'
	# The search limit doesn't actually seem to work, investigate this
	limit=20
	if 'limit' in kwargs: limit=kwargs['limit']

	# Start search
	log(f'Trying query \"{query}\" with a limit of {limit}')
	song_results=ytmusic.search(query=query,limit=limit,filter='songs')
	video_results=ytmusic.search(query=query,limit=limit,filter='videos')
	# Remove videos over a certain length
	duration_limit = 5 # in hours
	for i in song_results:
		if int(i['duration_seconds'])>duration_limit*60*60: song_results.pop(song_results.index(i))
	for i in video_results:
		if int(i['duration_seconds'])>duration_limit*60*60: video_results.pop(video_results.index(i))

	log('Checking for exact match...')
	if force_no_match: log(f'{plt.warn}force_no_match is set to True.')

	# Check for matches
	match=None
	def match_found():
		return match!=None and not force_no_match

	for i in song_results[:5]:
		if is_matching(reference,i,ignore_artist=True):
			log('Song match found.')
			match=i
			break

	if not match_found():
		log('Not found; checking for close match...')
		# Check user-uploaded videos
		for i in video_results:
			if int(i['duration_seconds'])>duration_limit*60*60: video_results.pop(video_results.index(i))
		# If no close match is found, pass to the user
		for i in video_results[:5]:
			if is_matching(reference,i,ignore_artist=True,ignore_album=True):
				log('Video match found.')
				match=i
				break

	if not match_found():
		log('No match. Setting unsure to True.')
		unsure=True

	# Make new dict with more relevant information
	results={}
	# Determine what to queue
	if match_found():
		match={
			'title': match['title'],
			'artist': match['artists'][0]['name'],
			'url': 'https://www.youtube.com/watch?v='+match['videoId'],
			'duration': match['duration'],
		}
		# Return match
		log('Returning match.')
		return match
	else:
		log('Creating results dictionary...')
		song_choices=2
		video_choices=2
		position = 0
		for result in song_results[:song_choices]:
			results[position] = {
				'title': result['title'],
				'artist': result['artists'][0]['name'],
				'album': result['album']['name'],
				'url': 'https://www.youtube.com/watch?v='+result['videoId'],
				'duration': result['duration'],
			}
			position+=1

		for result in video_results[:video_choices]:
			results[position] = {
				'title': result['title'],
				'artist': '',
				'album': '',
				'url': 'https://www.youtube.com/watch?v='+result['videoId'],
				'duration': result['duration'],
			}
			position+=1

		# Ask for confirmation if no exact match found
		if unsure:
			log('Returning as unsure.')
			return 'unsure', results

# SoundCloud
def soundcloud_playlist(url):
	playlist = sc.resolve(url).tracks
	return [obj for obj in playlist]

# Spotify
def get_uri(url):
	return url.split("/")[-1].split("?")[0]

def spotify_track(url):
	info=sp.track(url)
	title=info['name']
	# Only retrieves the first artist name
	artist=info['artists'][0]['name']
	album=info['album']['name']
	return {'title':title, 'artist':artist, 'album':album, 'url':info['external_urls']['spotify']}

def spotify_album(url):
	info=sp.album(url)
	return {'title':info['name'], 'artist':info['artists'][0]['name']}

def analyze_track(url):
	uri=get_uri(url)
	title=sp.track(uri)['name']
	artist=sp.track(uri)['artists'][0]['name']
	data=sp.audio_features(uri)[0]

	# Nicer formatting
	data['tempo']=str(int(data['tempo']))+'bpm'
	data['key']=keytable[data['key']]
	data['time_signature']=str(data['time_signature'])+'/4'
	data['loudness']=str(data['loudness'])+'dB'

	# Replace ms duration with readable duration
	ms=data['duration_ms']
	hours = int(ms/(1000*60*60))
	minutes = int(ms/(1000*60)%60)
	seconds = int(ms/1000%60)

	# Don't include hours if less than one
	hours=str(hours)
	hours+=':'
	if float(hours[:-1])<1:
		hours=''
	length = f'{hours}{minutes}:{seconds:02d}'
	data['duration']=length
	data.pop('duration_ms')

	# Ignore technical/non-useful information
	skip=['type', 'id', 'uri', 'track_href', 'analysis_url', 'mode']

	return data, skip

def spyt(url, **kwargs):
	limit=20
	if 'limit' in kwargs:
		limit=kwargs['limit']

	if '/album/' in url:
		log('Album detected.')
		return # work on this later
		tracks=spotify_playlist(url)
		playlist=[]
		for track in tracks:
			# For playlists, each track is searched for when its turn in the queue is reached.
			# This will pass along the title and spotify url
			playlist.append(track)
		return playlist
	else:
		log('Not a playlist.')
		track=spotify_track(url)
		result = search_ytmusic(title=track['title'],artist=track['artist'],album=track['album'],limit=limit,**kwargs)
		if type(result)==tuple and result[0]=='unsure':
			log('Returning as unsure.')
			return result
		return result