Eighty Nine Nine.com UPDATE!
############################

:category: Random
:image: ../images/kcrw_logo.png

D3 & speed upgrades to Eightyninenine.com
=========================================

After 3 or 4 years of leaving it to its own devices, I finally had the time to do some major fixes to `eightyninenine.com <http://www.eightyninenine.com>`_. Important changes:

  * replaced all the highcharts.js-based plots with my own d3.js versions. artist/song bar charts have been replaced with dual axes scatter plot for play counts and cumulative play counts. the DJ versions are cum. play counts for each DJ.
  
  * songplay-history plots have the ability to group by day, month, or year. it used to be that those options would actually initiate full queries of the postgres db in order to group (which is just dumb in itself). but now i do it all directly with javascript in the browser and it's infinitely faster.
  
  * i removed several superfluous db queries on page load; the site is at least slightly more responsive than it used to be.
  
  * didn't get any db indexing set up like i wanted so thing's still have a lot of room for improvement.
  
my secondary goal is to create some interesting data viz in honor of Jason Bentley's end of run as the producer for Morning Becomes Eclectic from KCRW. I pulled the ~ 2 million db entries from the site to have locally so I can play with them here and not worry about nuking the website.
