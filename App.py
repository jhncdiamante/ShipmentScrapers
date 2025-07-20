from flask import Flask, request, jsonify, render_template_string
from flask_socketio import SocketIO, emit
import pandas as pd
import threading
import time
import uuid
import os
from datetime import datetime
import queue
from typing import Dict, List, Optional
import logging
from dataclasses import dataclass, asdict
import json

# Import your existing scraper modules
from Driver.NormalDriver import NormalDriver
from Search.SearchBar import SearchBar
from Button.Button import Button
from Search.SearchFeature import SearchFeature
from CookiesManager.NoCookieHandler import NoCookieHandler
from Website.TrackingWebsite import TrackingWebsite
from CMA.CMAContainerEvaluator import smart_container_scraper_factory
from CMA.CMAMilestoneScraper import CMAMilestoneScraper
from CMA.CMAShipmentScraper import CMAShipmentScraper
from selenium.webdriver.common.by import By
from Date.ScrapeTime import ScrapeTime
from Driver.MaskedUserAgentDriver import MaskedUserAgentDriver
from Driver.NormalDriver import NormalDriver
from Maersk.MaerskSearchBar import MaerskSearchBar
from Search.SearchFeature import SearchFeature
from CookiesManager.CookieHandler import CookieHandler
from Website.TrackingWebsite import TrackingWebsite
from Maersk.MaerskShipment import MaerskShipmentScraper
from Maersk.ContainerScraper import MaerskContainerScraper
from Maersk.MilestoneScraper import MaerskMilestoneScraper

from OneEcomm.OneShipmentScraper import OneShipmentScraper
from OneEcomm.OneContainerScraper import OneContainerScraper
from OneEcomm.OneMilestoneScraper import OneMilestoneScraper
from OneEcomm.OneWebsite import OneWebsite


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ScrapingJob:
    job_id: str
    scraper_type: str
    bl_numbers: List[str]
    status: str  # 'pending', 'running', 'completed', 'stopped', 'failed'
    total_items: int
    completed_items: int
    failed_items: List[Dict]
    results: List[Dict]
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

