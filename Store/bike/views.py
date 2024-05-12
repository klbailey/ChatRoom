# Store>bike>views.py
from django.shortcuts import render, redirect
from .models import *
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import openai
import random

# openai.api_key = 'sk-proj-dVwz8zbLnnuJBcL0ScODT3BlbkFJySzzEmcDxesa15im0utL'
def chatbox(request):
    if request.method == 'POST':
        # Get user input from the POST request
        user_input = request.POST.get('user_input')

        # Use a list of prompts
        prompts = [
            "Hi there!",
            "How can I assist you today?",
            "What can I help you with?",
            "Tell me more about your inquiry.",
            "Greetings! What brings you here?"
        ]

        # Choose a random prompt
        prompt = random.choice(prompts)

        # Call the ChatGPT model to generate a response
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=prompt + " " + user_input,  # Concatenate the user input with the prompt
            max_tokens=50
        )

        # Return the chatbot's response as JSON
        return JsonResponse({'response': response['choices'][0]['text'].strip()})
    else:
        # Render the chatbox HTML template
        return render(request, 'chatbox.html')

def track_order(request):
    if request.method == 'POST':
        tracking_number = request.POST.get('tracking_number')
        order = Order.objects.filter(tracking_number=tracking_number).first()
        if order:
            return render(request, 'track_order.html', {'order': order})
        else:
            error_message = "Order not found. Please check your tracking number and try again."
            return render(request, 'track_order.html', {'error_message': error_message})
    else:
        return render(request, 'track_order.html')
    
    
def index(request):
    # Query some products to display on the homepage (e.g., first three products)
    products = Product.objects.all()[:3]
    return render(request, 'index.html', {'products': products})

def product_list(request):
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'product_detail.html', {'product': product})

def order_list(request):
    orders = Order.objects.all()
    return render(request, 'order_list.html', {'orders': orders})

def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, 'order_detail.html', {'order': order})

def road_bikes(request):
    # Retrieve any road bike product
    product = Product.objects.filter(category__name='Road Bike').first()

    # Check if a product is available
    if product:
        return render(request, 'road_bikes.html', {'product': product})
    else:
        # No road bikes available
        return render(request, 'road_bikes.html', {'product': None})

def mountain_bikes(request):
    mountain_bikes = Product.objects.filter(category__name='Mountain Bike')
    return render(request, 'mountain_bikes.html', {'mountain_bikes': mountain_bikes})

def e_bikes(request):
    e_bikes = Product.objects.filter(category__name='E-Bike')
    return render(request, 'e_bikes.html', {'e_bikes': e_bikes})

def favicon(request):
    return HttpResponse(status=204)


def add_to_cart(request, product_id):
    try:
        product = Product.objects.get(pk=product_id)
        cart = request.session.get('cart', {})
        cart[product_id] = {
            'name': product.name,
            'price': product.price,
            # Add any other product details you want to store in the cart
        }
        request.session['cart'] = cart
    except Product.DoesNotExist:
        # Handle case where product with given ID doesn't exist
        pass
    
    return redirect('view_cart')

def view_cart(request):
    cart = request.session.get('cart', {})
    total_price = sum(item['price'] for item in cart.values())
    return render(request, 'cart.html', {'cart': cart, 'total_price': total_price})

def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    if product_id in cart:
        del cart[product_id]
        request.session['cart'] = cart
    return redirect('view_cart')

def clear_cart(request):
    request.session.pop('cart', None)
    return redirect('view_cart')