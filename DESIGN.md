Summary:

Static Folder:
Within the static folder, you will find our logos, profile images, a folder for all of the files that users upload called "uploads" as well as our CSS style sheet.

Style.CSS:
This file contains all of our CSS for our project which encompases most of the design (some was done using bootstrap in HTML). We used different classes to specify certain designs mainly focusing on html elements and cards.

Templates:
Within templates you will find our templates for all of our pages that extend layout.html. Within these pages we used Jinja to pull data from SQL created in functions from app.py. Each template is also connected through layout.html to the style.css so we could style each template to our liking.

app.py:
app.py contains all of our functions to be preformed on the backend of the website. Within it are the functions to login, register, logout, list an item, search for items, deposit money, browse for items, remove items, watch items, edit your profile, and buy items. Much of this is comprised of db.execute commands to pull and work with iko.db (our SQL database). It was also crucial for us to check for errors and flash a message if an error occurs.

helpers.py:
Helpers.py contains some more functions to require a login, format US Dollars, and to make sure we allow only certain files to be uploaded.

iko.db:
iko.db contains our SQL database.

–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
Individual: 

List: To implement the ability to list a product, we created a table 'listings' in our database, with columns for each of the categories of a product (price, name, size, etc.). The difficult part, however, was allowing users to upload images to go with their products, as it is quite complicated to store images, especially user-uploaded images, in a SQL database. We were able to solve this by uploading the images to the server in a folder in static called "uploads". Instead of storing the images themselves in the database, we created and stored a URL to access the images. We also used a hash function to make sure that each image URL would be unique. Finally, with all this information, we added a new row to the listings table. 

Search: The search component was the key element to our website. We wanted users to be able to filter by any criteria to find items that would match an outfit or style. We tried to use select menus for as many categories as possible, but it was impractical for about half (like Title). Once the information was put in, we sent it to app.py to be prepared for a SQL Select. The biggest hurdle was navigating what to do when a field was left blank because the SQL query was predetermined. If we searched WHERE color = "", nothing would come up. A blank field actually meant that users wanted ALL colors (WHERE color = all). Such a statement does not exist in SQL, however, so we opted for "LIKE %". By looking up WHERE color LIKE %, we select every item. Thus, if statement were put in place to replace a "" with a "%". After getting all the result back, we displayed them on results.html using a for loop with jinja, each loop creating its own card. 

Browse: The browse page was the exact same as results.html, expect that the "results" on the browse page are always selecting all active (unsold) cards. 

Watchlist: We created a watchlist table in the iko.db database in order to facilitate the watchlist page. This was as simple as two columns for item id and watcher. If a user selected "Add to Watchlist" on a card, the card would be added to this database. The watchlist page uses a nested Select query to return "results" for watched cards. If a card is sold, the buy now button is replaced by "Sold" using a jinja if statement. To remove emove from watchlist means that listing is dropped from the watchlist table.

About: The about page was a simple HTML page.

Profile: The profile page is the heart of user experience. it has a profile card that has all user info. We displayed all listings owned by the user, and used jinja to display an "unlist" button or a "sold" marker. Unlisting removes the listing from listings, and thus removes it from the entire system. We didn't want to use a status to mark an item as unlisted because the information would still be in the system. If a user unlists an item, they want it permanently removed, not hidden. Below the listings section is a purchase log, which draws directly from the purchase_log table to show all items that the current user bought. Below this is a deposit cash section. We incldued this to circumvent users needing to input actual money. It works very simply with a form posted to a deposit function, where it then adds the input number to the user funds. Finally, there is a log-out button, which ends the current session and logs the user out. 

Buy: The buy function is not its own page, but is essential to the site. Whenever the "buy now" button is pressed on a card, the buy function is set into motion. We did this by creating a form with an invisible field "id" that uses jinja to store the id of the item on the card. When the buy now button is pressed, this id is sent to the buy function. We did this so that we could easily make sure that the correct item is being bought when the button is pressed. The buy function simply marks the listing as inactive, removes the funds for the price from the buyer, and adds these funds to the funds of the lister. It also tracks the purchase by adding it to the purchase_log.