class ScrapingManager:
    def __init__(self):
        self.active_jobs: Dict[str, ScrapingJob] = {}
        self.scraping_threads: Dict[str, threading.Thread] = {}
        self.stop_flags: Dict[str, threading.Event] = {}
        
    def create_job(self, scraper_type: str, bl_numbers: List[str]) -> str:
        job_id = str(uuid.uuid4())
        job = ScrapingJob(
            job_id=job_id,
            scraper_type=scraper_type,
            bl_numbers=bl_numbers,
            status='pending',
            total_items=len(bl_numbers),
            completed_items=0,
            failed_items=[],
            results=[],
            created_at=datetime.now()
        )
        self.active_jobs[job_id] = job
        return job_id
    
    def start_job(self, job_id: str):
        if job_id not in self.active_jobs:
            raise ValueError(f"Job {job_id} not found")
        
        job = self.active_jobs[job_id]
        if job.status == 'running':
            raise ValueError(f"Job {job_id} is already running")
        
        job.status = 'running'
        job.started_at = datetime.now()
        
        stop_flag = threading.Event()
        self.stop_flags[job_id] = stop_flag
        
        thread = threading.Thread(
            target=self._run_scraping_job, 
            args=(job_id, stop_flag)
        )
        self.scraping_threads[job_id] = thread
        thread.start()
    
    def stop_job(self, job_id: str):
        if job_id in self.stop_flags:
            self.stop_flags[job_id].set()
            self.active_jobs[job_id].status = 'stopped'
    
    def get_job_status(self, job_id: str) -> Optional[Dict]:
        if job_id not in self.active_jobs:
            return None
        job = self.active_jobs[job_id]
        return asdict(job)
    
    def _run_scraping_job(self, job_id: str, stop_flag: threading.Event):
        job = self.active_jobs[job_id]
        scraper_instance = None
        
        try:
            logger.info(f"Starting scraping job {job_id} with {job.total_items} items")
            
            # Initialize scraper based on type
            if job.scraper_type == 'cma':
                scraper_instance = self._initialize_cma_scraper()
            elif job.scraper_type == 'maersk':
                scraper_instance = self._initialize_maersk_scraper()
            elif job.scraper_type == 'one':
                scraper_instance = self._initialize_one_ecomm_scraper()
            else:
                raise ValueError(f"Unsupported scraper type: {job.scraper_type}")
            
            # Process each BL number
            for i, bl_number in enumerate(job.bl_numbers):
                if stop_flag.is_set():
                    job.status = 'stopped'
                    break
                
                try:
                    logger.info(f"Processing BL: {bl_number} ({i+1}/{job.total_items})")
                    
                    # Emit progress update
                    socketio.emit('scraping_progress', {
                        'job_id': job_id,
                        'current_item': i + 1,
                        'total_items': job.total_items,
                        'progress': ((i + 1) / job.total_items) * 100,
                        'current_bl': bl_number,
                        'status': 'processing'
                    })
                    if job.scraper_type == 'one':
                        scraper_instance.open()
                    # Perform actual scraping
                    result = self._scrape_shipment(scraper_instance, bl_number)
                    
                    if result:
                        for res in result:
                            job.results.append(res)
                            logger.info(f"Successfully scraped BL: {bl_number}")
                    else:
                        raise ValueError
                    
                    job.completed_items = i + 1
                    
                    # Emit item completion
                    socketio.emit('item_completed', {
                        'job_id': job_id,
                        'bl_number': bl_number,
                        'success': result is not None,
                        'result': result,
                        'completed_items': job.completed_items,
                        'failed_items': len(job.failed_items)
                    })
                    
                    # Small delay to prevent overwhelming the website
                    time.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Error scraping BL {bl_number}: {str(e)}")
                    failed_item = {
                        'bl_number': bl_number,
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    }
                    job.failed_items.append(failed_item)
                    job.completed_items = i + 1
                    
                    socketio.emit('item_failed', {
                        'job_id': job_id,
                        'bl_number': bl_number,
                        'error': str(e),
                        'completed_items': job.completed_items,
                        'failed_items': len(job.failed_items)
                    })
            
            # Job completed
            if not stop_flag.is_set():
                job.status = 'completed'
                job.completed_at = datetime.now()
                
                socketio.emit('job_completed', {
                    'job_id': job_id,
                    'total_results': len(job.results),
                    'total_failed': len(job.failed_items),
                    'success_rate': (len(job.results) / job.total_items) * 100 if job.total_items > 0 else 0
                })
                
                logger.info(f"Job {job_id} completed. Results: {len(job.results)}, Failed: {len(job.failed_items)}")
        
        except Exception as e:
            logger.error(f"Job {job_id} failed with error: {str(e)}")
            job.status = 'failed'
            job.error_message = str(e)
            
            socketio.emit('job_failed', {
                'job_id': job_id,
                'error': str(e)
            })
        
        finally:
            # Cleanup
            if scraper_instance and hasattr(scraper_instance, 'driver'):
                try:
                    scraper_instance.close()
                except:
                    logger.warning("Failed to quit chromedriver.")
                    pass
            
            # Remove from active threads
            if job_id in self.scraping_threads:
                del self.scraping_threads[job_id]
            if job_id in self.stop_flags:
                del self.stop_flags[job_id]

    def _initialize_one_ecomm_scraper(self):
        ONE_ECOMM_TRACKING_URL = "https://ecomm.one-line.com/one-ecom/manage-shipment/cargo-tracking"
        
        one_driver_handle = MaskedUserAgentDriver()
        one_driver_handle.set_up_driver()

        one_driver = one_driver_handle.driver

        search_bar = SearchBar(one_driver, (By.ID, "searchName"))
        search_button = Button((By.ID, "btnSearch"), one_driver)
        search_feature = SearchFeature(search_bar=search_bar, search_button=search_button)
        cookie_handler = NoCookieHandler()
        scrape_time = ScrapeTime()
        one = OneWebsite(
            ONE_ECOMM_TRACKING_URL,
            one_driver,
            search_feature,
            cookie_handler,
            shipment_scraper_factory=OneShipmentScraper,
            container_scraper_factory=OneContainerScraper,
            milestone_scraper_factory=OneMilestoneScraper,
            scrape_time=scrape_time,
        )

        one.open()
        return one

    

    def _initialize_maersk_scraper(self):
                
        MAERSK_TRACKING_URL = "https://www.maersk.com/tracking/"
        maersk_driver_handle = NormalDriver()
        maersk_driver_handle.set_up_driver()
        maersk_driver = maersk_driver_handle.driver
        maersk_driver.maximize_window()

        search_bar = MaerskSearchBar(maersk_driver, (By.CSS_SELECTOR, "mc-input#track-input"))
        search_button = Button(
            (By.CLASS_NAME, "track__search__button"), maersk_driver
        )
        search_feature = SearchFeature(search_bar=search_bar, search_button=search_button)
        allow_button = Button(
            (By.CSS_SELECTOR, "button[data-test='coi-allow-all-button']"),
            maersk_driver
        )
        cookie_handler = CookieHandler(maersk_driver, allow_cookies_button=allow_button)
        scrape_time = ScrapeTime()

        maersk = TrackingWebsite(
            MAERSK_TRACKING_URL,
            maersk_driver,
            search_feature,
            cookie_handler,
            shipment_scraper_factory=MaerskShipmentScraper,
            container_scraper_factory=MaerskContainerScraper,
            milestone_scraper_factory=MaerskMilestoneScraper,
            scrape_time=scrape_time,
        )

        maersk.open()

        return maersk

    
    def _initialize_cma_scraper(self):
        """Initialize CMA scraper instance"""
        CMA_CGM_URL = "https://www.cma-cgm.com/ebusiness/tracking/search"
        
        driver_handle = NormalDriver()
        driver_handle.set_up_driver()
        driver = driver_handle.driver
        driver.maximize_window()
        
        search_bar = SearchBar(driver, (By.ID, "Reference"))
        search_button = Button((By.ID, "btnTracking"), driver)
        search_feature = SearchFeature(search_bar=search_bar, search_button=search_button)
        cookie_handler = NoCookieHandler()
        scrape_time = ScrapeTime()
        
        cma_scraper = TrackingWebsite(
            CMA_CGM_URL,
            driver=driver,
            search_feature=search_feature,
            cookie_handler=cookie_handler,
            shipment_scraper_factory=CMAShipmentScraper,
            container_scraper_factory=smart_container_scraper_factory,
            milestone_scraper_factory=CMAMilestoneScraper,
            scrape_time=scrape_time,
        )
        
        cma_scraper.open()
        return cma_scraper
    
    def _scrape_shipment(self, scraper, bl_number: str) -> Optional[Dict]:
        """Scrape a single shipment and return structured data"""
        try:
            # This would call your existing scraping logic
            # For now, returning a mock result structure
            scraped_shipments = scraper.track_shipment(bl_number)
            
            return scraped_shipments
        except Exception as e:
            logger.error(f"Failed to scrape {bl_number}: {str(e)}")
            return None

