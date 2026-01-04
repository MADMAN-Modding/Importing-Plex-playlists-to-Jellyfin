# How to import playlists from Plex to Jellyfin, no matter the user type

<p>I'll preface this by saying that access to the Plex and Jellyfin servers' filesystems is required</p>

<p>I will also preface this with that I am doing this on Linux, the only command that will really need is sqlite3, as that will be used for data extraction.</p>

<h2>Exporting</h2>


You will need access to your Plex server's filesystem in some capacity, mine was an LXC container on Proxmox so I copied the raw disk image and mounted it, check <a href="#Mounting .raw file from Proxmox">here</a> for how to do that; or simply just SSH, I was doing a lot on the server so I wanted local access when I figured this out.

The path provided assumes that you have mounted your Plex server at <b>/mnt/lxc</b>. Running this command will output the following data:
    <b>Playlist ID</b>|Tracks|Playlist Name

    sqlite3 "/mnt/lxc353/var/lib/plexmediaserver/Library/Application Support/Plex Media Server/Plug-in Support/Databases/com.plexapp.plugins.library.db" \
    "
    SELECT ID, media_item_count, title
    FROM metadata_items
    WHERE metadata_type = 15;
    "

Identify your playlist's id a take note of it somewhere, I don't care where, memorize it if you're bored.

Now we need to export that playlist to a 3mu file, run the following command to do so, take note of what is happening here, this provides an example of how to replace the paths of the media as it is found and also change the PLAYLIST_ID section to your playlist's id.

Remove the SELECT REPLACE(...) line if your media is mounted the same on both servers

    sqlite3 "/mnt/lxc/var/lib/plexmediaserver/Library/Application Support/Plex Media Server/Plug-in Support/Databases/com.plexapp.plugins.library.db" \
    "
    SELECT REPLACE(mp.file, '/mnt/share/Media', '/mnt/Media')
    FROM play_queue_generators pqg
    JOIN media_items m ON m.metadata_item_id = pqg.metadata_item_id
    JOIN media_parts mp ON mp.media_item_id = m.id
    WHERE pqg.playlist_id = PLAYLIST_ID
    ORDER BY pqg.id;
    " > MyPlaylist.m3u

Now you have a .3mu file with the paths to all your music on it, which is exactly what you need from Plex to get this into Jellyfin.

# Importing to Jellyfin

There's two ways to do this

The first method involves scanning the 3mu file into Jellyfin via adding it to a library and having it recognize it as a playlist.

The second is converting the playlist to an XML file to overwrite an empty playlist on Jellyfin and then refreshing the playlist's metadata.

<h2>The First Solution</h2>

Add the 3mu file to your music library, run a scan on Jellyfin--if you are making a temporary library for this make sure your user can access it.

Locate the playlist in the playlists section since 3mu files are accessible to all, if your playlist is big like mine it won't show the songs at first,just press play to see if something happens, if not, it's probably fine, or not. 

Press the three vertically-stacked dots and press <b>Add to Playlist</b> then either make a new playlist or add it to an existing one, I don't care what you do.

Finally delete the 3mu file from your media library and refresh Jellyfin to remove it from your server.

<h2>The Second Solution</h2>
I'm going to be straight forward, I used AI to write this script because I wasn't about to learn how to handle XML in Python because as you can see by my GitHub, I don't use Python, Rust and Java are what I use the most.

Download the script called <b>3mu-to-xml.py</b>

Open it up and change the user_id on line 7 to match what is shown in the url when you go to your profile on Jellyfin (click your profile image) and grab the value for the URI component

    ex: http://jelly.example.com:8096/web/#/userprofile?userId=123a456b789c

Run the script, making sure that the 3mu file is in the same directory

    python ./3mu-to-xml.py

On Jellyfin make a playlist under your account, put a random song in there or something.

Now enter Jellyfin's file system, I did this via SFTP, you do you.

Head to the following directory

    /var/lib/jellyfin/data/playlists

This will contain nicely named folders based on the name of the playlist, simply replace the .xml file in that previously-created playlist with the one that was generated, ensuring that you are overwriting the file not making a file called something different and deleting the previous file.

Find the playlist on Jellyfin, it will not be updated

Press the three vertically-stacked dots, <b>Refresh metadata</b> I just stuck with <b>Scan for new and updated files</b> and after it scanned them in my playlist contained all of the music from my Plex playlist.

I'll mention that the song I added when I did this was one in my playlist already, I'm assuming Jellyfin would remove the song if it was not already in your playlist but we all know what assuming makes, or is that an assumption in it of it itself?

# Mounting .raw file from Proxmox

This is only for Linux, Windows & Mac users good luck, Mac will probably be find as it is built on Unix like GNU/Linux.

First you will need to get your file from Proxmox, now if you are not using an LXC I'm not sure what you're doing but anyways, lookup how to mount a qcow2 file. You can connect to Proxmox's files by either setting up a samba share on there or simply connecting via SFTP, if you are on KDE, just use the address bar to connect

    sftp://proxmox01.example.com

The login creds are what you would use to ssh

If you are sent to a directory called 

    /root


Then just go up one directory to get to the root filesystem of Proxmox.

If you don't remember where you mounted the drive that holds your Plex container, go the <b>storage</b> tab on the <b>Datacenter</b> page, look for the <b>Path/Target</b> for the desired drive.

Now that you know where you have to go, head there on Proxmox, go into the <b>images</b> folder and then the folder that matches the ID of your LXC container.

Copy the RAW file inside of there to your computer anywhere you'd like, it's probably going to be big so I hope you storage, if you don't, then you can SSH into Proxmox and copy the file and follow the following instructions on Proxmox, probably at least, that's up to you to test.

Run the following command to connect the image to the first unused loop device

    sudo losetup -f vm-XXX-disk-0.raw

Run this to find where the drive is connected

    losetup -a

    example output: dev/loop0: []: (/home/user/Downloads/XXX/vm-XXX-disk-0.raw)

Make a directory for the image and mount it

    sudo mkdir -p /mnt/lxc

    sudo mount /dev/loop0 /mnt/lxc

Continue with the rest of the instruction