import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin, urlparse
import time

class DynamicScraper:
    """
    A flexible web scraper that can extract data from any website
    """
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.soup = None
        self.scraped_data = {}
        
    def validate_url(self, url):
        """Check if the URL is valid"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def format_url(self, url):
        """Add protocol to URL if missing"""
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url
    
    def fetch_webpage(self, url):
        """Download the webpage"""
        try:
            print(f"\n🔄 Fetching webpage: {url}")
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            print("✅ Successfully downloaded webpage")
            return response.content
        except requests.exceptions.Timeout:
            print("❌ Error: Website took too long to respond (timeout)")
            return None
        except requests.exceptions.ConnectionError:
            print("❌ Error: Could not connect to website (check internet or URL)")
            return None
        except requests.exceptions.HTTPError as e:
            print(f"❌ Error: HTTP error occurred: {e}")
            return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def parse_html(self, content):
        """Parse HTML content with BeautifulSoup"""
        try:
            self.soup = BeautifulSoup(content, 'html.parser')
            print("✅ HTML parsed successfully")
            return True
        except Exception as e:
            print(f"❌ Error parsing HTML: {e}")
            return False
    
    def extract_basic_info(self):
        """Extract basic information like title, headings, paragraphs"""
        data = {}
        
        # Get page title
        title = self.soup.find('title')
        if title:
            data['page_title'] = title.text.strip()
        
        # Get meta description
        meta_desc = self.soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            data['page_description'] = meta_desc.get('content').strip()
        
        # Get all headings (h1, h2, h3)
        headings = {}
        for level in [1, 2, 3]:
            h_tags = self.soup.find_all(f'h{level}')
            if h_tags:
                headings[f'h{level}'] = [h.text.strip() for h in h_tags[:10]]  # Limit to 10
        if headings:
            data['headings'] = headings
        
        # Get all paragraphs (limit to first 5)
        paragraphs = self.soup.find_all('p')
        if paragraphs:
            data['paragraphs'] = [p.text.strip() for p in paragraphs[:5] if p.text.strip()]
        
        # Get all links
        links = self.soup.find_all('a')
        if links:
            data['links'] = [{'text': a.text.strip(), 'href': a.get('href', '#')} for a in links[:15] if a.text.strip()]
        
        # Get images
        images = self.soup.find_all('img')
        if images:
            data['images'] = [{'alt': img.get('alt', ''), 'src': img.get('src', '')} for img in images[:10]]
        
        return data
    
    def extract_tables(self):
        """Extract all tables from the webpage"""
        tables_data = []
        tables = self.soup.find_all('table')
        
        for idx, table in enumerate(tables[:5]):  # Limit to first 5 tables
            table_data = {'table_number': idx + 1, 'rows': []}
            rows = table.find_all('tr')
            
            for row in rows[:20]:  # Limit rows
                cols = row.find_all(['td', 'th'])
                row_data = [col.text.strip() for col in cols]
                if row_data:
                    table_data['rows'].append(row_data)
            
            if table_data['rows']:
                tables_data.append(table_data)
        
        return tables_data if tables_data else None
    
    def extract_lists(self):
        """Extract all lists (ul, ol) from the webpage"""
        lists_data = []
        
        # Get unordered lists
        ul_elements = self.soup.find_all('ul')
        for idx, ul in enumerate(ul_elements[:5]):
            items = ul.find_all('li')
            list_items = [item.text.strip() for item in items if item.text.strip()]
            if list_items:
                lists_data.append({
                    'type': 'unordered',
                    'number': idx + 1,
                    'items': list_items[:15]  # Limit to 15 items
                })
        
        # Get ordered lists
        ol_elements = self.soup.find_all('ol')
        for idx, ol in enumerate(ol_elements[:5]):
            items = ol.find_all('li')
            list_items = [item.text.strip() for item in items if item.text.strip()]
            if list_items:
                lists_data.append({
                    'type': 'ordered',
                    'number': idx + 1,
                    'items': list_items[:15]  # Limit to 15 items
                })
        
        return lists_data if lists_data else None
    
    def extract_forms(self):
        """Extract form information"""
        forms_data = []
        forms = self.soup.find_all('form')
        
        for idx, form in enumerate(forms[:5]):
            form_info = {
                'form_number': idx + 1,
                'action': form.get('action', ''),
                'method': form.get('method', 'GET'),
                'inputs': []
            }
            
            # Get all input fields
            inputs = form.find_all('input')
            for inp in inputs:
                form_info['inputs'].append({
                    'name': inp.get('name', ''),
                    'type': inp.get('type', ''),
                    'placeholder': inp.get('placeholder', '')
                })
            
            forms_data.append(form_info)
        
        return forms_data if forms_data else None
    
    def extract_all(self):
        """Extract all available data from the webpage"""
        if not self.soup:
            print("❌ HTML not parsed yet")
            return False
        
        print("\n🔍 Extracting information from webpage...")
        
        self.scraped_data['basic_info'] = self.extract_basic_info()
        
        tables = self.extract_tables()
        if tables:
            self.scraped_data['tables'] = tables
        
        lists = self.extract_lists()
        if lists:
            self.scraped_data['lists'] = lists
        
        forms = self.extract_forms()
        if forms:
            self.scraped_data['forms'] = forms
        
        print("✅ Extraction complete")
        return True
    
    def save_to_file(self, filename='scraped_data.json'):
        """Save scraped data to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.scraped_data, f, indent=2, ensure_ascii=False)
            print(f"💾 Data saved to '{filename}'")
            return True
        except Exception as e:
            print(f"❌ Error saving file: {e}")
            return False
    
    def display_summary(self):
        """Display a summary of scraped data"""
        print("\n" + "="*70)
        print("SCRAPING SUMMARY")
        print("="*70)
        
        if 'basic_info' in self.scraped_data:
            basic = self.scraped_data['basic_info']
            if 'page_title' in basic:
                print(f"📄 Page Title: {basic['page_title']}")
            if 'page_description' in basic:
                print(f"📝 Description: {basic['page_description'][:100]}...")
            if 'headings' in basic:
                total_headings = sum(len(v) for v in basic['headings'].values())
                print(f"📑 Headings Found: {total_headings}")
            if 'paragraphs' in basic:
                print(f"📖 Paragraphs Found: {len(basic['paragraphs'])}")
            if 'links' in basic:
                print(f"🔗 Links Found: {len(basic['links'])}")
            if 'images' in basic:
                print(f"🖼️  Images Found: {len(basic['images'])}")
        
        if 'tables' in self.scraped_data:
            print(f"📊 Tables Found: {len(self.scraped_data['tables'])}")
        
        if 'lists' in self.scraped_data:
            print(f"📋 Lists Found: {len(self.scraped_data['lists'])}")
        
        if 'forms' in self.scraped_data:
            print(f"📋 Forms Found: {len(self.scraped_data['forms'])}")
        
        print("="*70 + "\n")
    
    def scrape(self, url):
        """Main method to scrape a website"""
        # Validate and format URL
        url = self.format_url(url)
        if not self.validate_url(url):
            print("❌ Invalid URL format")
            return False
        
        # Fetch webpage
        content = self.fetch_webpage(url)
        if not content:
            return False
        
        # Parse HTML
        if not self.parse_html(content):
            return False
        
        # Extract data
        if not self.extract_all():
            return False
        
        # Display summary
        self.display_summary()
        
        return True


