from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FileField, IntegerField, FloatField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_wtf.file import FileField, FileAllowed

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'admin_login'

CONDITION_CHOICES = ['Seal Packed', 'Open Box', 'Super Mint', 'Mint', 'Very Good', 'Good']
INDIAN_BRANDS = ['Samsung', 'Xiaomi', 'Realme', 'Oppo', 'Vivo', 'OnePlus', 'Poco', 'Micromax', 'Lava', 'Karbonn', 'iQOO', 'Nothing']

# Specification options
RAM_OPTIONS = ['2GB', '3GB', '4GB', '6GB', '8GB', '12GB', '16GB']
ROM_OPTIONS = ['16GB', '32GB', '64GB', '128GB', '256GB', '512GB', '1TB']
NETWORK_OPTIONS = ['4G', '5G']
PROCESSOR_BRANDS = ['Snapdragon', 'MediaTek', 'Exynos', 'Bionic']
PROCESSOR_SERIES = {
    'Snapdragon': [
        '8 Gen 3', '8 Gen 2', '8 Gen 1', '8+ Gen 1',
        '888+', '888', '870', '865+', '865',
        '778G', '778G+', '780G', '782G',
        '695', '690', '680', '685',
        '662', '660', '665'
    ],
    'MediaTek': [
        'Dimensity 9300', 'Dimensity 9200+', 'Dimensity 9200',
        'Dimensity 8300', 'Dimensity 8200', 'Dimensity 8100',
        'Dimensity 1300', 'Dimensity 1200', 'Dimensity 1100',
        'Dimensity 7200', 'Dimensity 7100',
        'Helio G99', 'Helio G96', 'Helio G95', 'Helio G90T',
        'Helio G88', 'Helio G85', 'Helio G80'
    ],
    'Exynos': [
        '2400', '2300', '2200', '2100',
        '1380', '1330', '1280', '1080',
        '990', '980', '850'
    ],
    'Bionic': ['A17 Pro', 'A16', 'A15', 'A14', 'A13']
}
DISPLAY_TYPES = ['AMOLED', 'Super AMOLED', 'IPS LCD', 'OLED', 'Dynamic AMOLED', 'Dynamic AMOLED 2X']
BATTERY_SIZES = ['3000mAh', '4000mAh', '4500mAh', '5000mAh', '5500mAh', '6000mAh']
CHARGING_SPEEDS = ['15W', '18W', '25W', '33W', '45W', '65W', '80W', '100W', '120W', '150W']

class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

class Mobile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    condition = db.Column(db.String(50), nullable=False)
    original_price = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    specs = db.Column(db.Text, nullable=True)
    images = db.Column(db.String(500), nullable=False)
    brand = db.Column(db.String(50), nullable=False)
    model_year = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class Banner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(200), nullable=False)
    active = db.Column(db.Boolean, default=True)