# Initialize the scraping manager
scraping_manager = ScrapingManager()

@app.route('/')
def index():
    # Return the HTML template - you can move this to a separate file
    return render_template_string(open('templates/dashboard.html').read())

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload and extract BL numbers"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Read the file
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file)
        else:
            return jsonify({'error': 'Unsupported file format'}), 400
        
        # Extract BL numbers from first column
        bl_numbers = df.iloc[:, 1].dropna().unique().tolist()
        bl_numbers = [str(bl).strip() for bl in bl_numbers if str(bl).strip()]
        
        return jsonify({
            'success': True,
            'bl_numbers': bl_numbers,
            'total_count': len(bl_numbers),
            'filename': file.filename
        })
    
    except Exception as e:
        logger.error(f"File upload error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/scraping/start', methods=['POST'])
def start_scraping():
    """Start a new scraping job"""
    try:
        data = request.get_json()
        scraper_type = data.get('scraper_type', 'cma')
        bl_numbers = data.get('bl_numbers', [])
        
        if not bl_numbers:
            return jsonify({'error': 'No BL numbers provided'}), 400
        
        job_id = scraping_manager.create_job(scraper_type, bl_numbers)
        scraping_manager.start_job(job_id)
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'message': f'Started scraping job for {len(bl_numbers)} items'
        })
    
    except Exception as e:
        logger.error(f"Start scraping error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/scraping/stop/<job_id>', methods=['POST'])
def stop_scraping(job_id):
    """Stop a running scraping job"""
    try:
        scraping_manager.stop_job(job_id)
        return jsonify({'success': True, 'message': 'Scraping stopped'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/scraping/status/<job_id>')
def get_job_status(job_id):
    """Get the status of a scraping job"""
    status = scraping_manager.get_job_status(job_id)
    if status:
        # Convert datetime objects to strings for JSON serialization
        if status['created_at']:
            status['created_at'] = status['created_at'].isoformat()
        if status['started_at']:
            status['started_at'] = status['started_at'].isoformat()
        if status['completed_at']:
            status['completed_at'] = status['completed_at'].isoformat()
        
        return jsonify(status)
    else:
        return jsonify({'error': 'Job not found'}), 404

@app.route('/api/scraping/results/<job_id>')
def get_job_results(job_id):
    """Get the results of a scraping job"""
    job = scraping_manager.active_jobs.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    return jsonify({
        'results': job.results,
        'failed_items': job.failed_items,
        'total_results': len(job.results),
        'total_failed': len(job.failed_items)
    })

@app.route('/api/scraping/export/<job_id>')
def export_results(job_id):
    """Export job results as CSV"""
    job = scraping_manager.active_jobs.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    if not job.results:
        return jsonify({'error': 'No results to export'}), 400
    print(job.results)
    # Convert results to DataFrame and return CSV
    df = pd.DataFrame(job.results)
    csv_data = df.to_csv(index=False)
    
    from flask import Response
    return Response(
        csv_data,
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=scraping_results_{job_id}.csv'}
    )

@socketio.on('connect')
def handle_connect():
    emit('connected', {'message': 'Connected to scraper dashboard'})

@socketio.on('disconnect')
def handle_disconnect():
    logger.info('Client disconnected')

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)