def main():
    """Main function to run the scraper"""
    print("\n" + "="*70)
    print("DYNAMIC WEB SCRAPER")
    print("="*70)
    print("This tool will scrape any website and extract all available data")
    print("="*70)
    
    scraper = DynamicScraper()
    
    while True:
        print("\nOptions:")
        print("1. Scrape a new website")
        print("2. Exit")
        
        choice = input("\nEnter your choice (1 or 2): ").strip()
        
        if choice == '2':
            print("\n👋 Thank you for using Dynamic Web Scraper. Goodbye!")
            break
        
        elif choice == '1':
            url = input("\nEnter the website URL (e.g., google.com or https://example.com): ").strip()
            
            if not url:
                print("❌ URL cannot be empty")
                continue
            
            # Create fresh scraper instance for each URL
            scraper = DynamicScraper()
            
            if scraper.scrape(url):
                # Ask if user wants to save data
                save_choice = input("\nDo you want to save the scraped data? (yes/no): ").strip().lower()
                if save_choice in ['yes', 'y']:
                    filename = input("Enter filename (default: scraped_data.json): ").strip()
                    if not filename:
                        filename = 'scraped_data.json'
                    scraper.save_to_file(filename)
                
                # Ask if user wants to see raw data
                view_choice = input("\nDo you want to view the complete data? (yes/no): ").strip().lower()
                if view_choice in ['yes', 'y']:
                    print("\n" + "="*70)
                    print("COMPLETE SCRAPED DATA (JSON)")
                    print("="*70)
                    print(json.dumps(scraper.scraped_data, indent=2, ensure_ascii=False))
            else:
                print("\n❌ Failed to scrape the website. Please try another URL.")
        
        else:
            print("❌ Invalid choice. Please enter 1 or 2.")


if __name__ == "__main__":
    main()