class Broadcast(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    active = db.Column(db.Boolean, default=True)

class CommunityPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    pinned = db.Column(db.Boolean, default=False)

class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

def init_db():
    with app.app_context():
        db.create_all()
        # Create default admin account if it doesn't exist
        if not Admin.query.filter_by(username="rajib7677").first():
            admin = Admin(
                username="rajib7677",
                password_hash=generate_password_hash("rajib7677")
            )
            db.session.add(admin)
            db.session.commit()

def get_setting(key, default=''):
    setting = Settings.query.filter_by(key=key).first()
    return setting.value if setting else default

@app.context_processor
def inject_settings():
    return {
        'contact_phone': get_setting('contact_phone'),
        'contact_whatsapp': get_setting('contact_whatsapp'),
        'shop_name': get_setting('shop_name', 'Mobile Shop'),
        'shop_logo': get_setting('shop_logo')
    }

# Routes for user views
@app.route('/')
def home():
    # Get today's uploads
    today = datetime.utcnow().date()
    todays_mobiles = Mobile.query.filter(
        db.func.date(Mobile.created_at) == today
    ).order_by(Mobile.created_at.desc()).all()

    # Get all mobiles for the main list
    mobiles = Mobile.query.order_by(Mobile.created_at.desc()).all()
    banners = Banner.query.filter_by(active=True).all()
    return render_template('index.html', 
                         mobiles=mobiles, 
                         todays_mobiles=todays_mobiles,
                         banners=banners)

@app.route('/mobile/<int:id>')
def mobile_detail(id):
    mobile = Mobile.query.get_or_404(id)
    
    # Get related mobiles based on brand and price range
    price_range = 5000  # ±5000 price range
    related_mobiles = Mobile.query.filter(
        Mobile.id != id,  # Exclude current mobile
        Mobile.brand == mobile.brand,  # Same brand
        Mobile.price.between(mobile.price - price_range, mobile.price + price_range)  # Similar price range
    ).limit(5).all()
    
    # If we don't have enough related mobiles from the same brand, add some from other brands
    if len(related_mobiles) < 5:
        additional_mobiles = Mobile.query.filter(
            Mobile.id != id,
            Mobile.brand != mobile.brand,
            Mobile.price.between(mobile.price - price_range, mobile.price + price_range)
        ).limit(5 - len(related_mobiles)).all()
        related_mobiles.extend(additional_mobiles)
    
    return render_template('mobile_detail.html', mobile=mobile, related_mobiles=related_mobiles)

@app.route('/search')
def search():
    query = request.args.get('query', '')
    condition = request.args.get('condition', '')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    brand = request.args.get('brand', '')
    network = request.args.get('network', '')
    ram = request.args.get('ram', '')
    storage = request.args.get('storage', '')

    mobiles_query = Mobile.query

    if query:
        mobiles_query = mobiles_query.filter(
            db.or_(
                Mobile.name.ilike(f'%{query}%'),
                Mobile.brand.ilike(f'%{query}%'),
                Mobile.specs.ilike(f'%{query}%')
            )
        )
    if condition:
        mobiles_query = mobiles_query.filter(Mobile.condition == condition)
    if min_price is not None:
        mobiles_query = mobiles_query.filter(Mobile.price >= min_price)
    if max_price is not None:
        mobiles_query = mobiles_query.filter(Mobile.price <= max_price)
    if brand:
        mobiles_query = mobiles_query.filter(Mobile.brand == brand)
    if network:
        mobiles_query = mobiles_query.filter(Mobile.specs.ilike(f'%Network: {network}%'))
    if ram:
        mobiles_query = mobiles_query.filter(Mobile.specs.ilike(f'%RAM: {ram}%'))
    if storage:
        mobiles_query = mobiles_query.filter(Mobile.specs.ilike(f'%Storage: {storage}%'))

    mobiles = mobiles_query.order_by(Mobile.created_at.desc()).all()
    
    return render_template('search.html', 
                         mobiles=mobiles,
                         conditions=CONDITION_CHOICES,
                         brands=INDIAN_BRANDS,
                         ram_options=RAM_OPTIONS,
                         rom_options=ROM_OPTIONS)

@app.route('/broadcast')
def broadcast_list():
    broadcasts = Broadcast.query.filter_by(active=True).order_by(Broadcast.created_at.desc()).all()
    return render_template('broadcast.html', broadcasts=broadcasts)

@app.route('/community')
def community():
    pinned_posts = CommunityPost.query.filter_by(pinned=True).order_by(CommunityPost.created_at.desc()).all()
    regular_posts = CommunityPost.query.filter_by(pinned=False).order_by(CommunityPost.created_at.desc()).all()
    return render_template('community.html', pinned_posts=pinned_posts, regular_posts=regular_posts)

@app.route('/about')
def about():
    page = Page.query.filter_by(slug='about').first_or_404()
    return render_template('page.html', page=page)

@app.route('/contact')
def contact():
    page = Page.query.filter_by(slug='contact').first_or_404()
    return render_template('page.html', page=page)

# Admin routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        admin = Admin.query.filter_by(username=username).first()
        
        if admin and check_password_hash(admin.password_hash, password):
            login_user(admin)
            return redirect(url_for('admin_dashboard'))
        flash('Invalid credentials')
    return render_template('admin/login.html')

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    mobiles = Mobile.query.order_by(Mobile.created_at.desc()).all()
    banners = Banner.query.all()
    broadcasts = Broadcast.query.all()
    community_posts = CommunityPost.query.all()
    return render_template('admin/dashboard.html', 
                         mobiles=mobiles, 
                         banners=banners, 
                         broadcasts=broadcasts, 
                         community_posts=community_posts)

@app.route('/admin/mobile/add', methods=['GET', 'POST'])
@login_required
def add_mobile():
    if request.method == 'POST':
        name = request.form.get('name')
        condition = request.form.get('condition')
        original_price = float(request.form.get('original_price'))
        price = float(request.form.get('price'))
        brand = request.form.get('brand')
        model_year = request.form.get('model_year', type=int)
        
        # Get specifications
        specs_list = []
        
        # Required specifications
        ram = request.form.get('ram')
        if ram:
            specs_list.append(f"RAM: {ram}")
            
        rom = request.form.get('rom')
        if rom:
            specs_list.append(f"Storage: {rom}")
            
        network = request.form.get('network')
        if network:
            specs_list.append(f"Network: {network}")
            
        processor_brand = request.form.get('processor_brand')
        processor_model = request.form.get('processor_model')
        if processor_brand and processor_model:
            specs_list.append(f"Processor: {processor_brand} {processor_model}")
            
        display_type = request.form.get('display_type')
        if display_type:
            specs_list.append(f"Display: {display_type}")
            
        battery = request.form.get('battery')
        if battery:
            specs_list.append(f"Battery: {battery}")
            
        charging = request.form.get('charging')
        if charging:
            specs_list.append(f"Charging: {charging}")
        
        # Add any additional specifications from the text area
        additional_specs = request.form.get('additional_specs')
        if additional_specs:
            specs_list.extend(line.strip() for line in additional_specs.strip().split('\n') if line.strip())
        
        specs = '\n'.join(specs_list)
        
        images = []
        if 'images' in request.files:
            files = request.files.getlist('images')
            for file in files:
                if file and file.filename:
                    filename = f"{datetime.now().timestamp()}_{secure_filename(file.filename)}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    images.append(filename)
        
        mobile = Mobile(
            name=name,
            condition=condition,
            original_price=original_price,
            price=price,
            specs=specs,
            images=','.join(images) if images else '',
            brand=brand,
            model_year=model_year
        )
        db.session.add(mobile)
        db.session.commit()
        flash('Mobile added successfully!')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/add_mobile.html', 
                         conditions=CONDITION_CHOICES, 
                         brands=INDIAN_BRANDS,
                         ram_options=RAM_OPTIONS,
                         rom_options=ROM_OPTIONS,
                         network_options=NETWORK_OPTIONS,
                         processor_brands=PROCESSOR_BRANDS,
                         processor_series=PROCESSOR_SERIES,
                         display_types=DISPLAY_TYPES,
                         battery_sizes=BATTERY_SIZES,
                         charging_speeds=CHARGING_SPEEDS)

