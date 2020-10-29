// Unique words of Slack users
// Part I. A JavaScript code snippet for scraping messages on Slack.
// Full description on https://github.com/dmitryplaunov/unique-words-on-slack
// Copyright (c) 2020 Dmitry Plaunov; Licensed MIT.


// This script depends on the front-end of the search page on Slack.
// If Slack re-organizes the page or renames element classes (identifiers), this script might stop working.
// Luckily, in 6 months of 2020, only 1 element name was changed, so the script required minimal adjustment.


// declaring a variable where all the scraped messages will be stored
// making it empty, instead of 'undefined', as new messages will be appended after every page is scraped
var all_messages = ''

// getting the number of pages to scrape
// your search results page should not have more than 100 pages, as Slack breaks when navigating to pages after 100th
// if you have more than 100 pages, try to segment the search results by dates
try {
		page_counter_element = document.getElementsByClassName('c-search__pager__details')[0].innerHTML; // "Page 1 of 8"
		last_page_str = page_counter_element.split('of ')[1] // "8"
		number_of_pages = parseInt(last_page_str) // 8
} catch(error) {
		throw "The script needs adjustment. The number of pages element wasn't found."
}

// or you can define the number of pages manually
// it should not be bigger than 100, as Slack breaks when navigating to pages after 100th
// number_of_pages = 50

// a function for scraping Slack messages
function pageScraping()	{

		try {
				// declaring a variable where all the scraped messages from the current search page will be stored
				// the content of it will be later appended to 'all_messages'
				var page_messages = ''

				// getting the number of messages that need to be expanded to get their full content
				var num_of_expand = document.getElementsByClassName('c-button-unstyled c-search__expand').length;

				if (num_of_expand > 0) {
						// expanding messages on the page
						var k=0
						for (k=0; k<num_of_expand; k++) {
							// when the 'show more' button gets clicked, it disappears, so the next button has the 0 index again
								document.getElementsByClassName('c-button-unstyled c-search__expand')[0].click()
						}
				}

				// getting the number of messages on the page
				var num_of_messages = document.getElementsByClassName('c-search_message__content').length;

				// scraping all messages on the page
				var i=0
				for (i=0; i<num_of_messages; i++) {
						var message = document.getElementsByClassName('c-search_message__content')[i].getElementsByClassName('c-message__message_blocks')[0]
						// if a particular message has any text content (and not just a picure or emoji), then add it to 'page_messages'
						if (message.children[0] !== undefined || typeof message.children[0] !== 'undefined') {
								page_messages += message.children[0].innerText + ' ';
						}
				}

				// appending 'all_messages' with the messages from the current search page
				all_messages += page_messages + ' ';
		} catch(error) {
				throw "The script needs adjustment. Some message elements weren't found."
		}
}

// a function for moving to the next page
function nextPage()	{
		try {
				document.getElementsByClassName('c-link--button c-search__pager__button_forward')[0].click()
		} catch(error) {
				throw "The script needs adjustment. The next page button wasn't found."
		}
}

// initiating the main function
pageScraping();
console.log('Scraping...');

// a function that initiates nextPage() every 5 seconds
// giving time to load the search page and scrape it before moving further
var t = 1;
function pageLoop() {
	  setTimeout(function() {
				console.log('Moving to the next page')
		    nextPage()
		    t++;
		    if (t < number_of_pages) {
		      	pageLoop();
		    }
	  }, 5000)
}

// initiating the function for page switching
pageLoop();

// a function that initiates pageScraping() every 5 seconds
// waiting for the page to be changed, as they change only once in 5 seconds (see previous function)
var z = 1;
function scrapingLoop() {
	  setTimeout(function() {
				console.log('Scraping...')
		    pageScraping()
		    z++;
		    if (z < number_of_pages) {
		      	scrapingLoop();
		    }
	  }, 5000)
}

// initiating the loop with the scraping function
// adding a 4 second delay to wait for the search page to load
// the delay needs to be between 0 the the delay that is defined for each search page, currently 5 seconds
setTimeout(scrapingLoop, 4000);

// a function for copying the scraped messages to the clipboard
function scrapingDone() {
		console.log('_______________')
		console.log('Done!');
		copy(all_messages);
		console.log("If the messages weren't copied to your clipboard, then type 'copy(all_messages)'");
		console.log('_______________')
}

// initiating the function for copying the search messages to the clipboard
setTimeout(scrapingDone, number_of_pages*5000 + 1000);
