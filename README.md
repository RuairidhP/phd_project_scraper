This is a webscraper which combines the use of the BeautifulSoup package, Playwright, and pandas (amongst others) to scrape the websites of 3 universities: University of Strathclyde, University of Glasgow, and the University of St. Andrews for open PhD positions in departments that I am considering applying to after my masters degree. Playwright was used for St. Andrews as they have a .js file which dynamically loads their positions. BeautifulSoup couldn't extract the html but Playwright was able. I also attempted to use Selenium to open the webpage, load the .js, and then scrape but I had no luck with this method.

The results are saved to an Excel document with each univeristy's positions in their own Excel sheet.

An example output is provided in the repository.