@app.route('/admin/banner/add', methods=['GET', 'POST'])
@login_required
def add_banner():
    if request.method == 'POST':
        if 'image' in request.files:
            file = request.files['image']
            if file:
                filename = f"{datetime.now().timestamp()}_{file.filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                banner = Banner(image=filename)
                db.session.add(banner)
                db.session.commit()
                flash('Banner added successfully!')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/add_banner.html')

@app.route('/admin/broadcast/add', methods=['GET', 'POST'])
@login_required
def add_broadcast():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        image = None
        if 'image' in request.files:
            file = request.files['image']
            if file:
                filename = f"broadcast_{datetime.now().timestamp()}_{file.filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image = filename
        
        broadcast = Broadcast(title=title, content=content, image=image)
        db.session.add(broadcast)
        db.session.commit()
        flash('Broadcast added successfully!')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/add_broadcast.html')

@app.route('/admin/community/add', methods=['GET', 'POST'])
@login_required
def add_community_post():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        pinned = 'pinned' in request.form
        image = None
        if 'image' in request.files:
            file = request.files['image']
            if file:
                filename = f"community_{datetime.now().timestamp()}_{file.filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image = filename
        
        post = CommunityPost(title=title, content=content, image=image, pinned=pinned)
        db.session.add(post)
        db.session.commit()
        flash('Community post added successfully!')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/add_community_post.html')

