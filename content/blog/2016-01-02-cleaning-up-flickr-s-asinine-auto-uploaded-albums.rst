Cleaning up Flickr's Asinine Auto-uploaded Albums
#################################################

:date: 2016-01-02
:category: Random
:tags: flickr, photography, python, flickr uploadr

If you Google around for things like "mass delete flickr album", you'll find a lot of people on personal blogs and the flickr forum complaining about Flickr's desktop auto-uploader creating a friggin massive amount of albums. The uploader creates an album for every single folder it finds for your photos -- and since any intelligent photo management software will sort photos into subfolders based on date -- you can see where this will get out of hand.

The issue is that Flickr, via either their website or their auto-uploader software, provides NO WAY of deleting the albums in any helpful way. On the `flickr forums <https://www.flickr.com/help/forum/en-us/72157656351714341/>`_ you'll see that the acceptable solution is to just accept that you gotta go one-by-one on their site and just *delete 5 or 10 at a time*. That's ridiculous. Why does Flickr not provide the ability to bulk/mass delete albums??

My solution: Flickr API + Python
--------------------------------

So I tried deleting the albums manually for all of 5 minutes before I threw in the towel. I went instead to Flickr's API site and found you do have the ability to delete albums (photosets in API vernacular) from this interface. Luckily, there are also people who've made the api into `a Python module <https://github.com/alexis-mignon/python-flickr-api>`_.

Here I'll walk through how I used the `python_api` to delete most of my auto-generated albums.

Step 1: Get Flickr API key
~~~~~~~~~~~~~~~~~~~~~~~~~~
Go to the flickr site and apply for a key: https://www.flickr.com/services/apps/create/apply/

You'll end up with flickr giving you an api key and api secret. 

Step 2: Set up flickr_api
~~~~~~~~~~~~~~~~~~~~~~~~~
You can use pip to install flickr_api. Once installed, you've got to authenticate with flickr in Python. Specifically, we need to tell flickr that this script is going to have the permissions to delete -- so we can delete the photosets, obvs.

.. code-block:: python
    
    import flickr_api

    api_key = 'key_from_flickr'
    api_secret = 'secret_from_flickr'
    a = flickr_api.auth.AuthHandler() #creates the AuthHandler object
    perms = "delete" # set the required permissions
    url = a.get_authorization_url(perms)
    
    print(url)

then go to the url printed out and flickr will ask if you want to authorize. you OK it and then it'll give you some xml data in your browser. Find this line: `<oauth_verifier>my_auth_code</oauth_verifier>` (where obviously my_auth_code is a set of random letters and numbers...) and then we can auth with flickr and save the authentication so we don't need to do the above again...

.. code-block:: python
    
    a.set_verifier("my_auth_code")
    a.save('authed_flickr')

Step 3: Load auth'ed file and get those albums!
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Now that the file is saved the only code we need to run in our script from now on is

.. code-block:: python
    
    import flickr_api
    flickr_api.set_auth_handler('authed_flickr')
    user = flickr_api.test.login()

where the last line just gives us user for the case when we've already authenticated (which we have, with the 'authed_flickr' file). We can then get a whole list of our photosets with

.. code-block:: python
    
	photosets = user.getPhotosets()

If you check the type of photosets you'll see its a `flickr_api.objects.FlickrList`. So you can iterate through all the photosets and print them out with a simple

.. code-block:: python
    
    for photoset in photosets:
        print(photoset['title'])

Step 4: Figure out how to delete your garbage albums
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

At this point, you need to come up with your own clever solution for deleting the albums you no longer want. For me, I was lucky in that 989 of the 994 albums I didn't want were all in the standard expression of "yyyy-mm-dd". So all I needed to do was a crude loop through years and then delete any album whose name begins with that. In other words, I did this:

.. code-block:: python

    import numpy as np
    for N in np.arange(2001, 2016):
        photosets = user.getPhotosets()
        for photoset in photosets:
            if photoset['title'][0:5] == u'%s-'%(N):
                photoset.delete()
                print('deleting photoset '+photoset['title'])


This may not have been the most elegant loop through all my photosets but it worked. After only a few minutes, 99.5% of the damned albums had been deleted. Any album that didn't fit that format was then easily deleted one-by-one via it's name with a similar loop.

Step 5: Curse Flickr again for making this so annoying
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For real. WTF Flickr? Why do we have to go through this just to delete a bunch of albums? I actually hadn't logged into flickr for months because it was so annoying that all those albums existed and were clogging up my feed. I spent a few days looking for alternatives to flickr too. I just really really didn't want to delete those albums by hand. I'm sure I'm not the only one who had the same idea -- how many actually did jump ship? The flickr uploader was released in like... summer of 2015 (I think??) and it's been bothering everyone since then. Why couldn't they release a fix in the last 6 months? I just spent an hour and had at least a workable, janky solution and I'm not even a good coder. Yahoo -- you're losing business because of your shitty uploader and flickr interface! Do something about this!! 