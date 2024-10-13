# oxrgenerator
A program for Automatically generating Open X-Ray Files

# What is a Open X-Ray File?
An OXR or Open X-Ray File is used to display the actors in a certain frame. It is based on Amazon's Xray system.

# How does this program work?
This program takes a video file.
Then it searchs on IMDB and downloads actor's headshots.
Extracts 1 frame per second from it.
Then uses the headshots to try and identify the actors.
It then saves the identified actors to a subtitle-like file

It is my intention to build a database of these files and intergrate the file format into in-home streaming services like Plex and Jellyfin.
You can see the beginning of this database [here](https://oxrdatabase.neocities.org/).

