from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import *
from django.core.files.storage import FileSystemStorage
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect
from django.db.models import Q
from django.utils import timezone

def landing(request):
    if request.method == "POST":
        email = request.POST.get("user-email")
        password = request.POST.get("user-password")
        user = authenticate(request, email=email, password=password)
        print(user)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials')
            return redirect('login-page')
    # GET request - show login form
    return render(request, 'auth/login.html')


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('user-registration')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already in use.')
            return redirect('user-registration')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, 'Account created successfully. You can now log in.')
        return redirect('login-page')
    return render(request , 'auth/signup.html')

def home(request):
    products_count = Product.objects.count()
    category_count = Category.objects.count()
    supplier_count = Supplier.objects.count()
    
    # Get low stock items (assuming minimum stock threshold is 10)
    low_stock_count = Product.objects.filter(stock__lte=10).count()
    
    context = {
        'products_count': products_count,
        'category_count': category_count,
        'supplier_count': supplier_count,
        'low_stock_count': low_stock_count,
    }
    
    return render(request, 'core/index.html', context)

def view_inventory(request):
    products = Product.objects.all()
    categories = Category.objects.filter(status=Category.CategoryStatus.ACTIVE)
    suppliers = Supplier.objects.all()
    context = {
        'products': products,
        'categories': categories,
        'suppliers': suppliers,
    }
    if request.method == 'POST':
        try:
            # Get form data
            name = request.POST.get('name')
            category_id = request.POST.get('category')
            stock = request.POST.get('stock')
            price = request.POST.get('price')
            supplier_id = request.POST.get('supplier')
            product_image = request.FILES.get('product_image')
            
            # Validate required fields
            if not all([name, category_id, stock, price, supplier_id]):
                messages.error(request, "Please fill all required fields")
                return redirect('inventory')
            
            # Create new product
            product = Product(
                name=name,
                category_id=category_id,
                stock=stock,
                price=price,
                supplier_id=supplier_id,
                product_image = product_image
            )
            product.save()
            
            supplier = Supplier.objects.get(id=supplier_id)
            supplier.supplied_item += int(stock)
            supplier.save()
            messages.success(request, "Product added successfully!")
            return redirect('inventory')
        except Exception as e:
            messages.error(request, f"Error adding product: {str(e)}")
            return redirect('inventory')
        
    return render(request, 'core/inventory.html', context)


def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    categories = Category.objects.all()
    suppliers = Supplier.objects.all()
    
    old_stock = product.stock  # Store old stock value before updating
    
    if request.method == 'POST':
        try:
            product.name = request.POST.get('name')
            product.category_id = request.POST.get('category')
            product.stock = int(request.POST.get('stock'))  # Convert to int
            product.price = request.POST.get('price')
            product.supplier_id = request.POST.get('supplier')
            
            if 'product_image' in request.FILES:
                # Delete old image if exists
                if product.product_image:
                    product.product_image.delete()
                # Save new image
                fs = FileSystemStorage()
                image = request.FILES['product_image']
                filename = fs.save(f'product-images/{image.name}', image)
                product.product_image = filename
            
            product.save()
            
            # Update supplied_item in Supplier table
            supplier = Supplier.objects.get(id=product.supplier_id)
            supplier.supplied_item = supplier.supplied_item - old_stock + product.stock
            supplier.save()
            
            messages.success(request, "Product updated successfully!")
            return redirect('inventory')
            
        except Exception as e:
            messages.error(request, f"Error updating product: {str(e)}")
    
    context = {
        'product': product,
        'categories': categories,
        'suppliers': suppliers,
    }
    return render(request, 'core/edit_product.html', context)

def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        if product.product_image:
            product.product_image.delete()
        product.delete()
        messages.success(request, "Product deleted successfully!")
    except Exception as e:
        messages.error(request, f"Error deleting product: {str(e)}")
    return redirect('inventory')

def product_history(request):
    # Get all products ordered by creation date (newest first)
    products = Product.objects.all().order_by('-created_at')
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(category__name__icontains=search_query) |
            Q(supplier__name__icontains=search_query)
        )
    
    context = {
        'products': products,
        'search_query': search_query,
    }
    return render(request, 'core/product_history.html', context)

