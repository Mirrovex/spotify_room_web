import React, { useEffect, useState } from 'react';

export default function SpotifyPlayer() {
    const [spotifyReady, setSpotifyReady] = useState(false);
    const [player, setPlayer] = useState(null);

    useEffect(() => {
        console.log("START")
        const script = document.createElement('script');
        script.src = 'https://sdk.scdn.co/spotify-player.js';
        script.async = true;
        document.body.appendChild(script);

        script.onload = () => {
            console.log('Spotify SDK loaded');

            window.onSpotifyWebPlaybackSDKReady = () => {
                console.log('Spotify SDK ready');
                fetchAccessToken();
            };
        };

        const fetchAccessToken = async () => {
            fetch("/spotify/get-token")
            .then((response) => response.json())
            .then((data) => {
                initializeSpotifyPlayer(data.access_token)
            });
        };

    }, []);

    const initializeSpotifyPlayer = (accessToken) => {
        const newPlayer = new window.Spotify.Player({
            name: 'Web Playback SDK Quick Start Player',
            getOAuthToken: cb => { cb(accessToken); }
        });

        // Obsługa zdarzeń odtwarzacza i inna logika

        newPlayer.connect().then(success => {
            if (success) {
                setPlayer(newPlayer);
                setSpotifyReady(true);
            }
        }).catch(error => {
            console.error('Error connecting to Spotify:', error);
        });
    };

    const playMusic = () => {
        if (player) {
            player.togglePlay().then(() => {
                console.log('Music played/paused');
            }).catch(error => {
                console.error('Error toggling playback:', error);
            });
        }
    };

    return (
        <div>
            {spotifyReady ? (
                <div>
                    <button onClick={playMusic}>Play/Pause</button>
                </div>
            ) : (
                <div>
                    Inicjalizacja odtwarzacza...
                </div>
            )}
        </div>
    );
};