@app.route('/admin/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/admin/mobile/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_mobile(id):
    mobile = Mobile.query.get_or_404(id)
    if request.method == 'POST':
        mobile.name = request.form['name']
        mobile.brand = request.form['brand']
        mobile.condition = request.form['condition']
        mobile.original_price = float(request.form['original_price'])
        mobile.price = float(request.form['price'])
        mobile.specs = request.form['specs']
        mobile.model_year = int(request.form['model_year']) if request.form['model_year'] else None
        
        # Handle image upload
        if 'images' in request.files:
            images = []
            for file in request.files.getlist('images'):
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    images.append(filename)
            if images:
                mobile.images = ','.join(images)
        
        db.session.commit()
        flash('Mobile updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/edit_mobile.html', mobile=mobile)

@app.route('/admin/broadcast/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_broadcast(id):
    broadcast = Broadcast.query.get_or_404(id)
    if request.method == 'POST':
        broadcast.title = request.form['title']
        broadcast.content = request.form['content']
        broadcast.active = 'active' in request.form
        
        if 'image' in request.files and request.files['image'].filename:
            file = request.files['image']
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                broadcast.image = filename
        
        db.session.commit()
        flash('Broadcast updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/edit_broadcast.html', broadcast=broadcast)

@app.route('/admin/community/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_community_post(id):
    post = CommunityPost.query.get_or_404(id)
    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        post.pinned = 'pinned' in request.form
        
        if 'image' in request.files and request.files['image'].filename:
            file = request.files['image']
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                post.image = filename
        
        db.session.commit()
        flash('Community post updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/edit_community_post.html', post=post)

@app.route('/admin/mobile/delete/<int:id>')
@login_required
def delete_mobile(id):
    mobile = Mobile.query.get_or_404(id)
    try:
        # Delete associated images
        if mobile.images:
            for image in mobile.images.split(','):
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], image)
                if os.path.exists(image_path):
                    os.remove(image_path)
        
        db.session.delete(mobile)
        db.session.commit()
        flash('Mobile deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting mobile. Please try again.', 'error')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/broadcast/delete/<int:id>')
@login_required
def delete_broadcast(id):
    broadcast = Broadcast.query.get_or_404(id)
    try:
        # Delete associated image if exists
        if broadcast.image:
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], broadcast.image)
            if os.path.exists(image_path):
                os.remove(image_path)
        
        db.session.delete(broadcast)
        db.session.commit()
        flash('Broadcast deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting broadcast. Please try again.', 'error')
    
    return redirect(url_for('broadcast_list'))

@app.route('/admin/community/delete/<int:id>')
@login_required
def delete_community(id):
    post = CommunityPost.query.get_or_404(id)
    try:
        # Delete associated images
        if post.images:
            for image in post.images.split(','):
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], image)
                if os.path.exists(image_path):
                    os.remove(image_path)
        
        db.session.delete(post)
        db.session.commit()
        flash('Community post deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting community post. Please try again.', 'error')
    
    return redirect(url_for('community'))

@app.route('/admin/settings', methods=['GET', 'POST'])
@login_required
def admin_settings():
    if request.method == 'POST':
        # Handle logo upload
        if 'shop_logo' in request.files:
            file = request.files['shop_logo']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                setting = Settings.query.filter_by(key='shop_logo').first()
                if not setting:
                    setting = Settings(key='shop_logo')
                setting.value = filename
                db.session.add(setting)

        # Update other settings
        for key in ['contact_phone', 'contact_whatsapp', 'shop_name']:
            setting = Settings.query.filter_by(key=key).first()
            if not setting:
                setting = Settings(key=key)
            setting.value = request.form.get(key, '')
            db.session.add(setting)
        
        db.session.commit()
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('admin_settings'))
    
    settings = {s.key: s.value for s in Settings.query.all()}
    return render_template('admin/settings.html', settings=settings)

@app.route('/admin/pages')
@login_required
def admin_pages():
    pages = Page.query.all()
    return render_template('admin/pages.html', pages=pages)

@app.route('/admin/page/<string:slug>', methods=['GET', 'POST'])
@login_required
def edit_page(slug):
    page = Page.query.filter_by(slug=slug).first()
    if not page:
        page = Page(slug=slug)
        if slug == 'about':
            page.title = 'About Us'
        elif slug == 'contact':
            page.title = 'Contact Us'
    
    if request.method == 'POST':
        page.title = request.form['title']
        page.content = request.form['content']
        db.session.add(page)
        db.session.commit()
        flash('Page updated successfully!', 'success')
        return redirect(url_for('admin_pages'))
    
    return render_template('admin/edit_page.html', page=page)

@app.template_filter('nl2br')
def nl2br(value):
    """Convert newlines to <br> tags."""
    if not value:
        return ''
    return value.replace('\n', '<br>').replace('\r\n', '<br>')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    init_db()
    app.run(debug=True)