def category(request):
    if request.method == 'POST':
        # Handle form submission for adding new category
        try:
            name = request.POST.get('name')
            status = request.POST.get('status', 'INACTIVE')
            category_image = request.FILES.get('category_image')
            fav_icon = request.POST.get('fav_icon', 'fa-solid fa-icons')
            
            if not name:
                messages.error(request, "Category name is required")
                return redirect('category')
            
            category = Category(
                name=name,
                status=status,
                category_fav_icon=fav_icon,
                image_name=name.lower().replace(' ', '-')
            )
            
            if category_image:
                fs = FileSystemStorage()
                filename = fs.save(f'category-images/{category_image.name}', category_image)
                category.category_image = filename
            
            category.save()
            messages.success(request, "Category added successfully!")
            return redirect('category')
            
        except Exception as e:
            messages.error(request, f"Error adding category: {str(e)}")
            return redirect('category')
    
    categories = Category.objects.all().order_by('name')
    return render(request, 'core/categories.html', {'categories': categories})

def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        try:
            category.name = request.POST.get('name')
            category.status = request.POST.get('status')
            category.category_fav_icon = request.POST.get('fav_icon', 'fa-solid fa-icons')
            
            if 'category_image' in request.FILES:
                if category.category_image:
                    category.category_image.delete()
                fs = FileSystemStorage()
                image = request.FILES['category_image']
                filename = fs.save(f'category-images/{image.name}', image)
                category.category_image = filename
            
            category.save()
            messages.success(request, "Category updated successfully!")
            return redirect('category')
        except Exception as e:
            messages.error(request, f"Error updating category: {str(e)}")
    
    return render(request, 'core/edit_category.html', {'category': category})

def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        try:
            if category.category_image:
                category.category_image.delete()
            category.delete()
            messages.success(request, "Category deleted successfully!")
        except Exception as e:
            messages.error(request, f"Error deleting category: {str(e)}")
    return redirect('category')

def suppliers(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            contact_person = request.POST.get('contact_person')
            phone_number = request.POST.get('phone_number')
            email = request.POST.get('email')
            photo = request.FILES.get('photo')
            
            if not all([name, contact_person, phone_number, email]):
                messages.error(request, "Please fill all required fields")
                return redirect('suppliers')
            
            supplier = Supplier(
                name=name,
                contact_person=contact_person,
                phone_number=phone_number,
                email=email,
                supplied_item=0,
                photo = photo 
            )
            supplier.save()
            messages.success(request, "Supplier added successfully!")
            return redirect('suppliers')
            
        except Exception as e:
            messages.error(request, f"Error adding supplier: {str(e)}")
            return redirect('suppliers')
    
    suppliers = Supplier.objects.all().order_by('name')
    return render(request, 'core/suppliers.html', {'suppliers': suppliers})

def edit_supplier(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)
    
    if request.method == 'POST':
        try:
            supplier.name = request.POST.get('name')
            supplier.contact_person = request.POST.get('contact_person')
            supplier.phone_number = request.POST.get('phone_number')
            supplier.email = request.POST.get('email')
            
            # Handle photo update
            if 'photo' in request.FILES:
                # Delete old photo if exists
                if supplier.photo:
                    supplier.photo.delete()
                # Save new photo
                fs = FileSystemStorage()
                photo = request.FILES['photo']
                filename = fs.save(f'supplier-photo/{photo.name}', photo)
                supplier.photo = filename
            
            supplier.save()
            messages.success(request, "Supplier updated successfully!")
            return redirect('suppliers')
            
        except Exception as e:
            messages.error(request, f"Error updating supplier: {str(e)}")
            return redirect('suppliers')
    
    # For GET request, show the edit form (you'll need to create this template)
    return render(request, 'core/edit_supplier.html', {'supplier': supplier})

def delete_supplier(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)
    
    if request.method == 'POST':
        try:
            # Delete the photo file if exists
            if supplier.photo:
                supplier.photo.delete()
            supplier.delete()
            messages.success(request, "Supplier deleted successfully!")
        except Exception as e:
            messages.error(request, f"Error deleting supplier: {str(e)}")
    return redirect('suppliers')


def logout_view(request):
    logout(request)
    return redirect('login')